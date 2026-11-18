//! # tauri-plugin-filecon
//!
//! [Tauri 2](https://v2.tauri.app) plugin for the [Filecon](https://filecon.dev) file-type icons: 703 formats in
//! three styles, resolved by file name, extension or magic bytes. Pure Rust (built on the
//! [`filecon`](https://docs.rs/filecon) crate), so it runs on Windows, macOS, Linux, iOS and Android without
//! native code.
//!
//! ```rust,ignore
//! // src-tauri/src/lib.rs
//! tauri::Builder::default()
//!     .plugin(tauri_plugin_filecon::init())
//!     .run(tauri::generate_context!())
//!     .expect("error while running tauri application");
//! ```
//!
//! The JavaScript binding is the npm package `@filecon/tauri`.
//!
//! ## Commands
//!
//! | Command | Arguments (JSON) | Returns |
//! |---|---|---|
//! | `plugin:filecon\|resolve` | `{ fileName: string }` | icon name (`string`) |
//! | `plugin:filecon\|icon` | `{ name: string, style?: Style, theme?: Theme }` | SVG document (`string`) |
//! | `plugin:filecon\|icon_for_path` | `{ path: string, style?: Style, theme?: Theme }` | `{ name: string, svg: string }` |
//!
//! `Style` is `"default" | "gray" | "solid"`, `Theme` is `"light" | "dark"`.
//!
//! ## Permissions
//!
//! `filecon:default` allows `resolve` and `icon`. `icon_for_path` reads the first 1 KB of a file and must be enabled
//! explicitly with `filecon:allow-icon-for-path`.
//!
//! ## Rust API
//!
//! The command logic is available as plain functions in [`icons`] for use from the app's own Rust code.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use tauri::{
    plugin::{Builder, TauriPlugin},
    Runtime,
};

mod commands;
pub mod icons;

pub use icons::{IconForPath, Style, Theme};

/// Name of the plugin (prefix of its commands and permissions).
pub const PLUGIN_NAME: &str = "filecon";

/// Creates the plugin. Register it with `tauri::Builder::default().plugin(tauri_plugin_filecon::init())`.
pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new(PLUGIN_NAME)
        .invoke_handler(tauri::generate_handler![
            commands::resolve,
            commands::icon,
            commands::icon_for_path
        ])
        .build()
}
