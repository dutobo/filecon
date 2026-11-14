import { createElement, createRef } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { FIXED_STYLE } from "../src/generated/variant";
import { PdfIcon, TsStreamIcon } from "../src/icons";
import { FileIcon } from "../src/index";

describe("react specifics", () => {
  it("sets displayName on single icons", () => {
    expect(PdfIcon.displayName).toBe("PdfIcon");
    expect(TsStreamIcon.displayName).toBe("TsStreamIcon");
  });

  it("passes rest props to <svg>", () => {
    const html = renderToStaticMarkup(
      createElement(FileIcon, { name: "pdf", "data-testid": "x", id: "icon" } as never),
    );
    expect(html).toContain('data-testid="x"');
    expect(html).toContain('id="icon"');
  });

  it("accepts a ref", () => {
    const ref = createRef<SVGSVGElement>();
    expect(() => renderToStaticMarkup(createElement(PdfIcon, { ref }))).not.toThrow();
  });

  it.runIf(FIXED_STYLE !== null)("keeps native inline style in single-style packages", () => {
    const html = renderToStaticMarkup(createElement(FileIcon, { name: "pdf", style: { color: "red" } } as never));
    expect(html).toContain('style="color:red"');
  });

  it.runIf(FIXED_STYLE === null)("uses style to select the icon style in the all-styles package", () => {
    const solid = renderToStaticMarkup(createElement(FileIcon, { name: "pdf", style: "solid" } as never));
    expect(solid).not.toContain("style=");
    expect(solid).toContain('fill-opacity="0.32"');
  });
});
