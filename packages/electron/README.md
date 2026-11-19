# @filecon/electron

[Filecon](https://filecon.dev) helpers for Electron: resolve icons for files on disk in the main process
(reading at most 1 KB for magic-byte detection), IPC handlers and a typed `contextBridge` preload API.
Render icons in the renderer with `@filecon/js` or a framework package.

![The same file icons in all nine Filecon styles, light and dark](https://raw.githubusercontent.com/dutobo/filecon/main/docs/previews/styles.png)

More previews (a grid and a category overview per style): [docs/previews](https://github.com/dutobo/filecon/tree/main/docs/previews#readme).

```sh
npm install @filecon/electron
```

## Main process

```ts
import { app, ipcMain } from "electron";
import { iconForPath, registerFileconIpc } from "@filecon/electron/main";

const { name, svg } = await iconForPath("/data/app.db");          // { name: "db-sqlite", svg: "<svg …>" }
const dark = await iconForPath("/data/clip.ts", { theme: "dark" }); // MPEG-TS vs. TypeScript by content

// Expose to renderers (optionally restrict which paths may be read):
const dispose = registerFileconIpc(ipcMain, { allowPath: (path) => path.startsWith(app.getPath("documents")) });
```

`iconForPathSync` is the synchronous variant. Missing files resolve by name only; unreadable entries (e.g.
directories) resolve like an empty file – exactly like the reference resolver.

## Preload

```ts
// preload.ts (bundle it if your window uses sandbox: true)
import { exposeFileconApi } from "@filecon/electron/preload";

exposeFileconApi(); // window.filecon
```

## Renderer

```ts
import { fileconApi } from "@filecon/electron/renderer";

const { name, svg } = await fileconApi().iconForPath(file.path, { style: "gray", theme: "auto" });
element.innerHTML = svg;
```

```tsx
// or render in the renderer with a framework package:
import { FileIcon } from "@filecon/react";
const { name } = await fileconApi().iconForPath(path);
<FileIcon name={name} theme="auto" />;
```

## API

| Entry | Exports |
|---|---|
| `@filecon/electron/main` | `iconForPath(path, options?)`, `iconForPathSync`, `registerFileconIpc(ipcMain, { allowPath? })`, `FILECON_CHANNELS` |
| `@filecon/electron/preload` | `exposeFileconApi(key = "filecon")`, `createFileconApi(invoke)` |
| `@filecon/electron/renderer` | `fileconApi(key = "filecon")`, `FileconRendererApi` type, `window.filecon` typing |
| `@filecon/electron` | channel names and types |

`options` are the `@filecon/js` options: `style`, `theme`, `size`, `title`, `className`, `attributes`.

## Security

- The renderer never gets file contents, only the icon name and SVG.
- Arguments are validated in the IPC handlers; use `allowPath` to limit which files may be read.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
