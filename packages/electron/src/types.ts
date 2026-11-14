import type { IconOptions } from "@filecon/js";
import type { IconName } from "@filecon/shared";

export type { IconOptions };

/** Result of `iconForPath`: the resolved icon name and the rendered SVG. */
export interface FileIconResult {
  name: IconName;
  svg: string;
}

/** API exposed to the renderer by `exposeFileconApi()` (default: `window.filecon`). */
export interface FileconRendererApi {
  /** Resolves the icon for a file on disk (reads at most 1 KB in the main process). */
  iconForPath(path: string, options?: IconOptions): Promise<FileIconResult>;
  /** Renders an icon by name/extension in the main process. */
  getIcon(name: string, options?: IconOptions): Promise<string>;
}
