/** IPC channel names used between main process and preload. */
export const FILECON_CHANNELS = {
  iconForPath: "filecon:icon-for-path",
  getIcon: "filecon:get-icon",
} as const;

/** Default key under which the preload bridge exposes the API (`window.filecon`). */
export const DEFAULT_API_KEY = "filecon";
