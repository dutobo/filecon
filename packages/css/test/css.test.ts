import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ICON_NAMES, sourceSvg, TEST_STYLES, type TestStyle } from "@filecon/testkit";
import { describe, expect, it } from "vitest";

const dist = join(import.meta.dirname, "..", "dist");
const read = (file: string) => readFileSync(join(dist, file), "utf8");
const RULE = /\.filecon-([a-z0-9-]+)\{background-image:url\("data:image\/svg\+xml,([^"]*)"\)\}/g;

/** Icon name -> decoded SVG for every rule in a block of CSS. */
function parseRules(css: string): Map<string, string> {
  const result = new Map<string, string>();
  for (const match of css.matchAll(RULE)) result.set(match[1] as string, decodeURIComponent(match[2] as string));
  return result;
}

const expected = (style: TestStyle, theme: "light" | "dark", name: string) =>
  sourceSvg(style, theme, name)
    .replace(/<title>[^<]*<\/title>/, "")
    .trimEnd();

function expectIcons(rules: Map<string, string>, style: TestStyle, theme: "light" | "dark") {
  expect([...rules.keys()].sort()).toEqual([...ICON_NAMES]);
  const failed = ICON_NAMES.filter((name) => rules.get(name) !== expected(style, theme, name));
  expect(failed).toEqual([]);
}

describe("@filecon/css", () => {
  for (const style of TEST_STYLES.filter((style) => style !== "solid")) {
    for (const theme of ["light", "dark"] as const) {
      it(`${style}-${theme}.css embeds every pack SVG byte for byte`, () => {
        expectIcons(parseRules(read(`${style}-${theme}.css`)), style, theme);
      });
    }

    it(`${style}.css switches to the dark icons via prefers-color-scheme`, () => {
      const css = read(`${style}.css`);
      const index = css.indexOf("@media (prefers-color-scheme: dark){");
      expect(index).toBeGreaterThan(0);
      expectIcons(parseRules(css.slice(0, index)), style, "light");
      expectIcons(parseRules(css.slice(index)), style, "dark");
    });
  }

  it("solid.css embeds every pack SVG byte for byte", () => {
    expectIcons(parseRules(read("solid.css")), "solid", "light");
  });

  it("defines the base class and only uses safe characters inside url()", () => {
    for (const file of [
      "default.css",
      "gray-dark.css",
      "solid.css",
      "papered.css",
      "scratch-dark.css",
      "chalk.css",
      "iconic-dark.css",
    ]) {
      const css = read(file);
      expect(css).toContain(".filecon{display:inline-block;width:40px;height:40px;");
      for (const match of css.matchAll(RULE)) expect(match[2]).not.toMatch(/["<>#\n]/);
    }
  });
});
