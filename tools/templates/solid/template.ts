import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

export default defineTemplate({
  id: "solid",
  title: "Solid",
  packageJson: (ctx) => ({
    description: `Filecon file icons for SolidJS – ${ctx.vars.styleLabel}. SSR-safe, tree-shakable.`,
    keywords: ["solid", "solidjs", "solid-component"],
    entries: ["index", "icons"],
    dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^" },
    peerDependencies: { "solid-js": "^1.8.0" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      "solid-js": "^1.9.19",
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
