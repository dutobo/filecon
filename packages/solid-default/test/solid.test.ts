import { createComponent } from "solid-js";
import { renderToString } from "solid-js/web";
import { describe, expect, it } from "vitest";
import { FIXED_STYLE } from "../src/generated/variant";
import { FileIcon } from "../src/index";

describe("solid specifics", () => {
  it("passes rest props to <svg>", () => {
    const html = renderToString(() => createComponent(FileIcon, { name: "pdf", id: "icon" } as never));
    expect(html).toContain('id="icon"');
  });

  it.runIf(FIXED_STYLE === null)("uses style to select the icon style in the all-styles package", () => {
    const html = renderToString(() => createComponent(FileIcon, { name: "pdf", style: "solid" } as never));
    expect(html).toContain('fill-opacity="0.32"');
    expect(html).not.toContain("style=");
  });
});
