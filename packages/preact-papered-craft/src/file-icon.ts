import {
  type IconData,
  type IconName,
  iconComponentName,
  iconContent,
  resolveIcon,
  type Style,
  svgAttributes,
  type Theme,
  toIconName,
} from "@filecon/shared";
import { type FunctionComponent, h, type JSX } from "preact";
import { FIXED_STYLE, iconData, type MultiStyle, type StyleOption } from "./generated/variant";

/** Native SVG props. In the all-styles package `style` selects the icon style instead of inline CSS. */
type NativeSvgProps = Omit<
  JSX.IntrinsicElements["svg"],
  "children" | "dangerouslySetInnerHTML" | "name" | (MultiStyle extends true ? "style" : never)
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

export type IconComponent = FunctionComponent<IconProps>;

function renderIcon(data: IconData, props: IconProps) {
  const { theme, size, title, ...rest } = props as IconProps & Record<string, unknown>;
  let style: Style = FIXED_STYLE ?? "default";
  if (FIXED_STYLE === null) {
    style = (rest.style as Style | undefined) ?? "default";
    delete rest.style;
  }
  return h("svg", {
    ...svgAttributes({ size, title }),
    ...rest,
    dangerouslySetInnerHTML: { __html: iconContent(data, { style, theme, title }) },
  } as JSX.IntrinsicElements["svg"]);
}

/**
 * Renders the icon for `name` (icon name / extension) or `file` (file name, via the resolver).
 * `ref` is forwarded to the `<svg>` (Preact 11 passes `ref` as a regular prop).
 */
export function FileIcon({ name, file, ...props }: FileIconProps) {
  const icon = name === undefined ? resolveIcon(file ?? "") : toIconName(name);
  return renderIcon(iconData[icon], props);
}

/** Creates a single-icon component (used by the generated `icons` entry). */
export function createIcon(name: IconName, data: IconData): IconComponent {
  const Icon: IconComponent = (props) => renderIcon(data, props);
  Icon.displayName = iconComponentName(name);
  return Icon;
}
