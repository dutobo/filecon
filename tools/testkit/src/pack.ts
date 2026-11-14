import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export type TestStyle = "default" | "gray" | "solid";
export type TestTheme = "light" | "dark" | "auto";

export const PACK_DIR = fileURLToPath(new URL("../../../icon-pack/", import.meta.url));

export const manifest = JSON.parse(readFileSync(`${PACK_DIR}manifest.json`, "utf8")) as Record<
  string,
  { type: string; family?: string }
>;

/** All icon names of the pack, sorted. */
export const ICON_NAMES: readonly string[] = Object.keys(manifest).sort();

const cache = new Map<string, string>();

/** Original SVG from the pack (`solid` has no theme folders). */
export function sourceSvg(style: TestStyle, theme: "light" | "dark", name: string): string {
  const path = style === "solid" ? `${PACK_DIR}solid/${name}.svg` : `${PACK_DIR}${style}/${theme}/${name}.svg`;
  let svg = cache.get(path);
  if (svg === undefined) {
    svg = readFileSync(path, "utf8");
    cache.set(path, svg);
  }
  return svg;
}

export interface ResolveCase {
  file: string;
  content_hex: string;
  expected: string;
}

export const resolveCases = JSON.parse(
  readFileSync(`${PACK_DIR}tests/resolve-cases.json`, "utf8"),
) as readonly ResolveCase[];

export function hexToBytes(hex: string): Uint8Array {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = Number.parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  return out;
}
