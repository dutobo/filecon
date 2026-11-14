import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { normalizeSvg, sourceSvg } from "@filecon/testkit";
import { afterEach, describe, expect, it, vi } from "vitest";
import { FILECON_CHANNELS, iconForPath, iconForPathSync, registerFileconIpc } from "../src/main";

const electron = vi.hoisted(() => ({
  exposed: new Map<string, unknown>(),
  invoke: vi.fn(async (..._args: unknown[]) => "ok"),
}));
vi.mock("electron", () => ({
  contextBridge: { exposeInMainWorld: (key: string, api: unknown) => electron.exposed.set(key, api) },
  ipcRenderer: { invoke: electron.invoke },
}));

const dir = mkdtempSync(join(tmpdir(), "filecon-electron-"));
const file = (name: string, content: Uint8Array | string) => {
  const path = join(dir, name);
  writeFileSync(path, content);
  return path;
};

describe("main process", () => {
  it("resolves by magic bytes and renders the SVG", async () => {
    const result = await iconForPath(file("app.db", "SQLite format 3\u0000 rest"));
    expect(result.name).toBe("db-sqlite");
    expect(normalizeSvg(result.svg)).toBe(normalizeSvg(sourceSvg("default", "light", "db-sqlite")));
    expect(iconForPathSync(join(dir, "app.db")).name).toBe("db-sqlite");
  });

  it("passes icon options through", async () => {
    const { svg } = await iconForPath(file("report.pdf", "%PDF-1.7"), { style: "solid", size: 24 });
    expect(normalizeSvg(svg)).toBe(normalizeSvg(sourceSvg("solid", "light", "pdf")));
    expect(svg).toContain('width="24"');
  });

  it("falls back to the file name for missing files and directories", async () => {
    expect((await iconForPath(join(dir, "missing.ts"))).name).toBe("ts");
    mkdirSync(join(dir, "folder.ts"));
    expect((await iconForPath(join(dir, "folder.ts"))).name).toBe("ts");
    expect(iconForPathSync(join(dir, "missing.png")).name).toBe("png");
  });

  it("reads at most 1 KB", async () => {
    const content = new Uint8Array(4096).fill(0x20);
    content.set(new TextEncoder().encode("#import"), 2000);
    expect((await iconForPath(file("late.m", content))).name).toBe("m");
    expect(iconForPathSync(join(dir, "late.m")).name).toBe("m");
  });
});

describe("ipc", () => {
  const handlers = new Map<string, (event: unknown, ...args: unknown[]) => unknown>();
  const ipcMain = {
    handle: (channel: string, listener: (event: unknown, ...args: unknown[]) => unknown) =>
      handlers.set(channel, listener),
    removeHandler: (channel: string) => handlers.delete(channel),
  };
  afterEach(() => handlers.clear());

  it("registers and removes the handlers", async () => {
    const dispose = registerFileconIpc(ipcMain);
    expect([...handlers.keys()].sort()).toEqual(Object.values(FILECON_CHANNELS).sort());
    const result = (await handlers.get(FILECON_CHANNELS.iconForPath)?.({}, join(dir, "app.db"))) as { name: string };
    expect(result.name).toBe("db-sqlite");
    expect(await handlers.get(FILECON_CHANNELS.getIcon)?.({}, "pdf", { theme: "dark" })).toContain("<svg");
    dispose();
    expect(handlers.size).toBe(0);
  });

  it("does not read files outside allowPath", async () => {
    registerFileconIpc(ipcMain, { allowPath: () => false });
    const result = (await handlers.get(FILECON_CHANNELS.iconForPath)?.({}, join(dir, "app.db"))) as { name: string };
    expect(result.name).toBe("db");
  });

  it("validates arguments", async () => {
    registerFileconIpc(ipcMain);
    await expect(async () => handlers.get(FILECON_CHANNELS.iconForPath)?.({}, 42)).rejects.toThrow(TypeError);
  });
});

describe("preload and renderer", () => {
  it("exposes a typed API that invokes the channels", async () => {
    const { exposeFileconApi } = await import("../src/preload");
    exposeFileconApi();
    const api = electron.exposed.get("filecon") as import("../src/types").FileconRendererApi;
    await api.iconForPath("/tmp/a.pdf", { style: "gray" });
    await api.getIcon("pdf");
    expect(electron.invoke).toHaveBeenCalledWith(FILECON_CHANNELS.iconForPath, "/tmp/a.pdf", { style: "gray" });
    expect(electron.invoke).toHaveBeenCalledWith(FILECON_CHANNELS.getIcon, "pdf", undefined);
  });

  it("gives typed access in the renderer", async () => {
    const { fileconApi } = await import("../src/renderer");
    expect(() => fileconApi("nope")).toThrow(/exposeFileconApi/);
    const api = { iconForPath: vi.fn(), getIcon: vi.fn() };
    (globalThis as Record<string, unknown>).filecon = api;
    expect(fileconApi()).toBe(api);
  });
});
