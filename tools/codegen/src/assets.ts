// Static asset packages built straight from the pack files: @filecon/iconify (Iconify JSON icon sets) and
// @filecon/css (CSS classes with data-URI background images). Output goes to packages/<pkg>/src/generated/
// (gitignored); the package build (scripts/build.mjs) copies/wraps it into dist/.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { HOMEPAGE, PACKAGES_DIR, REPOSITORY } from "./config";
import { syncDirectory } from "./fsutil";
import { innerMarkup, type Pack, svgPath } from "./pack";

type PackStyle = "default" | "gray" | "solid";
type PackTheme = "light" | "dark";

interface Variant {
  /** File / set id, e.g. `filecon-gray-dark`. */
  id: string;
  style: PackStyle;
  theme: PackTheme;
  label: string;
}

/** Every distinct look of the pack: default + gray in light/dark, solid once. */
export const ASSET_VARIANTS: readonly Variant[] = [
  { id: "filecon", style: "default", theme: "light", label: "Filecon" },
  { id: "filecon-dark", style: "default", theme: "dark", label: "Filecon Dark" },
  { id: "filecon-gray", style: "gray", theme: "light", label: "Filecon Gray" },
  { id: "filecon-gray-dark", style: "gray", theme: "dark", label: "Filecon Gray Dark" },
  { id: "filecon-solid", style: "solid", theme: "light", label: "Filecon Solid" },
];

const SAMPLES = ["pdf", "zip", "ts"];
const TITLE = /<title>[^<]*<\/title>/;

/** The pack SVG without its `<title>` (and without the trailing newline). */
export function packSvgWithoutTitle(style: PackStyle, theme: PackTheme, name: string): string {
  return readFileSync(svgPath(style, theme, name), "utf8")
    .replace(TITLE, "")
    .trimEnd();
}

function iconifySet(pack: Pack, variant: Variant): Record<string, unknown> {
  const icons: Record<string, { body: string }> = {};
  const categories: Record<string, string[]> = {};
  for (const icon of pack.icons) {
    icons[icon.name] = { body: innerMarkup(variant.style, variant.theme, icon.name) };
    const category = icon.meta.category ?? "generic";
    const list = categories[category] ?? [];
    list.push(icon.name);
    categories[category] = list;
  }
  return {
    prefix: variant.id,
    info: {
      name: variant.label,
      total: pack.icons.length,
      version: "0.1.0",
      author: { name: "Filecon", url: HOMEPAGE },
      license: { title: "Apache 2.0", spdx: "Apache-2.0", url: `${REPOSITORY}/blob/main/LICENSE` },
      samples: SAMPLES,
      height: 40,
      category: "Thematic",
      palette: true,
    },
    icons,
    categories: Object.fromEntries(Object.entries(categories).sort(([a], [b]) => a.localeCompare(b))),
    width: 40,
    height: 40,
  };
}

export function generateIconify(pack: Pack): void {
  const files: Record<string, string> = {};
  for (const variant of ASSET_VARIANTS) files[`${variant.id}.json`] = `${JSON.stringify(iconifySet(pack, variant))}\n`;
  syncDirectory(join(PACKAGES_DIR, "iconify", "src", "generated"), files);
}

/** Minimal URL encoding for an SVG inside `url("…")` (much smaller than encodeURIComponent). */
export function cssDataUri(svg: string): string {
  const encoded = svg.replace(
    /[%"#<>\n\r\t]/g,
    (char) => `%${char.charCodeAt(0).toString(16).toUpperCase().padStart(2, "0")}`,
  );
  return `data:image/svg+xml,${encoded}`;
}

const BASE_RULE =
  ".filecon{display:inline-block;width:40px;height:40px;flex:none;vertical-align:middle;" +
  "background:no-repeat center/contain}";

const rules = (pack: Pack, style: PackStyle, theme: PackTheme, indent = ""): string[] =>
  pack.icons.map(
    (icon) =>
      `${indent}.filecon-${icon.name}{background-image:url("${cssDataUri(packSvgWithoutTitle(style, theme, icon.name))}")}`,
  );

const header = (description: string): string =>
  `/*! Filecon ${description} – ${HOMEPAGE} – Apache-2.0 (see LICENSE/NOTICE). Generated, do not edit. */`;

export function generateCss(pack: Pack): void {
  const files: Record<string, string> = {};
  for (const style of ["default", "gray"] as const) {
    for (const theme of ["light", "dark"] as const) {
      files[`${style}-${theme}.css`] = [
        header(`${style} style, ${theme} theme`),
        BASE_RULE,
        ...rules(pack, style, theme),
        "",
      ].join("\n");
    }
    files[`${style}.css`] = [
      header(`${style} style, light theme with dark theme via prefers-color-scheme`),
      BASE_RULE,
      ...rules(pack, style, "light"),
      "@media (prefers-color-scheme: dark){",
      ...rules(pack, style, "dark", "  "),
      "}",
      "",
    ].join("\n");
  }
  files["solid.css"] = [header("solid style"), BASE_RULE, ...rules(pack, "solid", "light"), ""].join("\n");
  syncDirectory(join(PACKAGES_DIR, "css", "src", "generated"), files);
}
