import { describe, expect, it, vi } from "vitest";

vi.mock("react-native", () => ({ useColorScheme: () => "light" }));
vi.mock("react-native-svg", () => ({ SvgXml: "SvgXml" }));

const { FileIcon } = await import("../src/index");
const { PdfIcon } = await import("../src/icons");

type ForwardRef = {
  render(props: Record<string, unknown>, ref: unknown): { type: unknown; props: Record<string, unknown> };
};
const render = (component: unknown, props: Record<string, unknown>) => (component as ForwardRef).render(props, null);

describe("react-native specifics", () => {
  it("renders SvgXml with size and hidden accessibility by default", () => {
    const element = render(FileIcon, { name: "pdf", size: 24 });
    expect(element.type).toBe("SvgXml");
    expect(element.props).toMatchObject({
      width: 24,
      height: 24,
      accessible: false,
      importantForAccessibility: "no-hide-descendants",
    });
  });

  it("exposes the title as accessibility label", () => {
    expect(render(FileIcon, { name: "pdf", title: "PDF" }).props).toMatchObject({
      accessible: true,
      accessibilityLabel: "PDF",
      accessibilityRole: "image",
    });
  });

  it("sets displayName on single icons", () => {
    expect(PdfIcon.displayName).toBe("PdfIcon");
  });
});
