import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

export default defineTemplate({
  id: "preact",
  title: "Preact",
  packageJson: (ctx) => ({
    description: `Filecon file icons for Preact – ${ctx.vars.styleLabel}. SSR-safe, tree-shakable.`,
    keywords: ["preact", "preact-component"],
    entries: ["index", "icons"],
    dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^" },
    peerDependencies: { preact: "^10.19.0 || ^11.0.0" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      preact: "^11.2.0",
      "preact-render-to-string": "^6.8.3",
      tsup: VERSIONS.tsup,
      vitest: VERSIONS.vitest,
    },
    scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
  }),
  generate: (ctx) => ({
    "src/generated/icons.ts": [
      GENERATED_HEADER,
      'import { createIcon } from "../file-icon";',
      dataImportStatement(ctx),
      ...ctx.icons.map(
        (icon) =>
          `export const ${icon.componentName} = /*#__PURE__*/ createIcon(${JSON.stringify(icon.name)}, ${icon.dataId});`,
      ),
      "",
    ].join("\n"),
  }),
});
