/** `[attribute, light value, dark value]` for one theme class. */
export type ThemeRule = readonly [attribute: string, light: string, dark: string];
export type ThemeTable = Readonly<Record<string, ThemeRule>>;

export const THEME_CLASS_PREFIX = "fc-t";
const CLASS_ATTR = / class="(fc-t\d+(?: fc-t\d+)*)"/g;
const CLASSED_TAG = /<([^<>]*?) class="(fc-t\d+(?: fc-t\d+)*)"(\/?)>/g;

/** Light markup = themed markup without the theme classes. */
export function toLightMarkup(themed: string): string {
  return themed.replace(CLASS_ATTR, "");
}

/** Dark markup = themed markup with every classed attribute switched to its dark value. */
export function toDarkMarkup(themed: string, table: ThemeTable): string {
  return themed.replace(CLASSED_TAG, (_match, body: string, classes: string, slash: string) => {
    let tag = body;
    for (const cls of classes.split(" ")) {
      const rule = table[cls];
      if (rule) tag = tag.replace(` ${rule[0]}="${rule[1]}"`, ` ${rule[0]}="${rule[2]}"`);
    }
    return `<${tag}${slash}>`;
  });
}

/** CSS that switches the used classes to their dark values under `prefers-color-scheme: dark`. */
export function themeStyleSheet(themed: string, table: ThemeTable): string {
  const used = new Set<string>();
  for (const match of themed.matchAll(CLASS_ATTR)) {
    for (const cls of (match[1] ?? "").split(" ")) used.add(cls);
  }
  if (used.size === 0) return "";
  let rules = "";
  for (const cls of [...used].sort()) {
    const rule = table[cls];
    if (rule) rules += `.${cls}{${rule[0]}:${rule[2]}}`;
  }
  return `@media (prefers-color-scheme: dark){${rules}}`;
}

/** Auto markup = light colors as attributes, dark colors via an embedded media query. */
export function toAutoMarkup(themed: string, table: ThemeTable): string {
  const css = themeStyleSheet(themed, table);
  return css ? `<style>${css}</style>${themed}` : themed;
}
