import { autoMarkup, darkMarkup, lightMarkup } from "./theme";
import { type IconData, STYLES, type Style, type Theme } from "./types";

export const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
export const VIEW_BOX = "0 0 40 40";
export const DEFAULT_SIZE = 40;

export interface ContentOptions {
  style?: Style | undefined;
  theme?: Theme | undefined;
  title?: string | undefined;
}

export interface AttributeOptions {
  size?: number | string | undefined;
  title?: string | undefined;
}

export type AttributeValue = string | number | boolean | null | undefined;

export interface RenderOptions extends ContentOptions, AttributeOptions {
  className?: string | undefined;
  attributes?: Readonly<Record<string, AttributeValue>> | undefined;
}

/** Outer `<svg>` attributes used by every package. */
export interface SvgAttributes {
  xmlns: string;
  width: string;
  height: string;
  viewBox: string;
  fill: "none";
  role?: "img";
  "aria-hidden"?: "true";
}

/** The requested style if the data has it, otherwise the first available one (single-style packages). */
export function availableStyle(data: IconData, style: Style = "default"): Style {
  if (data[style] !== undefined) return style;
  return STYLES.find((candidate) => data[candidate] !== undefined) ?? style;
}

const cache = new Map<string, string>();

/** Inner markup (without `<svg>` and `<title>`) for a style and theme. `solid` ignores the theme. */
export function iconMarkup(data: IconData, style: Style = "default", theme: Theme = "light"): string {
  const resolved = availableStyle(data, style);
  const markup = data[resolved] ?? "";
  if (resolved === "solid") return markup;
  const key = `${theme}\u0000${markup}`;
  let result = cache.get(key);
  if (result === undefined) {
    if (theme === "dark") result = darkMarkup(markup);
    else if (theme === "auto") result = autoMarkup(markup);
    else result = lightMarkup(markup);
    if (cache.size > 4096) cache.clear();
    cache.set(key, result);
  }
  return result;
}

/** Escapes text for XML/HTML text and attribute content. */
export function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Children of the `<svg>` element: optional `<title>` followed by the icon markup. */
export function iconContent(data: IconData, options: ContentOptions = {}): string {
  const markup = iconMarkup(data, options.style, options.theme);
  return options.title ? `<title>${escapeXml(options.title)}</title>${markup}` : markup;
}

/** Outer `<svg>` attributes. With `title` the icon gets `role="img"`, otherwise `aria-hidden="true"`. */
export function svgAttributes(options: AttributeOptions = {}): SvgAttributes {
  const size = String(options.size ?? DEFAULT_SIZE);
  const attributes: SvgAttributes = {
    xmlns: SVG_NAMESPACE,
    width: size,
    height: size,
    viewBox: VIEW_BOX,
    fill: "none",
  };
  if (options.title) attributes.role = "img";
  else attributes["aria-hidden"] = "true";
  return attributes;
}

/** Serializes attributes (`true` -> bare attribute, `false`/`null`/`undefined` -> omitted). */
export function serializeAttributes(attributes: Readonly<Record<string, AttributeValue>>): string {
  let result = "";
  for (const [key, value] of Object.entries(attributes)) {
    if (value === undefined || value === null || value === false) continue;
    result += value === true ? ` ${key}` : ` ${key}="${escapeXml(String(value))}"`;
  }
  return result;
}

/** Complete SVG document as a string. */
export function renderSvg(data: IconData, options: RenderOptions = {}): string {
  const attributes = serializeAttributes({
    ...svgAttributes(options),
    class: options.className,
    ...options.attributes,
  });
  return `<svg${attributes}>${iconContent(data, options)}</svg>`;
}

/** `data:` URI for an SVG string (usable in `<img src>` or CSS `url()`). */
export function toDataUri(svg: string): string {
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}
