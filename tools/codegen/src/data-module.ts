import type { Style } from "../../../packages/shared/src/types";
import { GENERATED_HEADER, type TemplateContext } from "./template-api";

/** JS string literal; prefers single quotes because the markup is full of double quotes. */
export function stringLiteral(value: string): string {
  const lineBreaks = ["\n", "\r", String.fromCharCode(0x2028), String.fromCharCode(0x2029)];
  if (lineBreaks.some((char) => value.includes(char))) return JSON.stringify(value);
  return `'${value.replace(/\\/g, "\\\\").replace(/'/g, "\\'")}'`;
}

/** Object key: bare when it is an identifier (`default`), quoted otherwise (`"papered-flat"`). */
const propertyKey = (key: string): string => (/^[A-Za-z_$][\w$]*$/.test(key) ? key : JSON.stringify(key));

/** `src/generated/data.ts`: one constant per icon (inner markup of the package's styles) plus the lookup map. */
export function dataModule(ctx: TemplateContext): string {
  const lines: string[] = [GENERATED_HEADER, 'import type { IconData, IconName } from "@filecon/shared";\n'];
  for (const icon of ctx.icons) {
    const fields = ctx.styles
      .map((style: Style) => `${propertyKey(style)}: ${stringLiteral(icon.data[style])}`)
      .join(", ");
    lines.push(`export const ${icon.dataId}: IconData = { ${fields} };`);
  }
  lines.push("", "/** Lookup map: icon name -> data. Import single constants instead when bundle size matters. */");
  lines.push("export const iconData: Readonly<Record<IconName, IconData>> = {");
  for (const icon of ctx.icons) lines.push(`  ${JSON.stringify(icon.name)}: ${icon.dataId},`);
  lines.push("};", "");
  return lines.join("\n");
}

/** `src/generated/variant.ts`: which styles this package contains and where its data lives. */
export function variantModule(ctx: TemplateContext): string {
  const single = ctx.fixedStyle !== null;
  return `${GENERATED_HEADER}import type { Style } from "@filecon/shared";

/** Package name. */
export const PACKAGE_NAME = ${JSON.stringify(ctx.packageName)};
/** ${single ? `Single-style package: always renders the "${ctx.fixedStyle}" style.` : "All styles; chosen per icon via the style option."} */
export const FIXED_STYLE: Style | null = ${single ? JSON.stringify(ctx.fixedStyle) : "null"};
/** Styles contained in this package. */
export const STYLES: readonly Style[] = ${JSON.stringify(ctx.styles)};
/** \`true\` when the package offers the \`style\` option. */
export type MultiStyle = ${single ? "false" : "true"};
/** Style option of this package (absent in single-style packages). */
// biome-ignore lint/complexity/noBannedTypes: intentionally empty for single-style packages
export type StyleOption = ${single ? "{}" : "{ style?: Style | undefined }"};

export { iconData } from "${ctx.dataImport}";
`;
}
