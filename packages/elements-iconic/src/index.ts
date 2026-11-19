export type { IconData, IconName, Style, Theme } from "@filecon/shared";
export { iconComponentName, iconNames, isIconName, resolveIcon, toIconName } from "@filecon/shared";
export {
  createIconElement,
  defineIcons,
  FileconElementBase,
  ICON_ATTRIBUTES,
  type IconElementClass,
} from "./element";
export { defineFileconIcon, FILECON_ICON_TAG, FileconIconElement } from "./file-icon";
export { FIXED_STYLE, STYLES } from "./generated/variant";
