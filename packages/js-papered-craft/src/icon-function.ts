import { type IconData, type RenderOptions, renderSvg, type Style } from "@filecon/shared";
import { FIXED_STYLE, type StyleOption } from "./generated/variant";

/** Options for `getIcon` and the single-icon functions. */
export type IconOptions = Omit<RenderOptions, "style"> & StyleOption;

/** A single-icon export: returns the complete SVG string. */
export type IconFunction = (options?: IconOptions) => string;

export function resolveStyle(options: IconOptions): Style {
  return FIXED_STYLE ?? (options as { style?: Style | undefined }).style ?? "default";
}

export function createIconFunction(data: IconData): IconFunction {
  return (options = {}) => renderSvg(data, { ...options, style: resolveStyle(options) });
}
