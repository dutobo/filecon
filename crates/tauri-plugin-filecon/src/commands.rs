//! Tauri commands. Argument names are converted to camelCase by Tauri (`file_name` → `fileName`).

use crate::icons::{self, IconForPath, Style, Theme};

/// `plugin:filecon|resolve` – `{ fileName: string }` → icon name.
#[tauri::command]
pub(crate) fn resolve(file_name: String) -> String {
    icons::resolve(&file_name).to_string()
}

/// `plugin:filecon|icon` – `{ name: string, style?: Style, theme?: Theme }` → SVG document.
#[tauri::command]
pub(crate) fn icon(name: String, style: Option<Style>, theme: Option<Theme>) -> String {
    icons::icon(&name, style, theme).to_string()
}

/// `plugin:filecon|icon_for_path` – `{ path: string, style?: Style, theme?: Theme }` → `{ name, svg }`.
///
/// Async so that the file read does not block the main thread.
#[tauri::command]
pub(crate) async fn icon_for_path(
    path: String,
    style: Option<Style>,
    theme: Option<Theme>,
) -> IconForPath {
    icons::icon_for_path(&path, style, theme)
}
