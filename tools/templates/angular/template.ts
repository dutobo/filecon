import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

const ANGULAR = "^22.2.6";

/** Standalone Angular component `<filecon-icon>`, built with ng-packagr (partial compilation, FESM). */
export default defineTemplate({
  id: "angular",
  title: "Angular",
  packageJson: (ctx) => {
    const base = ctx.packageName.replace("@", "").replace("/", "-");
    const bundle = `./dist/fesm2022/${base}.mjs`;
    const types = `./dist/types/${base}.d.ts`;
    const entry = { types, default: bundle };
    return {
      description: `Filecon file icons for Angular – ${ctx.vars.styleLabel}. Standalone component, SSR-safe.`,
      keywords: ["angular", "angular-component", "standalone"],
      exports: { ".": entry, "./icons": entry, "./package.json": "./package.json" },
      extra: { module: bundle, typings: types },
      dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^", tslib: "^2.9.1" },
      peerDependencies: {
        "@angular/core": "^20.0.0 || ^21.0.0 || ^22.0.0",
        "@angular/platform-browser": "^20.0.0 || ^21.0.0 || ^22.0.0",
      },
      devDependencies: {
        "@angular/common": ANGULAR,
        "@angular/compiler": ANGULAR,
        "@angular/compiler-cli": ANGULAR,
        "@angular/core": ANGULAR,
        "@angular/platform-browser": ANGULAR,
        "@filecon/testkit": "workspace:*",
        "@types/node": VERSIONS.nodeTypes,
        jsdom: "^31.0.1",
        "ng-packagr": ANGULAR,
        rxjs: "^7.8.2",
        vitest: VERSIONS.vitest,
      },
      scripts: {
        // ng-packagr writes a dist/package.json for publishing dist/ directly; we publish the package root instead.
        build:
          "ng-packagr -p ng-package.json -c tsconfig.lib.json && node -e \"require('node:fs').rmSync('dist/package.json')\"",
        typecheck: "tsc --noEmit",
        test: "vitest run",
      },
    };
  },
  generate: (ctx) => ({
    "src/generated/icons.ts": [
      GENERATED_HEADER,
      'import type { FileconIcon } from "../icon-def";',
      dataImportStatement(ctx),
      ...ctx.icons.map(
        (icon) =>
          `export const ${icon.componentName}: FileconIcon = { name: ${JSON.stringify(icon.name)}, data: ${icon.dataId} };`,
      ),
      "",
    ].join("\n"),
  }),
});
