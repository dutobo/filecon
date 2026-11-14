// Main-process helpers. Reads at most 1 KB of a file for magic-byte detection; never more.
import { closeSync, openSync, readSync, statSync } from "node:fs";
import { open, stat } from "node:fs/promises";
import { getIcon } from "@filecon/js";
import { resolveIcon } from "@filecon/shared";
import { FILECON_CHANNELS } from "./channels";
import type { FileIconResult, IconOptions } from "./types";

export type { FileIconResult, IconOptions };
export { FILECON_CHANNELS };

const HEAD_SIZE = 1024;

/**
 * First bytes of a file like the reference resolver: `undefined` if the path does not exist (name-only
 * resolution), an empty buffer if it exists but cannot be read (e.g. a directory).
 */
async function readHead(path: string): Promise<Uint8Array | undefined> {
  try {
    await stat(path);
  } catch {
    return undefined;
  }
  try {
    const handle = await open(path, "r");
    try {
      const buffer = new Uint8Array(HEAD_SIZE);
      const { bytesRead } = await handle.read(buffer, 0, HEAD_SIZE, 0);
      return buffer.subarray(0, bytesRead);
    } finally {
      await handle.close();
    }
  } catch {
    return new Uint8Array();
  }
}

function readHeadSync(path: string): Uint8Array | undefined {
  try {
    statSync(path);
  } catch {
    return undefined;
  }
  let fd: number | undefined;
  try {
    fd = openSync(path, "r");
    const buffer = new Uint8Array(HEAD_SIZE);
    const bytesRead = readSync(fd, buffer, 0, HEAD_SIZE, 0);
    return buffer.subarray(0, bytesRead);
  } catch {
    return new Uint8Array();
  } finally {
    if (fd !== undefined) closeSync(fd);
  }
}

/** Icon for a file on disk: file name, then magic bytes (first 1 KB), then extension. */
export async function iconForPath(path: string, options: IconOptions = {}): Promise<FileIconResult> {
  const name = resolveIcon(path, await readHead(path));
  return { name, svg: getIcon(name, options) };
}

/** Synchronous variant of `iconForPath`. */
export function iconForPathSync(path: string, options: IconOptions = {}): FileIconResult {
  const name = resolveIcon(path, readHeadSync(path));
  return { name, svg: getIcon(name, options) };
}

/** The subset of Electron's `ipcMain` used here (keeps the package free of a hard electron import). */
export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
  removeHandler(channel: string): void;
}

export interface RegisterOptions {
  /**
   * Called before a renderer may read the head of `path`. Return `false` to deny (the icon is then resolved
   * from the file name only). Use it to restrict access to directories the renderer is allowed to show.
   */
  allowPath?: (path: string) => boolean;
}

/**
 * Registers the IPC handlers used by the preload bridge. Returns a function that removes them again.
 *
 * ```ts
 * import { ipcMain } from "electron";
 * import { registerFileconIpc } from "@filecon/electron/main";
 * registerFileconIpc(ipcMain);
 * ```
 */
export function registerFileconIpc(ipcMain: IpcMainLike, options: RegisterOptions = {}): () => void {
  ipcMain.handle(FILECON_CHANNELS.iconForPath, async (_event, path, iconOptions) => {
    if (typeof path !== "string") throw new TypeError("filecon: path must be a string");
    const opts = (iconOptions ?? {}) as IconOptions;
    if (options.allowPath && !options.allowPath(path)) {
      const name = resolveIcon(path);
      return { name, svg: getIcon(name, opts) } satisfies FileIconResult;
    }
    return iconForPath(path, opts);
  });
  ipcMain.handle(FILECON_CHANNELS.getIcon, (_event, name, iconOptions) => {
    if (typeof name !== "string") throw new TypeError("filecon: name must be a string");
    return getIcon(name, (iconOptions ?? {}) as IconOptions);
  });
  return () => {
    ipcMain.removeHandler(FILECON_CHANNELS.iconForPath);
    ipcMain.removeHandler(FILECON_CHANNELS.getIcon);
  };
}
