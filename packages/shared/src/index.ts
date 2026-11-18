export type { IconName } from "./generated/names";
export { iconNames } from "./generated/names";
export { iconComponentName } from "./names";
export {
  type AttributeOptions,
  type AttributeValue,
  availableStyle,
  type ContentOptions,
  DEFAULT_SIZE,
  escapeXml,
  iconContent,
  iconMarkup,
  type RenderOptions,
  renderSvg,
  SVG_NAMESPACE,
  type SvgAttributes,
  serializeAttributes,
  svgAttributes,
  toDataUri,
  VIEW_BOX,
} from "./render";
export { isIconName, resolveIcon, toIconName } from "./resolve";
export { autoMarkup, darkMarkup, lightMarkup, THEME_TABLE } from "./theme";
export type { ThemeRule, ThemeTable } from "./theme-core";
export { type IconData, isThemedStyle, STYLES, type Style, THEMELESS_STYLES, THEMES, type Theme } from "./types";
