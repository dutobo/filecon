import { VERSIONS } from "../../codegen/src/config";
import { dataModule } from "../../codegen/src/data-module";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

/** Framework-free package. Also the data provider for every other framework package (`/data` entry). */
export default defineTemplate({
  id: "js",
  title: "JavaScript",
  packageJson: (ctx) => ({
    description: `Filecon file icons as SVG strings – ${ctx.vars.styleLabel}. Framework-free, tree-shakable.`,
    keywords: ["svg-string", "vanilla-js"],
    entries: ["index", "icons", "data"],
    dependencies: { "@filecon/shared": "workspace:^" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      tsup: VERSIONS.tsup,
      vitest: VERSIONS.vitest,
    },
    scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
  }),
  generate: (ctx) => ({
    "src/generated/data.ts": dataModule(ctx),
    "src/generated/icons.ts": [
      GENERATED_HEADER,
      'import { createIconFunction } from "../icon-function";',
      dataImportStatement(ctx),
      ...ctx.icons.map(
        (icon) => `export const ${icon.componentName} = /*#__PURE__*/ createIconFunction(${icon.dataId});`,
      ),
      "",
    ].join("\n"),
  }),
});
