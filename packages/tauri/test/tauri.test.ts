import { clearMocks, mockIPC } from "@tauri-apps/api/mocks";
import { afterEach, describe, expect, it } from "vitest";
import { getIcon, iconForPath, resolveIcon } from "../src/index";

const calls: { cmd: string; args: unknown }[] = [];

function mockPlugin(): void {
  mockIPC((cmd, args) => {
    calls.push({ cmd, args });
    if (cmd === "plugin:filecon|resolve") return "pdf";
    if (cmd === "plugin:filecon|icon") return "<svg/>";
    if (cmd === "plugin:filecon|icon_for_path") return { name: "db-sqlite", svg: "<svg/>" };
    throw new Error(`unexpected command ${cmd}`);
  });
}

afterEach(() => {
  clearMocks();
  calls.length = 0;
});

describe("@filecon/tauri", () => {
  it("invokes the plugin commands with camelCase arguments", async () => {
    mockPlugin();
    expect(await resolveIcon("report.pdf")).toBe("pdf");
    expect(await getIcon("pdf", { style: "solid" })).toBe("<svg/>");
    expect(await iconForPath("/tmp/app.db", { theme: "dark" })).toEqual({ name: "db-sqlite", svg: "<svg/>" });
    expect(calls).toEqual([
      { cmd: "plugin:filecon|resolve", args: { fileName: "report.pdf" } },
      { cmd: "plugin:filecon|icon", args: { name: "pdf", style: "solid", theme: null } },
      { cmd: "plugin:filecon|icon_for_path", args: { path: "/tmp/app.db", style: null, theme: "dark" } },
    ]);
  });
});
