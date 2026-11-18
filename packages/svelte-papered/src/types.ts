import type { IconName, Theme } from "@filecon/shared";
import type { SVGAttributes } from "svelte/elements";
import type { MultiStyle, StyleOption } from "./generated/variant.js";

/** Native SVG props. In the all-styles package `style` selects the icon style instead of inline CSS. */
type NativeSvgProps = Omit<
  SVGAttributes<SVGSVGElement>,
  "children" | "name" | "title" | (MultiStyle extends true ? "style" : never)
>;

export type IconProps = NativeSvgProps &
  StyleOption & {
    /** `light` (default), `dark` or `auto` (follows `prefers-color-scheme`, SSR-safe). */
    theme?: Theme | undefined;
    /** Width and height, default 40. */
    size?: number | string | undefined;
    /** Accessible name: adds `<title>` and `role="img"`. Without it the icon is `aria-hidden`. */
    title?: string | undefined;
  };

export type FileIconProps = IconProps &
  (
    | { /** Icon name or extension, e.g. `pdf`, `db-sqlite`. */ name: IconName | (string & {}); file?: undefined }
    | { /** File name; the icon is picked by the resolver. */ file: string; name?: undefined }
  );
