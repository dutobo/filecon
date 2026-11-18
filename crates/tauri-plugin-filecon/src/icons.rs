//! Command logic as plain functions (no Tauri types), so it can be used and tested without a running app.

use serde::{Deserialize, Serialize};
use std::io::Read;
use std::path::Path;

/// Number of bytes read from the start of a file for magic-byte detection.
pub const HEAD_LIMIT: u64 = 1024;

/// Visual style of an icon; serialized in kebab case: `"default"`, `"gray"`, `"solid"`, `"papered"`,
/// `"papered-flat"`, `"papered-craft"`, `"scratch"` or `"chalk"`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum Style {
    /// Outline with a colored label.
    #[default]
    Default,
    /// Filled gray page.
    Gray,
    /// Filled colored page with white label, identical in light and dark.
    Solid,
    /// Realistic paper sheet with a soft shadow and a shaded dog-ear.
    Papered,
    /// Flat warm paper sheet with fine grain and a subtle offset shadow.
    PaperedFlat,
    /// Cut paper: colored back sheet, tinted front sheet, label as a cut strip.
    PaperedCraft,
    /// Pencil sketch on a note, handwritten label.
    Scratch,
    /// Colored marker on a whiteboard (light) or chalk on a blackboard (dark), handwritten label.
    Chalk,
}

/// Color theme; serialized as `"light"` or `"dark"`. [`Style::Solid`] ignores it.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Theme {
    /// For light backgrounds.
    #[default]
    Light,
    /// For dark backgrounds.
    Dark,
}

impl From<Style> for filecon::Style {
    fn from(style: Style) -> Self {
        match style {
            Style::Default => filecon::Style::Default,
            Style::Gray => filecon::Style::Gray,
            Style::Solid => filecon::Style::Solid,
            Style::Papered => filecon::Style::Papered,
            Style::PaperedFlat => filecon::Style::PaperedFlat,
            Style::PaperedCraft => filecon::Style::PaperedCraft,
            Style::Scratch => filecon::Style::Scratch,
            Style::Chalk => filecon::Style::Chalk,
        }
    }
}

impl From<filecon::Style> for Style {
    fn from(style: filecon::Style) -> Self {
        match style {
            filecon::Style::Default => Style::Default,
            filecon::Style::Gray => Style::Gray,
            filecon::Style::Solid => Style::Solid,
            filecon::Style::Papered => Style::Papered,
            filecon::Style::PaperedFlat => Style::PaperedFlat,
            filecon::Style::PaperedCraft => Style::PaperedCraft,
            filecon::Style::Scratch => Style::Scratch,
            filecon::Style::Chalk => Style::Chalk,
        }
    }
}

impl From<Theme> for filecon::Theme {
    fn from(theme: Theme) -> Self {
        match theme {
            Theme::Light => filecon::Theme::Light,
            Theme::Dark => filecon::Theme::Dark,
        }
    }
}

impl From<filecon::Theme> for Theme {
    fn from(theme: filecon::Theme) -> Self {
        match theme {
            filecon::Theme::Light => Theme::Light,
            filecon::Theme::Dark => Theme::Dark,
        }
    }
}

/// Result of [`icon_for_path`]: the resolved icon name and its SVG document.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct IconForPath {
    /// Icon name, e.g. `"db-sqlite"`; `"empty"` if nothing matched.
    pub name: String,
    /// Complete SVG document of the icon.
    pub svg: String,
}

/// Normalizes an icon name or extension (`"PDF"`, `".pdf"`, `" pdf "`) and falls back to `"empty"`.
pub fn to_icon_name(name_or_extension: &str) -> &'static str {
    let normalized = name_or_extension
        .trim()
        .trim_start_matches('.')
        .to_lowercase();
    let names = filecon::names();
    names
        .binary_search(&normalized.as_str())
        .map(|index| names[index])
        .unwrap_or("empty")
}

/// Icon name for a file name or path, using only the name and the extension (no file access).
pub fn resolve(file_name: &str) -> &'static str {
    filecon::resolve(file_name, None)
}

/// SVG document for an icon name or extension. Unknown names give the `empty` icon.
///
/// If the requested style's feature is disabled, the first enabled style is used. Returns an empty string only if
/// all style features are disabled.
pub fn icon(name: &str, style: Option<Style>, theme: Option<Theme>) -> &'static str {
    let name = to_icon_name(name);
    let theme = theme.unwrap_or_default().into();
    std::iter::once(style.unwrap_or_default().into())
        .chain(filecon::Style::ALL)
        .find_map(|style| filecon::svg(name, style, theme))
        .unwrap_or("")
}

/// Reads at most [`HEAD_LIMIT`] bytes from the start of a file.
pub fn read_head(path: &Path) -> std::io::Result<Vec<u8>> {
    let mut head = Vec::with_capacity(HEAD_LIMIT as usize);
    std::fs::File::open(path)?
        .take(HEAD_LIMIT)
        .read_to_end(&mut head)?;
    Ok(head)
}

/// Icon name for a file on disk: file name → magic bytes (first 1 KB) → extension → `empty`.
///
/// If the file cannot be read (missing, no permission, a directory, an Android `content://` URI, …) only the
/// name is used; this never fails.
pub fn resolve_path(path: &str) -> &'static str {
    match read_head(Path::new(path)) {
        Ok(head) => filecon::resolve(path, Some(&head)),
        Err(_) => filecon::resolve(path, None),
    }
}

/// Icon name and SVG document for a file on disk; see [`resolve_path`].
pub fn icon_for_path(path: &str, style: Option<Style>, theme: Option<Theme>) -> IconForPath {
    let name = resolve_path(path);
    IconForPath {
        name: name.to_string(),
        svg: icon(name, style, theme).to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    /// A file in a fresh temporary directory, removed on drop.
    struct TempFile(PathBuf);

    impl TempFile {
        fn new(file_name: &str, content: &[u8]) -> Self {
            let dir = std::env::temp_dir().join(format!(
                "tauri-plugin-filecon-{}-{}",
                std::process::id(),
                file_name.replace(['.', '/'], "_")
            ));
            std::fs::create_dir_all(&dir).unwrap();
            let path = dir.join(file_name);
            std::fs::write(&path, content).unwrap();
            TempFile(path)
        }

        fn path(&self) -> &str {
            self.0.to_str().unwrap()
        }
    }

    impl Drop for TempFile {
        fn drop(&mut self) {
            if let Some(dir) = self.0.parent() {
                let _ = std::fs::remove_dir_all(dir);
            }
        }
    }

    fn enabled(style: filecon::Style) -> bool {
        filecon::svg("pdf", style, filecon::Theme::Light).is_some()
    }

    #[test]
    fn resolve_uses_name_and_extension() {
        assert_eq!(resolve("report.final.pdf"), "pdf");
        assert_eq!(resolve("src/app/Dockerfile"), "dockerfile");
        assert_eq!(resolve("C:\\work\\Makefile"), "mk");
        assert_eq!(resolve("clip.unknown"), "empty");
        assert_eq!(resolve(""), "empty");
    }

    #[test]
    fn icon_returns_the_svg_document() {
        if !enabled(filecon::Style::Default) || !enabled(filecon::Style::Gray) {
            return;
        }
        assert_eq!(
            icon("pdf", None, None),
            filecon::svg("pdf", filecon::Style::Default, filecon::Theme::Light).unwrap()
        );
        assert_eq!(
            icon("pdf", Some(Style::Gray), Some(Theme::Dark)),
            filecon::svg("pdf", filecon::Style::Gray, filecon::Theme::Dark).unwrap()
        );
        assert!(icon("pdf", None, None).starts_with("<svg"));
    }

    #[test]
    #[cfg(any(
        feature = "style-default",
        feature = "style-gray",
        feature = "style-solid",
        feature = "style-papered",
        feature = "style-papered-flat",
        feature = "style-papered-craft",
        feature = "style-scratch",
        feature = "style-chalk",
    ))]
    fn icon_normalizes_names_and_falls_back_to_empty() {
        assert_eq!(icon(".PDF", None, None), icon("pdf", None, None));
        assert_eq!(icon(" Pdf ", None, None), icon("pdf", None, None));
        assert_eq!(icon("no-such-icon", None, None), icon("empty", None, None));
        assert_ne!(icon("pdf", None, None), icon("empty", None, None));
        assert!(icon("no-such-icon", None, None).contains("<title>empty</title>"));
    }

    #[test]
    fn solid_ignores_the_theme() {
        if !enabled(filecon::Style::Solid) {
            return;
        }
        assert_eq!(
            icon("zip", Some(Style::Solid), Some(Theme::Light)),
            icon("zip", Some(Style::Solid), Some(Theme::Dark))
        );
    }

    #[test]
    fn icon_for_path_detects_magic_bytes() {
        let file = TempFile::new("app.db", b"SQLite format 3\0rest of the header");
        let result = icon_for_path(file.path(), Some(Style::Solid), None);
        assert_eq!(result.name, "db-sqlite");
        assert_eq!(result.svg, icon("db-sqlite", Some(Style::Solid), None));
    }

    #[test]
    fn icon_for_path_falls_back_to_the_name() {
        let missing = std::env::temp_dir().join("tauri-plugin-filecon-missing/app.db");
        let result = icon_for_path(missing.to_str().unwrap(), None, Some(Theme::Dark));
        assert_eq!(result.name, "db");
        assert_eq!(result.svg, icon("db", None, Some(Theme::Dark)));
        // Android content URIs are no file system paths.
        assert_eq!(
            resolve_path("content://com.android.providers/document/report.pdf"),
            "pdf"
        );
        // A directory cannot be read as a file either.
        let dir = std::env::temp_dir().join(format!(
            "tauri-plugin-filecon-dir-{}/notes.pdf",
            std::process::id()
        ));
        std::fs::create_dir_all(&dir).unwrap();
        assert_eq!(resolve_path(dir.to_str().unwrap()), "pdf");
        let _ = std::fs::remove_dir_all(dir.parent().unwrap());
    }

    #[test]
    fn icon_for_path_reads_only_the_first_kilobyte() {
        let mut content = vec![b' '; 4096];
        content[2000..2007].copy_from_slice(b"#import");
        let file = TempFile::new("late.m", &content);
        assert_eq!(read_head(Path::new(file.path())).unwrap().len(), 1024);
        assert_eq!(resolve_path(file.path()), "m");

        content[10..17].copy_from_slice(b"#import");
        let file = TempFile::new("early.m", &content);
        assert_eq!(resolve_path(file.path()), "m-objc");
    }

    #[test]
    fn style_and_theme_use_lowercase_json() {
        for (json, style) in [
            ("\"default\"", Style::Default),
            ("\"gray\"", Style::Gray),
            ("\"solid\"", Style::Solid),
            ("\"papered\"", Style::Papered),
            ("\"papered-flat\"", Style::PaperedFlat),
            ("\"papered-craft\"", Style::PaperedCraft),
            ("\"scratch\"", Style::Scratch),
            ("\"chalk\"", Style::Chalk),
        ] {
            assert_eq!(serde_json::from_str::<Style>(json).unwrap(), style);
            assert_eq!(serde_json::to_string(&style).unwrap(), json);
        }
        for (json, theme) in [("\"light\"", Theme::Light), ("\"dark\"", Theme::Dark)] {
            assert_eq!(serde_json::from_str::<Theme>(json).unwrap(), theme);
            assert_eq!(serde_json::to_string(&theme).unwrap(), json);
        }
        assert!(serde_json::from_str::<Style>("\"Default\"").is_err());
        assert!(serde_json::from_str::<Theme>("\"auto\"").is_err());
    }

    #[test]
    fn icon_for_path_serializes_name_and_svg() {
        let value = serde_json::to_value(IconForPath {
            name: "pdf".into(),
            svg: "<svg/>".into(),
        })
        .unwrap();
        assert_eq!(value, serde_json::json!({ "name": "pdf", "svg": "<svg/>" }));
    }

    #[test]
    fn enum_conversions_round_trip() {
        for style in [
            Style::Default,
            Style::Gray,
            Style::Solid,
            Style::Papered,
            Style::PaperedFlat,
            Style::PaperedCraft,
            Style::Scratch,
            Style::Chalk,
        ] {
            assert_eq!(Style::from(filecon::Style::from(style)), style);
        }
        for theme in [Theme::Light, Theme::Dark] {
            assert_eq!(Theme::from(filecon::Theme::from(theme)), theme);
        }
    }
}
