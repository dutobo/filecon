//! Conformance tests: the component rendered with `dioxus-ssr` produces the pack SVG for every name, style and
//! theme (outer attributes compared as a set, inner markup compared exactly), plus accessibility, resolver and
//! fallback behaviour.

// Without any style feature no icon markup is embedded, so there is nothing to compare.
#![cfg(any(
    feature = "style-default",
    feature = "style-gray",
    feature = "style-solid",
    feature = "style-papered",
    feature = "style-papered-flat",
    feature = "style-papered-craft",
    feature = "style-scratch",
    feature = "style-chalk",
))]

use dioxus::prelude::*;
use filecon_dioxus::{icon_markup, names, FileIcon, Style, Theme};
use std::collections::BTreeMap;
use std::path::PathBuf;

/// A rendered or pack `<svg>` element split into its attributes and its inner markup.
#[derive(Debug, PartialEq)]
struct Svg {
    attributes: BTreeMap<String, String>,
    inner: String,
}

/// Parses `<svg a="b" …>inner</svg>` (attribute order and whitespace between attributes are irrelevant).
fn parse_svg(markup: &str) -> Svg {
    let markup = markup.trim();
    let rest = markup.strip_prefix("<svg").expect("starts with <svg");
    let end = rest.find('>').expect("start tag ends");
    let mut attributes = BTreeMap::new();
    let mut tag = &rest[..end];
    loop {
        tag = tag.trim_start();
        if tag.is_empty() {
            break;
        }
        let eq = tag.find('=').expect("attribute has a value");
        let key = tag[..eq].trim().to_string();
        let value_start = tag[eq + 1..].find('"').unwrap() + eq + 2;
        let value_end = value_start + tag[value_start..].find('"').unwrap();
        let previous = attributes.insert(key.clone(), tag[value_start..value_end].to_string());
        assert!(previous.is_none(), "duplicate attribute {key}");
        tag = &tag[value_end + 1..];
    }
    let inner = rest[end + 1..]
        .strip_suffix("</svg>")
        .expect("ends with </svg>")
        .to_string();
    Svg { attributes, inner }
}

/// Removes the pack's `<title>name</title>` (always the first child).
fn without_title(mut svg: Svg, name: &str) -> Svg {
    let title = format!("<title>{name}</title>");
    assert!(svg.inner.starts_with(&title), "{name}: pack title");
    svg.inner = svg.inner[title.len()..].to_string();
    svg
}

fn pack_file(style: Style, theme: Theme, name: &str) -> String {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    let pack = match style {
        Style::Default | Style::Gray | Style::Solid => root.join("icon-pack"),
        _ => root.join("icon-styles"),
    };
    let dir = match (style, theme) {
        (Style::Solid, _) => "solid",
        (Style::Default, Theme::Light) => "default/light",
        (Style::Default, Theme::Dark) => "default/dark",
        (Style::Gray, Theme::Light) => "gray/light",
        (Style::Gray, Theme::Dark) => "gray/dark",
        (Style::Papered, Theme::Light) => "papered/light",
        (Style::Papered, Theme::Dark) => "papered/dark",
        (Style::PaperedFlat, Theme::Light) => "papered-flat/light",
        (Style::PaperedFlat, Theme::Dark) => "papered-flat/dark",
        (Style::PaperedCraft, Theme::Light) => "papered-craft/light",
        (Style::PaperedCraft, Theme::Dark) => "papered-craft/dark",
        (Style::Scratch, Theme::Light) => "scratch/light",
        (Style::Scratch, Theme::Dark) => "scratch/dark",
        (Style::Chalk, Theme::Light) => "chalk/light",
        (Style::Chalk, Theme::Dark) => "chalk/dark",
    };
    std::fs::read_to_string(pack.join(dir).join(format!("{name}.svg"))).unwrap()
}

fn pack_available() -> bool {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../icon-pack/manifest.json")
        .exists()
}

fn render(element: Element) -> String {
    dioxus_ssr::render_element(element)
}

fn variants() -> Vec<(Style, Theme)> {
    let mut variants = Vec::new();
    if cfg!(feature = "style-default") {
        variants.extend([
            (Style::Default, Theme::Light),
            (Style::Default, Theme::Dark),
        ]);
    }
    if cfg!(feature = "style-gray") {
        variants.extend([(Style::Gray, Theme::Light), (Style::Gray, Theme::Dark)]);
    }
    if cfg!(feature = "style-solid") {
        variants.push((Style::Solid, Theme::Light));
    }
    let generated = [
        (cfg!(feature = "style-papered"), Style::Papered),
        (cfg!(feature = "style-papered-flat"), Style::PaperedFlat),
        (cfg!(feature = "style-papered-craft"), Style::PaperedCraft),
        (cfg!(feature = "style-scratch"), Style::Scratch),
        (cfg!(feature = "style-chalk"), Style::Chalk),
    ];
    for (enabled, style) in generated {
        if enabled {
            variants.extend([(style, Theme::Light), (style, Theme::Dark)]);
        }
    }
    variants
}

#[test]
fn renders_every_icon_like_the_pack() {
    if !pack_available() {
        eprintln!(
            "icon-pack not found next to the crate; skipping (only runs inside the repository)"
        );
        return;
    }
    assert_eq!(names().len(), 703);
    let mut compared = 0;
    for &(style, theme) in &variants() {
        for &name in names() {
            let rendered = parse_svg(&render(rsx! {
                FileIcon { name, style, theme }
            }));
            let mut expected = without_title(parse_svg(&pack_file(style, theme, name)), name);
            expected
                .attributes
                .insert("aria-hidden".into(), "true".into());
            assert_eq!(rendered, expected, "{name} {style:?} {theme:?}");
            assert_eq!(
                icon_markup(name, style, theme),
                Some(expected.inner.as_str())
            );
            compared += 1;
        }
    }
    assert_eq!(compared, 703 * variants().len());
}

#[test]
#[cfg(feature = "style-solid")]
fn solid_ignores_the_theme() {
    let light = render(rsx! { FileIcon { name: "pdf", style: Style::Solid, theme: Theme::Light } });
    let dark = render(rsx! { FileIcon { name: "pdf", style: Style::Solid, theme: Theme::Dark } });
    assert_eq!(light, dark);
}

#[test]
fn decorative_without_title() {
    let svg = parse_svg(&render(rsx! { FileIcon { name: "pdf" } }));
    assert_eq!(
        svg.attributes.get("aria-hidden").map(String::as_str),
        Some("true")
    );
    assert!(!svg.attributes.contains_key("role"));
    assert!(!svg.inner.contains("<title>"));
    // An empty title counts as no title (like the JavaScript packages).
    let svg = parse_svg(&render(rsx! { FileIcon { name: "pdf", title: "" } }));
    assert_eq!(
        svg.attributes.get("aria-hidden").map(String::as_str),
        Some("true")
    );
}

#[test]
fn labelled_with_title() {
    let svg = parse_svg(&render(
        rsx! { FileIcon { name: "pdf", title: "PDF document" } },
    ));
    assert_eq!(svg.attributes.get("role").map(String::as_str), Some("img"));
    assert!(!svg.attributes.contains_key("aria-hidden"));
    // Default style (or the first enabled one when features are reduced).
    let markup = variants()
        .into_iter()
        .find_map(|(style, theme)| icon_markup("pdf", style, theme))
        .unwrap();
    assert_eq!(svg.inner, format!("<title>PDF document</title>{markup}"));
}

#[test]
fn title_is_escaped() {
    let svg = parse_svg(&render(
        rsx! { FileIcon { name: "pdf", title: "<b>\"Q&A\"</b> 'x'" } },
    ));
    assert!(svg
        .inner
        .starts_with("<title>&lt;b&gt;&quot;Q&amp;A&quot;&lt;/b&gt; &#39;x&#39;</title><path"));
    assert_eq!(svg.inner.matches("<title>").count(), 1);
}

#[test]
fn size_and_class() {
    let svg = parse_svg(&render(
        rsx! { FileIcon { name: "pdf", size: 24, class: "icon big" } },
    ));
    assert_eq!(svg.attributes["width"], "24");
    assert_eq!(svg.attributes["height"], "24");
    assert_eq!(svg.attributes["viewBox"], "0 0 40 40");
    assert_eq!(svg.attributes["xmlns"], "http://www.w3.org/2000/svg");
    assert_eq!(svg.attributes["fill"], "none");
    assert_eq!(svg.attributes["class"], "icon big");
    let svg = parse_svg(&render(rsx! { FileIcon { name: "pdf" } }));
    assert_eq!(svg.attributes["width"], "40");
    assert!(!svg.attributes.contains_key("class"));
}

#[test]
fn file_is_resolved() {
    let by_file = render(rsx! { FileIcon { file: "docs/report.final.PDF" } });
    let by_name = render(rsx! { FileIcon { name: "pdf" } });
    assert_eq!(by_file, by_name);
    let dockerfile = render(rsx! { FileIcon { file: "src/Dockerfile" } });
    assert_eq!(dockerfile, render(rsx! { FileIcon { name: "dockerfile" } }));
    let makefile = render(rsx! { FileIcon { file: "C:\\work\\Makefile" } });
    assert_eq!(makefile, render(rsx! { FileIcon { name: "mk" } }));
    // `name` wins over `file`.
    let both = render(rsx! { FileIcon { name: "pdf", file: "a.zip" } });
    assert_eq!(both, by_name);
}

#[test]
fn unknown_names_render_the_empty_icon() {
    let empty = render(rsx! { FileIcon { name: "empty" } });
    assert_eq!(render(rsx! { FileIcon { name: "no-such-icon" } }), empty);
    assert_eq!(render(rsx! { FileIcon { file: "clip.unknown" } }), empty);
    assert_eq!(render(rsx! { FileIcon {} }), empty);
    assert_ne!(render(rsx! { FileIcon { name: "pdf" } }), empty);
}

#[test]
fn names_are_normalized() {
    let pdf = render(rsx! { FileIcon { name: "pdf" } });
    assert_eq!(render(rsx! { FileIcon { name: ".PDF" } }), pdf);
    assert_eq!(render(rsx! { FileIcon { name: " Pdf " } }), pdf);
    assert_eq!(render(rsx! { FileIcon { name: String::from("pdf") } }), pdf);
}

#[test]
fn icon_markup_for_unknown_names() {
    assert_eq!(
        icon_markup("no-such-icon", Style::Default, Theme::Light),
        None
    );
}
