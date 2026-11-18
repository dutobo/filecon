//! # filecon-dioxus
//!
//! [Dioxus](https://dioxuslabs.com) component for the [Filecon](https://filecon.dev) file-type icons: 703 formats
//! in three styles, rendered as inline SVG. Works with every Dioxus renderer (web, desktop, mobile, SSR/fullstack)
//! because the component only emits an `<svg>` element.
//!
//! ```
//! use dioxus::prelude::*;
//! use filecon_dioxus::{FileIcon, Style, Theme};
//!
//! #[component]
//! fn Row(file_name: String) -> Element {
//!     rsx! {
//!         // Icon by file name (resolved with `filecon::resolve`):
//!         FileIcon { file: file_name.clone(), size: 24 }
//!         // Icon by name, with a different style/theme and an accessible title:
//!         FileIcon { name: "pdf", style: Style::Solid, theme: Theme::Dark, title: "PDF document" }
//!     }
//! }
//! ```
//!
//! ## Features
//!
//! `style-default`, `style-gray` and `style-solid` (all enabled by default) are forwarded to the
//! [`filecon`] crate and control which SVGs are embedded. If the requested style is disabled, the first enabled
//! style is used instead.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use dioxus::prelude::*;

pub use filecon::{is_icon_name, names, resolve, Style, Theme};

/// `xmlns` of the rendered `<svg>` element.
pub const SVG_NAMESPACE: &str = "http://www.w3.org/2000/svg";
/// `viewBox` of every icon.
pub const VIEW_BOX: &str = "0 0 40 40";
/// Default width and height in pixels.
pub const DEFAULT_SIZE: u32 = 40;

/// Normalizes an icon name or extension (`"PDF"`, `".pdf"`, `" pdf "`) and falls back to `"empty"`.
///
/// ```
/// assert_eq!(filecon_dioxus::to_icon_name(".PDF"), "pdf");
/// assert_eq!(filecon_dioxus::to_icon_name("no-such-icon"), "empty");
/// ```
pub fn to_icon_name(name_or_extension: &str) -> &'static str {
    let normalized = name_or_extension
        .trim()
        .trim_start_matches('.')
        .to_lowercase();
    names()
        .binary_search(&normalized.as_str())
        .map(|index| names()[index])
        .unwrap_or("empty")
}

/// Removes the outer `<svg …>` tag, the `<title>` and the closing `</svg>` from a pack SVG.
fn inner(svg: &'static str) -> &'static str {
    let body = svg.find('>').map_or(svg, |end| &svg[end + 1..]);
    let body = match body.strip_prefix("<title>") {
        Some(rest) => rest
            .find("</title>")
            .map_or(rest, |end| &rest[end + "</title>".len()..]),
        None => body,
    };
    let body = body.trim_end();
    body.strip_suffix("</svg>").unwrap_or(body)
}

/// Inner SVG markup (everything between `<svg>` and `</svg>`, without the pack's `<title>`) of an icon.
///
/// Returns `None` if `name` is not an icon name or the style's feature is disabled. [`Style::Solid`] ignores the
/// theme.
///
/// ```
/// use filecon_dioxus::{icon_markup, Style, Theme};
///
/// if let Some(markup) = icon_markup("pdf", Style::Default, Theme::Light) {
///     assert!(markup.starts_with("<path"));
///     assert!(!markup.contains("<title>"));
/// }
/// assert_eq!(icon_markup("no-such-icon", Style::Solid, Theme::Light), None);
/// ```
pub fn icon_markup(name: &str, style: Style, theme: Theme) -> Option<&'static str> {
    filecon::svg(name, style, theme).map(inner)
}

/// Inner markup for `name`, falling back to the first enabled style if `style` is disabled. Empty if no style is
/// enabled at all.
fn markup_with_fallback(name: &str, style: Style, theme: Theme) -> &'static str {
    [style, Style::Default, Style::Gray, Style::Solid]
        .into_iter()
        .find_map(|candidate| icon_markup(name, candidate, theme))
        .unwrap_or("")
}

/// Escapes text for XML/HTML text and attribute content.
pub fn escape_xml(value: &str) -> String {
    let mut escaped = String::with_capacity(value.len());
    for character in value.chars() {
        match character {
            '&' => escaped.push_str("&amp;"),
            '<' => escaped.push_str("&lt;"),
            '>' => escaped.push_str("&gt;"),
            '"' => escaped.push_str("&quot;"),
            '\'' => escaped.push_str("&#39;"),
            other => escaped.push(other),
        }
    }
    escaped
}

/// Children of the `<svg>` element as markup: an optional escaped `<title>` followed by the icon markup.
fn content(icon: &str, style: Style, theme: Theme, title: Option<&str>) -> String {
    let markup = markup_with_fallback(icon, style, theme);
    match title {
        Some(title) => format!("<title>{}</title>{markup}", escape_xml(title)),
        None => markup.to_string(),
    }
}

/// A Filecon file-type icon as inline SVG.
///
/// Renders
/// `<svg xmlns="http://www.w3.org/2000/svg" width=… height=… viewBox="0 0 40 40" fill="none">…</svg>`.
/// Without `title` the icon is decorative (`aria-hidden="true"`); with `title` it gets `role="img"` and an escaped
/// `<title>` as its first child.
///
/// The icon is picked from `name` if given, otherwise from `file` via [`resolve`]. Unknown names (and neither prop)
/// render the `empty` icon.
#[component]
pub fn FileIcon(
    /// Icon name or extension, e.g. `"pdf"`, `"db-sqlite"`, `".PDF"`. Takes precedence over `file`.
    #[props(into)]
    name: Option<String>,
    /// File name or path; the icon is picked by [`resolve`] (name and extension only, no file access).
    #[props(into)]
    file: Option<String>,
    /// Visual style, [`Style::Default`] by default.
    #[props(default = Style::Default)]
    style: Style,
    /// Color theme, [`Theme::Light`] by default. Ignored by [`Style::Solid`].
    #[props(default)]
    theme: Theme,
    /// Width and height in pixels, 40 by default.
    #[props(default = DEFAULT_SIZE)]
    size: u32,
    /// Accessible title. Makes the icon `role="img"` instead of `aria-hidden="true"`.
    #[props(into)]
    title: Option<String>,
    /// CSS class of the `<svg>` element.
    #[props(into)]
    class: Option<String>,
) -> Element {
    let icon = match (&name, &file) {
        (Some(name), _) => to_icon_name(name),
        (None, Some(file)) => resolve(file, None),
        (None, None) => "empty",
    };
    let title = title.as_deref().filter(|title| !title.is_empty());
    let inner_html = content(icon, style, theme, title);
    let labelled = title.is_some();
    rsx! {
        svg {
            "xmlns": SVG_NAMESPACE,
            width: "{size}",
            height: "{size}",
            view_box: VIEW_BOX,
            fill: "none",
            role: if labelled { "img" },
            "aria-hidden": if !labelled { "true" },
            class,
            dangerous_inner_html: inner_html,
        }
    }
}
