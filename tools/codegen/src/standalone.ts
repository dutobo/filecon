// Hand-written packages (not template based). Their package.json is still composed here so that
// metadata (license, author, publishConfig, ...) is identical across all packages.
import { VERSIONS } from "./config";
import type { Pack } from "./pack";
import { tsupExports } from "./package-json";
import type { PackageJsonParts } from "./template-api";

export interface StandalonePackage {
  dirName: string;
  parts: PackageJsonParts;
}

export function standalonePackages(pack: Pack): StandalonePackage[] {
  return [
    {
      dirName: "shared",
      parts: {
        description: `Filecon core: ${pack.icons.length} file icon SVGs in three styles, manifest, types and the file-type resolver.`,
        keywords: ["file-type", "magic-bytes", "resolver"],
        exports: {
          ...tsupExports(["index"]),
          "./manifest.json": "./dist/manifest.json",
          "./svg/*": "./dist/svg/*",
        },
        scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
        devDependencies: {
          "@filecon/testkit": "workspace:*",
          "@types/node": VERSIONS.nodeTypes,
          tsup: VERSIONS.tsup,
          vitest: VERSIONS.vitest,
        },
      },
    },
    {
      dirName: "electron",
      parts: {
        description:
          "Filecon helpers for Electron: iconForPath() in the main process, IPC handlers and a typed preload bridge.",
        keywords: ["electron", "ipc", "preload", "contextBridge"],
        entries: ["index", "main", "preload", "renderer"],
        dependencies: { "@filecon/js": "workspace:^", "@filecon/shared": "workspace:^" },
        peerDependencies: { electron: ">=28" },
        peerDependenciesMeta: { electron: { optional: true } },
        devDependencies: {
          "@filecon/testkit": "workspace:*",
          "@types/node": VERSIONS.nodeTypes,
          electron: "^45.3.2",
          tsup: VERSIONS.tsup,
          vitest: VERSIONS.vitest,
        },
        scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
      },
    },
    {
      dirName: "tauri",
      parts: {
        description:
          "Filecon for Tauri 2: JavaScript binding of tauri-plugin-filecon (iconForPath, getIcon, resolveIcon) for desktop, iOS and Android.",
        keywords: ["tauri", "tauri-plugin", "desktop", "mobile"],
        entries: ["index"],
        peerDependencies: { "@tauri-apps/api": "^2.0.0" },
        devDependencies: {
          "@tauri-apps/api": "^2.12.5",
          "@types/node": VERSIONS.nodeTypes,
          jsdom: "^31.0.1",
          tsup: VERSIONS.tsup,
          vitest: VERSIONS.vitest,
        },
        scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
      },
    },
    {
      dirName: "iconify",
      parts: {
        description: `Filecon file icons as Iconify JSON icon sets (${pack.icons.length} icons; default, gray and solid, light and dark) for UnoCSS, unplugin-icons, Iconify and Tailwind.`,
        keywords: ["iconify", "iconify-json", "unocss", "unplugin-icons", "tailwind"],
        exports: {
          ".": {
            import: { types: "./dist/index.d.ts", default: "./dist/index.js" },
            require: { types: "./dist/index.d.cts", default: "./dist/index.cjs" },
          },
          "./*.json": "./dist/*.json",
          "./*": {
            import: { types: "./dist/set.d.ts", default: "./dist/*.js" },
            require: { types: "./dist/set.d.cts", default: "./dist/*.cjs" },
          },
          "./package.json": "./package.json",
        },
        scripts: { build: "node scripts/build.mjs", typecheck: "tsc --noEmit", test: "vitest run" },
        devDependencies: {
          "@filecon/testkit": "workspace:*",
          "@iconify/utils": "^3.1.0",
          "@types/node": VERSIONS.nodeTypes,
          vitest: VERSIONS.vitest,
        },
      },
    },
    {
      dirName: "css",
      parts: {
        description: `Filecon file icons as CSS classes (${pack.icons.length} icons, data-URI backgrounds; default, gray and solid, light/dark/auto). No JavaScript needed.`,
        keywords: ["css", "css-icons", "background-image", "data-uri"],
        exports: {
          ".": "./dist/default.css",
          "./*.css": "./dist/*.css",
          "./package.json": "./package.json",
        },
        extra: { style: "./dist/default.css", sideEffects: ["*.css"] },
        scripts: { build: "node scripts/build.mjs", typecheck: "tsc --noEmit", test: "vitest run" },
        devDependencies: {
          "@filecon/testkit": "workspace:*",
          "@types/node": VERSIONS.nodeTypes,
          vitest: VERSIONS.vitest,
        },
      },
    },
  ];
}
