import { readFileSync } from "node:fs";
import { hexToBytes, ICON_NAMES, PACK_DIR, resolveCases } from "@filecon/testkit";
import { describe, expect, it } from "vitest";
import {
  escapeXml,
  iconComponentName,
  iconNames,
  isIconName,
  resolveIcon,
  svgAttributes,
  THEME_TABLE,
  toDataUri,
  toIconName,
} from "../src/index";

describe("names", () => {
  it("matches the manifest", () => {
    expect([...iconNames]).toEqual(ICON_NAMES);
    expect(iconNames).toHaveLength(703);
  });

  it("builds component names", () => {
    expect(iconComponentName("pdf")).toBe("PdfIcon");
    expect(iconComponentName("ts-stream")).toBe("TsStreamIcon");
    expect(iconComponentName("db-sqlite")).toBe("DbSqliteIcon");
    expect(iconComponentName("7z")).toBe("Icon7z");
    expect(iconComponentName("3d")).toBe("Icon3d");
  });

  it("has no component name collisions", () => {
    const names = iconNames.map(iconComponentName);
    expect(new Set(names).size).toBe(iconNames.length);
    for (const name of names) expect(name).toMatch(/^[A-Z][A-Za-z0-9]*$/);
  });

  it("normalizes names", () => {
    expect(toIconName(".PDF")).toBe("pdf");
    expect(toIconName("nope")).toBe("empty");
    expect(isIconName("pdf")).toBe(true);
    expect(isIconName("PDF")).toBe(false);
  });
});

describe("resolveIcon", () => {
  it(`passes all ${resolveCases.length} cases of icon-pack/tests/resolve-cases.json`, () => {
    expect(resolveCases).toHaveLength(20);
    for (const c of resolveCases) expect(resolveIcon(c.file, hexToBytes(c.content_hex)), c.file).toBe(c.expected);
  });

  it("works with names only", () => {
    expect(resolveIcon("report.final.pdf")).toBe("pdf");
    expect(resolveIcon("src/app/Dockerfile")).toBe("dockerfile");
    expect(resolveIcon("C:\\work\\Makefile")).toBe("mk");
    expect(resolveIcon("Thumbs.db")).toBe("db");
    expect(resolveIcon("noext")).toBe("empty");
    expect(resolveIcon("")).toBe("empty");
  });

  it("only looks at the first 1 KB", () => {
    const head = new Uint8Array(4096);
    head.set(new TextEncoder().encode("#import"), 2000);
    expect(resolveIcon("x.m", head)).toBe("m");
  });

  it("handles disk images and empty content like the reference", () => {
    expect(resolveIcon("x.img", new Uint8Array())).toBe("img-disk");
    expect(resolveIcon("x.img", hexToBytes("89504e47"))).toBe("img");
    const vhd = new Uint8Array(1024);
    vhd.set(new TextEncoder().encode("conectix"), 512);
    expect(resolveIcon("x.vhd", vhd)).toBe("vhd");
  });
});

describe("render helpers", () => {
  it("escapes", () => {
    expect(escapeXml(`<a href="x">&'</a>`)).toBe("&lt;a href=&quot;x&quot;&gt;&amp;&#39;&lt;/a&gt;");
  });

  it("builds svg attributes", () => {
    expect(svgAttributes()).toEqual({
      xmlns: "http://www.w3.org/2000/svg",
      width: "40",
      height: "40",
      viewBox: "0 0 40 40",
      fill: "none",
      "aria-hidden": "true",
    });
    expect(svgAttributes({ size: 24, title: "x" })).toMatchObject({ width: "24", role: "img" });
  });

  it("encodes data URIs", () => {
    expect(toDataUri("<svg/>")).toBe("data:image/svg+xml,%3Csvg%2F%3E");
  });

  it("has a theme table with the documented outline colors", () => {
    const rules = Object.values(THEME_TABLE).map((rule) => rule.join(" "));
    expect(rules).toContain("stroke #D5D7DA #3F3F46");
  });
});

describe("assets", () => {
  it("ships the pack manifest unchanged", () => {
    const shipped = readFileSync(new URL("../dist/manifest.json", import.meta.url));
    expect(shipped.equals(readFileSync(`${PACK_DIR}manifest.json`))).toBe(true);
  });
});
