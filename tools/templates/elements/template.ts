import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

/** Framework-free Web Components (custom elements, light DOM, SSR-safe import). */
export default defineTemplate({
  id: "elements",
  title: "Web Components",
  packageJson: (ctx) => ({
    description: `Filecon file icons as Web Components (<filecon-icon>) – ${ctx.vars.styleLabel}. Works with any framework or plain HTML.`,
    keywords: ["web-components", "custom-elements", "html", "lit", "htmx"],
    entries: ["index", "icons", "define"],
    dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      jsdom: "^31.0.1",
      tsup: VERSIONS.tsup,
      vitest: VERSIONS.vitest,
    },
    scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
    // `define` registers <filecon-icon> when imported; everything else is side-effect free.
    extra: { sideEffects: ["./dist/define.js", "./dist/define.cjs"] },
  }),
  generate: (ctx) => ({
    "src/generated/icons.ts": [
      GENERATED_HEADER,
      'import { createIconElement } from "../element";',
      dataImportStatement(ctx),
      ...ctx.icons.map(
        (icon) =>
          `export const ${icon.componentName} = /*#__PURE__*/ createIconElement(${JSON.stringify(icon.name)}, ${icon.dataId});`,
      ),
      "",
    ].join("\n"),
  }),
});
