import { type IconName, renderSvg, resolveIcon, toIconName } from "@filecon/shared";
import { iconData } from "./generated/variant";
import { type IconOptions, resolveStyle } from "./icon-function";

/**
 * SVG string for an icon name or extension (`"pdf"`, `".PDF"`). Unknown names render the `empty` icon.
 */
export function getIcon(name: IconName | (string & {}), options: IconOptions = {}): string {
  return renderSvg(iconData[toIconName(name)], { ...options, style: resolveStyle(options) });
}

/** SVG string for a file name, using the resolver (pass `head` = first bytes of the file for magic-byte detection). */
export function getFileIcon(fileName: string, options: IconOptions & { head?: Uint8Array } = {}): string {
  const { head, ...rest } = options;
  return getIcon(resolveIcon(fileName, head), rest as IconOptions);
}
