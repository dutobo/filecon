import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

export default defineTemplate({
  id: "react-native",
  title: "React Native",
  packageJson: (ctx) => ({
    description: `Filecon file icons for React Native – ${ctx.vars.styleLabel}. Rendered with react-native-svg, tree-shakable.`,
    keywords: ["react-native", "react-native-svg", "expo"],
    entries: ["index", "icons"],
    dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^" },
    peerDependencies: { react: ">=18", "react-native": ">=0.72", "react-native-svg": ">=13" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      "@types/react": "^19.3.0",
      react: "^19.3.1",
      "react-native": "^0.88.1",
      "react-native-svg": "^15.16.1",
      tsup: VERSIONS.tsup,
      vitest: VERSIONS.vitest,
    },
    extra: { "react-native": "./dist/index.js" },
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
