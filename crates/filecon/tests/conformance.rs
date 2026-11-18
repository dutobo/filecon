//! Acceptance tests: the resolver passes `icon-pack/tests/resolve-cases.json`, and every embedded SVG is the
//! pack file for its name, style and theme.

use filecon::{names, resolve, svg, Style, Theme};
use std::path::PathBuf;

/// Minimal parser for the flat `[{ "key": "string", ... }]` structure of resolve-cases.json (no dependencies).
fn parse_cases(json: &str) -> Vec<(String, String, String)> {
    let mut cases = Vec::new();
    for object in json.split('{').skip(1) {
        let field = |key: &str| -> String {
            let start = object
                .find(&format!("\"{key}\""))
                .unwrap_or_else(|| panic!("missing {key}"));
            let rest = &object[start + key.len() + 2..];
            let open = rest.find('"').unwrap() + 1;
            let close = open + rest[open..].find('"').unwrap();
            rest[open..close].to_string()
        };
        cases.push((field("file"), field("content_hex"), field("expected")));
    }
    cases
}

fn hex(text: &str) -> Vec<u8> {
    (0..text.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&text[i..i + 2], 16).unwrap())
        .collect()
}

#[test]
fn resolver_passes_the_pack_cases() {
    let cases = parse_cases(include_str!("data/resolve-cases.json"));
    assert_eq!(cases.len(), 20);
    for (file, content, expected) in cases {
        assert_eq!(resolve(&file, Some(&hex(&content))), expected, "{file}");
    }
}

#[test]
fn resolver_without_content() {
    assert_eq!(resolve("report.final.pdf", None), "pdf");
    assert_eq!(resolve("src/app/Dockerfile", None), "dockerfile");
    assert_eq!(resolve("C:\\work\\Makefile", None), "mk");
    assert_eq!(resolve("Thumbs.db", None), "db");
    assert_eq!(resolve("noext", None), "empty");
    assert_eq!(resolve("", None), "empty");
}

#[test]
fn resolver_only_reads_the_first_kilobyte() {
    let mut head = vec![0u8; 4096];
    head[2000..2007].copy_from_slice(b"#import");
    assert_eq!(resolve("x.m", Some(&head)), "m");
    assert_eq!(resolve("x.img", Some(b"")), "img-disk");
}

#[test]
fn has_all_names() {
    assert_eq!(names().len(), 703);
    assert!(names().windows(2).all(|pair| pair[0] < pair[1]));
}

fn pack_file(style: Style, theme: Theme, name: &str) -> String {
    // In the repository compare with the icon pack itself; in a packaged crate with the shipped copies.
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let pack = manifest_dir.join("../../icon-pack");
    let in_repo = pack.join("manifest.json").exists();
    let base = match style {
        Style::Default | Style::Gray | Style::Solid if in_repo => pack,
        _ if in_repo => manifest_dir.join("../../icon-styles"),
        _ => manifest_dir.join("icons"),
    };
    let path = match (style, theme) {
        (Style::Solid, _) => base.join("solid"),
        (Style::Default, Theme::Light) => base.join("default/light"),
        (Style::Default, Theme::Dark) => base.join("default/dark"),
        (Style::Gray, Theme::Light) => base.join("gray/light"),
        (Style::Gray, Theme::Dark) => base.join("gray/dark"),
        (Style::Papered, Theme::Light) => base.join("papered/light"),
        (Style::Papered, Theme::Dark) => base.join("papered/dark"),
        (Style::PaperedFlat, Theme::Light) => base.join("papered-flat/light"),
        (Style::PaperedFlat, Theme::Dark) => base.join("papered-flat/dark"),
        (Style::PaperedCraft, Theme::Light) => base.join("papered-craft/light"),
        (Style::PaperedCraft, Theme::Dark) => base.join("papered-craft/dark"),
        (Style::Scratch, Theme::Light) => base.join("scratch/light"),
        (Style::Scratch, Theme::Dark) => base.join("scratch/dark"),
        (Style::Chalk, Theme::Light) => base.join("chalk/light"),
        (Style::Chalk, Theme::Dark) => base.join("chalk/dark"),
    };
    std::fs::read_to_string(path.join(format!("{name}.svg"))).unwrap()
}

#[test]
fn embedded_svgs_match_the_pack() {
    let styles: Vec<Style> = [
        cfg!(feature = "style-default").then_some(Style::Default),
        cfg!(feature = "style-gray").then_some(Style::Gray),
        cfg!(feature = "style-solid").then_some(Style::Solid),
        cfg!(feature = "style-papered").then_some(Style::Papered),
        cfg!(feature = "style-papered-flat").then_some(Style::PaperedFlat),
        cfg!(feature = "style-papered-craft").then_some(Style::PaperedCraft),
        cfg!(feature = "style-scratch").then_some(Style::Scratch),
        cfg!(feature = "style-chalk").then_some(Style::Chalk),
    ]
    .into_iter()
    .flatten()
    .collect();
    for name in names() {
        for &style in &styles {
            for theme in [Theme::Light, Theme::Dark] {
                let embedded = svg(name, style, theme).unwrap_or_else(|| panic!("{name}"));
                assert_eq!(
                    embedded,
                    pack_file(style, theme, name),
                    "{name} {style:?} {theme:?}"
                );
                assert!(embedded.contains(&format!("<title>{name}</title>")));
            }
        }
    }
}

#[test]
fn disabled_styles_and_unknown_names_return_none() {
    assert_eq!(svg("does-not-exist", Style::Solid, Theme::Light), None);
    assert_eq!(
        svg("pdf", Style::Default, Theme::Light).is_some(),
        cfg!(feature = "style-default")
    );
    assert_eq!(
        svg("pdf", Style::Gray, Theme::Dark).is_some(),
        cfg!(feature = "style-gray")
    );
    assert_eq!(
        svg("pdf", Style::Solid, Theme::Dark).is_some(),
        cfg!(feature = "style-solid")
    );
    assert_eq!(
        svg("pdf", Style::Papered, Theme::Dark).is_some(),
        cfg!(feature = "style-papered")
    );
    assert_eq!(
        svg("pdf", Style::PaperedFlat, Theme::Dark).is_some(),
        cfg!(feature = "style-papered-flat")
    );
    assert_eq!(
        svg("pdf", Style::PaperedCraft, Theme::Dark).is_some(),
        cfg!(feature = "style-papered-craft")
    );
    assert_eq!(
        svg("pdf", Style::Scratch, Theme::Dark).is_some(),
        cfg!(feature = "style-scratch")
    );
    assert_eq!(
        svg("pdf", Style::Chalk, Theme::Dark).is_some(),
        cfg!(feature = "style-chalk")
    );
}
