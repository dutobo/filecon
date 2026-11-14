/** Visual style of an icon. */
export type Style = "default" | "gray" | "solid";

/**
 * Color theme. `auto` follows `prefers-color-scheme` via an embedded `<style>` (SSR-safe).
 * The `solid` style looks identical in every theme.
 */
export type Theme = "light" | "dark" | "auto";

/**
 * Icon markup per style: only the inner SVG markup (no outer `<svg>`, no `<title>`).
 * `default` and `gray` are stored "themed" (light colors plus `fc-t*` classes that describe the dark colors).
 */
export interface IconData {
  readonly default?: string;
  readonly gray?: string;
  readonly solid?: string;
}

export const STYLES: readonly Style[] = ["default", "gray", "solid"];
export const THEMES: readonly Theme[] = ["light", "dark", "auto"];
