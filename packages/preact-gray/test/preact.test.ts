import { h } from "preact";
import { renderToString } from "preact-render-to-string";
import { describe, expect, it } from "vitest";
import { FIXED_STYLE } from "../src/generated/variant";
import { PdfIcon } from "../src/icons";
import { FileIcon } from "../src/index";

describe("preact specifics", () => {
  it("sets displayName on single icons", () => {
    expect(PdfIcon.displayName).toBe("PdfIcon");
  });

  it("passes rest props to <svg>", () => {
    const html = renderToString(h(FileIcon, { name: "pdf", id: "icon", "data-testid": "x" } as never));
    expect(html).toContain('id="icon"');
    expect(html).toContain('data-testid="x"');
  });

  it.runIf(FIXED_STYLE === null)("uses style to select the icon style in the all-styles package", () => {
    const solid = renderToString(h(FileIcon, { name: "pdf", style: "solid" } as never));
    expect(solid).not.toContain("style=");
    expect(solid).toContain('fill-opacity="0.32"');
  });
});
