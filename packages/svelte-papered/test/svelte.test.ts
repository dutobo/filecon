import { render } from "svelte/server";
import { describe, expect, it } from "vitest";
import FileIcon from "../src/FileIcon.svelte";
import { FIXED_STYLE } from "../src/generated/variant.js";

describe("svelte specifics", () => {
  it("passes rest props to <svg>", () => {
    const { body } = render(FileIcon, { props: { name: "pdf", id: "icon" } as never });
    expect(body).toContain('id="icon"');
  });

  it.runIf(FIXED_STYLE === null)("uses style to select the icon style in the all-styles package", () => {
    const { body } = render(FileIcon, { props: { name: "pdf", style: "solid" } as never });
    expect(body).toContain('fill-opacity="0.32"');
    expect(body).not.toContain("style=");
  });
});
