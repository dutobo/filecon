//! # filecon
//!
//! File-type icons for 703 formats in three styles, embedded as SVG strings, plus the Filecon file-type resolver
//! (file name → magic bytes → extension → `empty`).
//!
//! ```
//! use filecon::{resolve, svg, Style, Theme};
//!
//! let name = resolve("report.final.pdf", None);
//! assert_eq!(name, "pdf");
//! if let Some(icon) = svg(name, Style::Default, Theme::Light) {
//!     assert!(icon.starts_with("<svg"));
//! }
//!
//! // Magic bytes win over the extension:
//! assert_eq!(resolve("app.db", Some(b"SQLite format 3\0")), "db-sqlite");
//! ```
//!
//! ## Features
//!
//! `style-default`, `style-gray` and `style-solid` (all enabled by default) control which SVGs are embedded.
//! [`svg`] returns `None` for a style whose feature is disabled.
//!
//! The SVGs are the unmodified files of the Filecon icon pack (40×40, `viewBox="0 0 40 40"`, including a
//! `<title>` with the icon name).

#![forbid(unsafe_code)]
#![warn(missing_docs)]

#[rustfmt::skip]
mod generated;
mod resolve;

pub use resolve::resolve;

/// Visual style of an icon.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Style {
    /// Outline with a colored label (feature `style-default`).
    Default,
    /// Filled gray page (feature `style-gray`).
    Gray,
    /// Filled colored page with white label, identical in light and dark (feature `style-solid`).
    Solid,
}

/// Color theme. [`Style::Solid`] looks the same in both themes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub enum Theme {
    /// For light backgrounds.
    #[default]
    Light,
    /// For dark backgrounds.
    Dark,
}

/// All icon names, sorted.
pub fn names() -> &'static [&'static str] {
    &generated::NAMES
}

/// Index of an icon name in [`names`].
pub(crate) fn index_of(name: &str) -> Option<usize> {
    generated::NAMES.binary_search(&name).ok()
}

/// `true` if `name` is one of the icon names.
pub fn is_icon_name(name: &str) -> bool {
    index_of(name).is_some()
}

/// The SVG document for an icon, or `None` if the name is unknown or the style's feature is disabled.
pub fn svg(name: &str, style: Style, theme: Theme) -> Option<&'static str> {
    let index = index_of(name)?;
    let table: Option<&'static [&'static str]> = match (style, theme) {
        #[cfg(feature = "style-default")]
        (Style::Default, Theme::Light) => Some(&generated::DEFAULT_LIGHT),
        #[cfg(feature = "style-default")]
        (Style::Default, Theme::Dark) => Some(&generated::DEFAULT_DARK),
        #[cfg(feature = "style-gray")]
        (Style::Gray, Theme::Light) => Some(&generated::GRAY_LIGHT),
        #[cfg(feature = "style-gray")]
        (Style::Gray, Theme::Dark) => Some(&generated::GRAY_DARK),
        #[cfg(feature = "style-solid")]
        (Style::Solid, _) => Some(&generated::SOLID),
        #[allow(unreachable_patterns)]
        _ => None,
    };
    table.map(|svgs| svgs[index])
}
