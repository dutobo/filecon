// JavaScript binding of the Rust plugin `tauri-plugin-filecon` (crates/tauri-plugin-filecon).
import { invoke } from "@tauri-apps/api/core";

/** Icon style. */
export type Style = "default" | "gray" | "solid" | "papered" | "papered-flat" | "papered-craft" | "scratch" | "chalk";
/** Color theme (`solid` looks the same in both). */
export type Theme = "light" | "dark";

export interface IconOptions {
  /** `default` (outline, colored label), `gray`, `solid`, `papered`, `papered-flat`, `papered-craft`, `scratch` or `chalk`. Default `default`. */
  style?: Style | undefined;
  /** `light` (default) or `dark`. */
  theme?: Theme | undefined;
}

/** Result of {@link iconForPath}. */
export interface PathIcon {
  /** Resolved icon name, e.g. `pdf`, `db-sqlite`. */
  name: string;
  /** Complete SVG document (40×40, with `<title>`). */
  svg: string;
}

const PLUGIN = "plugin:filecon";

/** Icon name for a file name (name rules and extension; no file access). */
export function resolveIcon(fileName: string): Promise<string> {
  return invoke<string>(`${PLUGIN}|resolve`, { fileName });
}

/** SVG for an icon name or extension (`pdf`, `.PDF`); unknown names return the `empty` icon. */
export function getIcon(name: string, options: IconOptions = {}): Promise<string> {
  return invoke<string>(`${PLUGIN}|icon`, { name, style: options.style ?? null, theme: options.theme ?? null });
}

/**
 * Icon for a file on disk: reads at most the first 1 KB for magic-byte detection (e.g. SQLite, PNG renamed to
 * `.dat`). Needs the `filecon:allow-icon-for-path` permission. Unreadable files fall back to the file name.
 */
export function iconForPath(path: string, options: IconOptions = {}): Promise<PathIcon> {
  return invoke<PathIcon>(`${PLUGIN}|icon_for_path`, {
    path,
    style: options.style ?? null,
    theme: options.theme ?? null,
  });
}
