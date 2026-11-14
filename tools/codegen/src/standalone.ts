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
  ];
}
