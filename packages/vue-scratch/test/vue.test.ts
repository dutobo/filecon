import { describe, expect, it } from "vitest";
import { createSSRApp, h } from "vue";
import { renderToString } from "vue/server-renderer";
import { FIXED_STYLE } from "../src/generated/variant";
import { PdfIcon } from "../src/icons";
import { FileIcon } from "../src/index";

describe("vue specifics", () => {
  it("names single icon components", () => {
    expect(PdfIcon.name).toBe("PdfIcon");
  });

  it("lets attributes fall through to <svg>", async () => {
    const html = await renderToString(
      createSSRApp({ render: () => h(FileIcon, { name: "pdf", id: "icon", style: "color:red" }) }),
    );
    expect(html).toContain('id="icon"');
    expect(html).toContain('style="color:red;"');
  });

  it.runIf(FIXED_STYLE === null)("selects the icon style with icon-style", async () => {
    const html = await renderToString(createSSRApp({ render: () => h(FileIcon, { name: "pdf", iconStyle: "solid" }) }));
    expect(html).toContain('fill-opacity="0.32"');
  });
});
