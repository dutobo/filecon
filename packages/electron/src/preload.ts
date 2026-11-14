// Preload bridge: exposes a small, typed API to the renderer via contextBridge (works with contextIsolation).
import { contextBridge, ipcRenderer } from "electron";
import { DEFAULT_API_KEY, FILECON_CHANNELS } from "./channels";
import type { FileconRendererApi, FileIconResult, IconOptions } from "./types";

export type { FileconRendererApi };

/** Creates the renderer API on top of `ipcRenderer.invoke`. */
export function createFileconApi(
  invoke: (channel: string, ...args: unknown[]) => Promise<unknown>,
): FileconRendererApi {
  return {
    iconForPath: (path: string, options?: IconOptions) =>
      invoke(FILECON_CHANNELS.iconForPath, path, options) as Promise<FileIconResult>,
    getIcon: (name: string, options?: IconOptions) =>
      invoke(FILECON_CHANNELS.getIcon, name, options) as Promise<string>,
  };
}

/**
 * Exposes the API as `window[key]` (default `window.filecon`). Call it from your preload script:
 *
 * ```ts
 * import { exposeFileconApi } from "@filecon/electron/preload";
 * exposeFileconApi();
 * ```
 */
export function exposeFileconApi(key: string = DEFAULT_API_KEY): void {
  contextBridge.exposeInMainWorld(
    key,
    createFileconApi((channel, ...args) => ipcRenderer.invoke(channel, ...args)),
  );
}
