import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

export default defineTemplate({
  id: "react",
  title: "React",
  packageJson: (ctx) => ({
    description: `Filecon file icons for React – ${ctx.vars.styleLabel}. SSR-safe, tree-shakable.`,
    keywords: ["react", "react-component"],
    entries: ["index", "icons"],
    dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^" },
    peerDependencies: { react: ">=18" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      "@types/react": "^19.3.0",
      "@types/react-dom": "^19.3.0",
      react: "^19.3.1",
      "react-dom": "^19.3.1",
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
