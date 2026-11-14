// Reads the icon pack (read-only source of truth) and derives everything the packages need.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { iconComponentName } from "../../../packages/shared/src/names";
import {
  THEME_CLASS_PREFIX,
  type ThemeRule,
  type ThemeTable,
  toDarkMarkup,
  toLightMarkup,
} from "../../../packages/shared/src/theme-core";
import type { IconData, Style } from "../../../packages/shared/src/types";
import { PACK_DIR } from "./config";

export interface ManifestEntry {
  type: "ext" | "generic" | "generic-ext" | "variant";
  color: string;
  category?: string;
  label?: string;
  family?: string;
  of?: string;
  meaning?: string;
  ambiguous?: string[];
}

export interface PackIcon {
  name: string;
  /** Single-export name, e.g. `PdfIcon`, `Icon7z`. */
  componentName: string;
  /** Identifier of the data constant, e.g. `d_ts_stream`. */
  dataId: string;
  meta: ManifestEntry;
  /** Inner markup per style; `default`/`gray` are themed (light colors + `fc-t*` classes). */
  data: Required<IconData>;
}

export interface Pack {
  manifest: Record<string, ManifestEntry>;
  /** Icons sorted by name. */
  icons: PackIcon[];
  themeTable: ThemeTable;
}

const SVG_PATTERN =
  /^<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" width="40" height="40" viewBox="0 0 40 40" fill="none"><title>([^<]*)<\/title>([\s\S]*)<\/svg>\n?$/;
const TAG = /<[^<>]+>/g;
const ATTR = / ([\w:-]+)="([^"]*)"/g;

export function svgPath(style: Style, theme: "light" | "dark", name: string): string {
  return style === "solid" ? join(PACK_DIR, "solid", `${name}.svg`) : join(PACK_DIR, style, theme, `${name}.svg`);
}

/** Inner markup of a pack SVG (without the outer `<svg>` and the `<title>`). */
export function innerMarkup(style: Style, theme: "light" | "dark", name: string): string {
  const file = svgPath(style, theme, name);
  const match = SVG_PATTERN.exec(readFileSync(file, "utf8"));
  if (!match) throw new Error(`Unexpected SVG structure: ${file}`);
  if (match[1] !== name) throw new Error(`<title> "${match[1]}" does not match file name: ${file}`);
  return match[2] as string;
}

const attributes = (tag: string): Map<string, string> =>
  new Map([...tag.matchAll(ATTR)].map((m) => [m[1] as string, m[2] as string]));

/** Differences between light and dark tags as `[attribute, light, dark]` per tag index. */
function diffTags(light: string, dark: string, label: string): Map<number, ThemeRule[]> {
  const lightTags = light.match(TAG) ?? [];
  const darkTags = dark.match(TAG) ?? [];
  if (light.replace(TAG, "\u0000") !== dark.replace(TAG, "\u0000") || lightTags.length !== darkTags.length) {
    throw new Error(`Light and dark markup differ structurally: ${label}`);
  }
  const diffs = new Map<number, ThemeRule[]>();
  lightTags.forEach((lightTag, index) => {
    const darkTag = darkTags[index] as string;
    if (lightTag === darkTag) return;
    if (lightTag.includes(" class=")) throw new Error(`Unexpected class attribute: ${label}`);
    const la = attributes(lightTag);
    const da = attributes(darkTag);
    if ([...la.keys()].join() !== [...da.keys()].join()) throw new Error(`Attribute sets differ: ${label}`);
    const rules: ThemeRule[] = [];
    for (const [key, value] of la) {
      const darkValue = da.get(key) as string;
      if (value !== darkValue) rules.push([key, value, darkValue]);
    }
    diffs.set(index, rules);
  });
  return diffs;
}

const ruleKey = (rule: ThemeRule): string => rule.join("\u0000");

export function loadPack(): Pack {
  const manifest = JSON.parse(readFileSync(join(PACK_DIR, "manifest.json"), "utf8")) as Record<string, ManifestEntry>;
  const names = Object.keys(manifest).sort();

  // Pass 1: collect all light/dark differences to build a stable class table.
  const sources = new Map<string, Record<string, { light: string; dark: string; diffs: Map<number, ThemeRule[]> }>>();
  const allRules = new Map<string, ThemeRule>();
  for (const name of names) {
    const perStyle: Record<string, { light: string; dark: string; diffs: Map<number, ThemeRule[]> }> = {};
    for (const style of ["default", "gray"] as const) {
      const light = innerMarkup(style, "light", name);
      const dark = innerMarkup(style, "dark", name);
      const diffs = diffTags(light, dark, `${style}/${name}`);
      for (const rules of diffs.values()) for (const rule of rules) allRules.set(ruleKey(rule), rule);
      perStyle[style] = { light, dark, diffs };
    }
    sources.set(name, perStyle);
  }
  const sortedRules = [...allRules.values()].sort((a, b) => ruleKey(a).localeCompare(ruleKey(b)));
  const themeTable: Record<string, ThemeRule> = {};
  const classByRule = new Map<string, string>();
  sortedRules.forEach((rule, index) => {
    const cls = `${THEME_CLASS_PREFIX}${index}`;
    themeTable[cls] = rule;
    classByRule.set(ruleKey(rule), cls);
  });

  // Pass 2: themed markup = light markup + classes; verify that both themes round-trip exactly.
  const componentNames = new Map<string, string>();
  const icons = names.map((name): PackIcon => {
    const perStyle = sources.get(name) as Record<
      string,
      { light: string; dark: string; diffs: Map<number, ThemeRule[]> }
    >;
    const themed = (style: "default" | "gray"): string => {
      const { light, dark, diffs } = perStyle[style] as {
        light: string;
        dark: string;
        diffs: Map<number, ThemeRule[]>;
      };
      let index = 0;
      const markup = light.replace(TAG, (tag) => {
        const rules = diffs.get(index++);
        if (!rules) return tag;
        const classes = rules.map((rule) => classByRule.get(ruleKey(rule))).join(" ");
        return tag.replace(/(\/?)>$/, ` class="${classes}"$1>`);
      });
      if (toLightMarkup(markup) !== light) throw new Error(`Light round-trip failed: ${style}/${name}`);
      if (toDarkMarkup(markup, themeTable) !== dark) throw new Error(`Dark round-trip failed: ${style}/${name}`);
      return markup;
    };
    const solidLight = innerMarkup("solid", "light", name);
    const componentName = iconComponentName(name);
    const clash = componentNames.get(componentName);
    if (clash) throw new Error(`Component name collision: ${clash} and ${name} -> ${componentName}`);
    componentNames.set(componentName, name);
    return {
      name,
      componentName,
      dataId: `d_${name.replace(/[^a-z0-9]/g, "_")}`,
      meta: manifest[name] as ManifestEntry,
      data: { default: themed("default"), gray: themed("gray"), solid: solidLight },
    };
  });
  return { manifest, icons, themeTable };
}
