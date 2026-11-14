// Renderer side: typed access to the API exposed by the preload bridge. Render icons with
// `@filecon/js` or a framework package (`@filecon/react`, `@filecon/vue`, ...) – no Node access needed.
import { DEFAULT_API_KEY } from "./channels";
import type { FileconRendererApi } from "./types";

export type { FileconRendererApi, FileIconResult, IconOptions } from "./types";

declare global {
  interface Window {
    filecon?: FileconRendererApi;
  }
}

/** The API exposed by `exposeFileconApi(key)`. Throws if the preload bridge was not installed. */
export function fileconApi(key: string = DEFAULT_API_KEY): FileconRendererApi {
  const api = (globalThis as unknown as Record<string, FileconRendererApi | undefined>)[key];
  if (!api) throw new Error(`filecon: window.${key} is missing – call exposeFileconApi() in your preload script`);
  return api;
}
