// Acceptance tests shared by every framework package (criteria 1 and 5 of the project brief).
import { describe, expect, it } from "vitest";
import { evaluateAutoTheme, normalizeSvg, rootAttributes } from "./normalize";
import { ICON_NAMES, sourceSvg, type TestStyle, type TestTheme } from "./pack";

export interface RenderProps {
  name?: string;
  file?: string;
  style?: TestStyle;
  theme?: TestTheme;
  size?: number;
  title?: string;
  className?: string;
}

type Rendered = string | Promise<string>;

export interface ConformanceOptions {
  packageName: string;
  /** Styles contained in the package (one for single-style packages). */
  styles: readonly TestStyle[];
  /** Renders the main component (`<FileIcon>` or equivalent) to an SVG string. */
  render(props: RenderProps): Rendered;
  /** Renders a single-icon export (e.g. `PdfIcon`) to an SVG string. */
  renderSingle(exportName: string, props: Omit<RenderProps, "name" | "file">): Rendered;
  /** Module namespace of the single-icon exports (e.g. `import * as icons from "../src/icons"`). */
  singleExports: Record<string, unknown>;
  iconComponentName(name: string): string;
  /**
   * How `theme="auto"` works: `css` = embedded `prefers-color-scheme` stylesheet (default),
   * `color-scheme` = the platform reports the scheme (React Native); `setColorScheme` switches it.
   */
  autoMode?: "css" | "color-scheme";
  setColorScheme?(scheme: "light" | "dark"): void;
  /** Whether a `className` prop ends up as `class` on the `<svg>` (default true). */
  classOnSvg?: boolean;
}

async function mismatches(
  names: readonly string[],
  expected: (name: string) => string,
  actual: (name: string) => Rendered,
): Promise<string[]> {
  const failed: string[] = [];
  for (const name of names) {
    const got = normalizeSvg(await actual(name));
    if (got !== normalizeSvg(expected(name))) failed.push(name);
  }
  return failed;
}

export function conformanceSuite(options: ConformanceOptions): void {
  const { styles } = options;
  const firstStyle = styles[0] as TestStyle;
  const singleExportNames = Object.keys(options.singleExports).filter((key) => /^(Icon\w+|\w+Icon)$/.test(key));

  describe(`${options.packageName} – conformance`, () => {
    it("has one single-icon export per manifest entry", () => {
      expect(singleExportNames).toHaveLength(ICON_NAMES.length);
      expect(new Set(singleExportNames)).toEqual(new Set(ICON_NAMES.map(options.iconComponentName)));
    });

    for (const style of styles) {
      for (const theme of ["light", "dark"] as const) {
        it(`renders every icon like the pack: ${style}/${theme}`, async () => {
          const failed = await mismatches(
            ICON_NAMES,
            (name) => sourceSvg(style, theme, name),
            (name) => options.render({ name, style, theme }),
          );
          expect(failed).toEqual([]);
        });
      }

      it(`theme="auto" resolves to the pack's light and dark SVGs: ${style}`, async () => {
        for (const scheme of ["light", "dark"] as const) {
          const failed: string[] = [];
          for (const name of ICON_NAMES) {
            let rendered: string;
            if (options.autoMode === "color-scheme") {
              options.setColorScheme?.(scheme);
              rendered = await options.render({ name, style, theme: "auto" });
            } else {
              const auto = await options.render({ name, style, theme: "auto" });
              rendered = style === "solid" ? auto : evaluateAutoTheme(auto, scheme);
            }
            if (normalizeSvg(rendered) !== normalizeSvg(sourceSvg(style, scheme, name))) failed.push(name);
          }
          expect(failed, scheme).toEqual([]);
        }
      });
    }

    it("renders every single-icon export like the pack", async () => {
      const failed: string[] = [];
      for (const name of ICON_NAMES) {
        const exportName = options.iconComponentName(name);
        for (const theme of ["light", "dark"] as const) {
          const rendered = await options.renderSingle(exportName, { style: firstStyle, theme });
          if (normalizeSvg(rendered) !== normalizeSvg(sourceSvg(firstStyle, theme, name)))
            failed.push(`${name}/${theme}`);
        }
      }
      expect(failed).toEqual([]);
    });

    it("defaults to theme light, size 40 and the package's first style", async () => {
      const svg = await options.render({ name: "pdf" });
      expect(normalizeSvg(svg)).toBe(normalizeSvg(sourceSvg(firstStyle, "light", "pdf")));
      expect(rootAttributes(svg)).toMatchObject({ width: "40", height: "40", viewBox: "0 0 40 40", fill: "none" });
    });

    it("applies size", async () => {
      expect(rootAttributes(await options.render({ name: "pdf", size: 48 }))).toMatchObject({
        width: "48",
        height: "48",
      });
    });

    it("resolves file names", async () => {
      const cases: [string, string][] = [
        ["report.final.pdf", "pdf"],
        ["Dockerfile", "dockerfile"],
        ["Makefile", "mk"],
        ["archive.unknown-ext", "empty"],
      ];
      for (const [file, icon] of cases) {
        expect(normalizeSvg(await options.render({ file })), file).toBe(
          normalizeSvg(sourceSvg(firstStyle, "light", icon)),
        );
      }
    });

    it("is aria-hidden without title", async () => {
      const svg = await options.render({ name: "pdf" });
      const attrs = rootAttributes(svg);
      expect(attrs["aria-hidden"]).toBe("true");
      expect(attrs.role).toBeUndefined();
      expect(svg).not.toContain("<title>");
    });

    it('has role="img" and a <title> with title', async () => {
      const svg = await options.render({ name: "pdf", title: 'Report <"final">' });
      const attrs = rootAttributes(svg);
      expect(attrs.role).toBe("img");
      expect(attrs["aria-hidden"]).toBeUndefined();
      expect(svg).toContain("<title>Report &lt;&quot;final&quot;&gt;</title>");
    });

    if (options.classOnSvg !== false) {
      it("passes className through", async () => {
        expect(rootAttributes(await options.render({ name: "pdf", className: "icon big" })).class).toBe("icon big");
      });
    }
  });
}
