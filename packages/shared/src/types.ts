/**
 * All icon styles. `default`, `gray` and `solid` come from the icon pack; the others are drawn by the Filecon
 * style generator (tools/stylegen) on top of it.
 */
export const STYLES = [
  "default",
  "gray",
  "solid",
  "papered",
  "papered-flat",
  "papered-craft",
  "scratch",
  "chalk",
] as const;

/** Visual style of an icon. */
export type Style = (typeof STYLES)[number];

/** Styles that look the same in every theme (they have no dark variant). */
export const THEMELESS_STYLES: readonly Style[] = ["solid"];

/** `true` if the style has separate light and dark variants. */
export const isThemedStyle = (style: Style): boolean => !THEMELESS_STYLES.includes(style);

/**
 * Color theme. `auto` follows `prefers-color-scheme` via an embedded `<style>` (SSR-safe).
 * The `solid` style looks identical in every theme.
 */
export type Theme = "light" | "dark" | "auto";

/**
 * Icon markup per style: only the inner SVG markup (no outer `<svg>`, no `<title>`).
 * Themed styles are stored "themed" (light colors plus `fc-t*` classes that describe the dark colors).
 */
export type IconData = { readonly [S in Style]?: string };

export const THEMES: readonly Theme[] = ["light", "dark", "auto"];
