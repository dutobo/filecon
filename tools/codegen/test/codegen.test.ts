import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { toDarkMarkup, toLightMarkup } from "../../../packages/shared/src/theme-core";
import { PACK_DIR } from "../src/config";
import { renderTemplate } from "../src/mustache";
import { innerMarkup, loadPack } from "../src/pack";
import { stripSourceCondition, tsupExports } from "../src/package-json";

const pack = loadPack();

describe("pack", () => {
  it("loads all icons of the manifest", () => {
    const manifest = JSON.parse(readFileSync(join(PACK_DIR, "manifest.json"), "utf8")) as object;
    expect(pack.icons).toHaveLength(Object.keys(manifest).length);
    expect(pack.icons).toHaveLength(703);
  });

  it("derives themed markup that round-trips to the light and dark SVGs", () => {
    for (const icon of pack.icons) {
      for (const style of ["default", "gray"] as const) {
        expect(toLightMarkup(icon.data[style])).toBe(innerMarkup(style, "light", icon.name));
        expect(toDarkMarkup(icon.data[style], pack.themeTable)).toBe(innerMarkup(style, "dark", icon.name));
      }
      expect(icon.data.solid).toBe(innerMarkup("solid", "light", icon.name));
    }
  });

  it("produces unique component and data identifiers", () => {
    expect(new Set(pack.icons.map((icon) => icon.componentName)).size).toBe(703);
    expect(new Set(pack.icons.map((icon) => icon.dataId)).size).toBe(703);
  });
});

describe("templates", () => {
  it("renders placeholders and sections", () => {
    const vars = { name: "x", yes: true, no: false };
    expect(renderTemplate("a {{name}} {{#yes}}Y{{/yes}}{{#no}}N{{/no}}{{^no}}!{{/no}}", vars)).toBe("a x Y!");
    expect(() => renderTemplate("{{missing}}", vars)).toThrow(/missing/);
  });
});

describe("package.json", () => {
  it("strips the dev-only source condition for publishing", () => {
    const exportsMap = tsupExports(["index", "icons"]);
    expect(JSON.stringify(exportsMap)).toContain("@filecon/source");
    expect(JSON.stringify(stripSourceCondition(exportsMap))).not.toContain("@filecon/source");
  });
});
