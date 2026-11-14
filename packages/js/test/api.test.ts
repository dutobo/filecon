import { hexToBytes, ICON_NAMES, resolveCases } from "@filecon/testkit";
import { describe, expect, it } from "vitest";
import { getFileIcon, getIcon, iconNames, resolveIcon, toDataUri } from "../src/index";

describe("js api", () => {
  it("exposes all icon names", () => {
    expect([...iconNames]).toEqual(ICON_NAMES);
  });

  it("resolves the pack's test cases", () => {
    for (const c of resolveCases) expect(resolveIcon(c.file, hexToBytes(c.content_hex)), c.file).toBe(c.expected);
  });

  it("renders unknown names as the empty icon", () => {
    expect(getIcon("does-not-exist")).toBe(getIcon("empty"));
    expect(getIcon(".PDF")).toBe(getIcon("pdf"));
  });

  it("uses magic bytes when head is given", () => {
    const sqlite = new TextEncoder().encode("SQLite format 3\u0000");
    expect(getFileIcon("app.db", { head: sqlite })).toBe(getIcon("db-sqlite"));
  });

  it("creates data URIs", () => {
    const uri = toDataUri(getIcon("pdf"));
    expect(uri.startsWith("data:image/svg+xml,")).toBe(true);
    expect(decodeURIComponent(uri.slice("data:image/svg+xml,".length))).toBe(getIcon("pdf"));
  });
});
