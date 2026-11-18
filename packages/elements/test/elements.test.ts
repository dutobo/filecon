import { describe, expect, it } from "vitest";
import { PdfIcon } from "../src/icons";
import { defineFileconIcon, FileconIconElement } from "../src/index";

defineFileconIcon();

describe("web components specifics", () => {
  it("re-renders when attributes or properties change", () => {
    const element = document.createElement("filecon-icon");
    element.name = "pdf";
    document.body.append(element);
    const pdf = element.innerHTML;
    element.name = "zip";
    expect(element.innerHTML).not.toBe(pdf);
    element.setAttribute("name", "pdf");
    expect(element.innerHTML).toBe(pdf);
    element.size = 24;
    expect(element.querySelector("svg")?.getAttribute("width")).toBe("24");
    element.label = "PDF document";
    expect(element.querySelector("svg")?.getAttribute("role")).toBe("img");
    element.remove();
  });

  it("is an instance of FileconIconElement", () => {
    expect(document.createElement("filecon-icon")).toBeInstanceOf(FileconIconElement);
  });

  it("supports additional tag names", () => {
    defineFileconIcon("my-file-icon");
    defineFileconIcon("my-file-icon");
    const element = document.createElement("my-file-icon");
    element.setAttribute("file", "notes.md");
    document.body.append(element);
    expect(element.innerHTML).toBe(
      (() => {
        const reference = document.createElement("filecon-icon");
        reference.setAttribute("name", "md");
        document.body.append(reference);
        return reference.innerHTML;
      })(),
    );
  });

  it("exposes tag names on single icons", () => {
    expect(PdfIcon.tagName).toBe("filecon-pdf");
    expect(PdfIcon.iconName).toBe("pdf");
  });
});
