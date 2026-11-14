import { THEME_TABLE } from "./generated/theme";
import { toAutoMarkup, toDarkMarkup, toLightMarkup } from "./theme-core";

export { THEME_TABLE };

/** Light variant of themed markup. */
export const lightMarkup = (themed: string): string => toLightMarkup(themed);
/** Dark variant of themed markup. */
export const darkMarkup = (themed: string): string => toDarkMarkup(themed, THEME_TABLE);
/** `prefers-color-scheme` aware variant of themed markup (embeds a `<style>`). */
export const autoMarkup = (themed: string): string => toAutoMarkup(themed, THEME_TABLE);
