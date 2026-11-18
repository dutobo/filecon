import { VERSIONS } from "../../codegen/src/config";
import { dataImportStatement, defineTemplate, GENERATED_HEADER } from "../../codegen/src/template-api";

export default defineTemplate({
  id: "vue",
  title: "Vue",
  packageJson: (ctx) => ({
    description: `Filecon file icons for Vue 3 – ${ctx.vars.styleLabel}. SSR-safe, tree-shakable, no SFC build step.`,
    keywords: ["vue", "vue3", "vue-component"],
    entries: ["index", "icons"],
    dependencies: { "@filecon/shared": "workspace:^", [ctx.dataPackage]: "workspace:^" },
    peerDependencies: { vue: "^3.3.0" },
    devDependencies: {
      "@filecon/testkit": "workspace:*",
      "@types/node": VERSIONS.nodeTypes,
      tsup: VERSIONS.tsup,
      vitest: VERSIONS.vitest,
      vue: "^3.5.45",
    },
    scripts: { build: "tsup", typecheck: "tsc --noEmit", test: "vitest run" },
  }),
  generate: (ctx) => ({
    // Vue reserves `style` (it is parsed as inline CSS), so the all-styles package uses `iconStyle` / `icon-style`.
    "src/generated/style-props.ts":
      ctx.fixedStyle === null
        ? `${GENERATED_HEADER}import type { Style } from "@filecon/shared";
import type { PropType } from "vue";

export const styleProps = {
  /** Icon style, e.g. \`default\`, \`gray\`, \`solid\`, \`papered\` or \`scratch\` (template: \`icon-style="solid"\`). */
  iconStyle: { type: String as PropType<Style>, default: "default" },
} as const;
`
        : `${GENERATED_HEADER}export const styleProps = {} as const;\n`,
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
