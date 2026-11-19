import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { ICON_NAMES, normalizeSvg, sourceSvg, TEST_STYLES, type TestStyle } from "@filecon/testkit";
import { getIconData, iconToHTML, iconToSVG, validateIconSet } from "@iconify/utils";
import { describe, expect, it } from "vitest";

interface IconSet {
  id: string;
  style: TestStyle;
  theme: "light" | "dark";
}

// One set per style and theme; `solid` looks the same in both themes and has a single set.
const SETS: IconSet[] = TEST_STYLES.flatMap((style): IconSet[] => {
  const id = style === "default" ? "filecon" : `filecon-${style}`;
  if (style === "solid") return [{ id, style, theme: "light" }];
  return [
    { id, style, theme: "light" },
    { id: `${id}-dark`, style, theme: "dark" },
  ];
});

it("has a set for every style and theme", () => {
  expect(SETS).toHaveLength(17);
});

const dist = join(import.meta.dirname, "..", "dist");
const load = (id: string) => JSON.parse(readFileSync(join(dist, `${id}.json`), "utf8"));
const withoutTitle = (svg: string) => svg.replace(/<title>[^<]*<\/title>/, "");

describe("@filecon/iconify", () => {
  for (const set of SETS) {
    describe(set.id, () => {
      const data = load(set.id);

      it("is a valid Iconify icon set with every icon", () => {
        expect(() => validateIconSet(data)).not.toThrow();
        expect(data.prefix).toBe(set.id);
        expect(Object.keys(data.icons).sort()).toEqual([...ICON_NAMES]);
        expect(data.info.total).toBe(ICON_NAMES.length);
        expect(data.info.license.spdx).toBe("Apache-2.0");
      });

      it("renders every icon like the pack", () => {
        const failed = ICON_NAMES.filter((name) => {
          const icon = getIconData(data, name);
          if (!icon) return true;
          const rendered = iconToSVG(icon);
          const svg = iconToHTML(rendered.body, { ...rendered.attributes, fill: "none" });
          return normalizeSvg(svg) !== normalizeSvg(withoutTitle(sourceSvg(set.style, set.theme, name)));
        });
        expect(failed).toEqual([]);
      });
    });
  }

  it("exposes prefixes and lazy collections (ESM and CJS)", async () => {
    const esm = await import(join(dist, "index.js"));
    expect(esm.prefixes).toEqual(SETS.map((set) => set.id).sort());
    expect((await esm.collections.filecon()).prefix).toBe("filecon");
    const cjs = createRequire(import.meta.url)(join(dist, "index.cjs"));
    expect((await cjs.collections["filecon-solid"]()).prefix).toBe("filecon-solid");
    expect(createRequire(import.meta.url)(join(dist, "filecon-gray.cjs")).prefix).toBe("filecon-gray");
    expect((await esm.collections["filecon-papered-flat-dark"]()).prefix).toBe("filecon-papered-flat-dark");
  });
});
