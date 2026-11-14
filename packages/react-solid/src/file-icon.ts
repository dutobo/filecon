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
import {
  createElement,
  type ForwardRefExoticComponent,
  forwardRef,
  type Ref,
  type RefAttributes,
  type SVGProps,
} from "react";
import { FIXED_STYLE, iconData, type MultiStyle, type StyleOption } from "./generated/variant";

/** Native SVG props. In the all-styles package `style` selects the icon style instead of inline CSS. */
type NativeSvgProps = Omit<
  SVGProps<SVGSVGElement>,
  "ref" | "children" | "dangerouslySetInnerHTML" | "name" | (MultiStyle extends true ? "style" : never)
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

export type IconComponent = ForwardRefExoticComponent<IconProps & RefAttributes<SVGSVGElement>>;

function renderIcon(data: IconData, props: IconProps, ref: Ref<SVGSVGElement>) {
  const { theme, size, title, ...rest } = props as IconProps & Record<string, unknown>;
  let style: Style = FIXED_STYLE ?? "default";
  if (FIXED_STYLE === null) {
    style = (rest.style as Style | undefined) ?? "default";
    delete rest.style;
  }
  return createElement("svg", {
    ...svgAttributes({ size, title }),
    ...rest,
    ref,
    dangerouslySetInnerHTML: { __html: iconContent(data, { style, theme, title }) },
  });
}

/** Renders the icon for `name` (icon name / extension) or `file` (file name, via the resolver). */
// PURE: lets bundlers drop FileIcon (and with it the full icon map) when only single icons are imported.
export const FileIcon = /*#__PURE__*/ forwardRef<SVGSVGElement, FileIconProps>(function FileIcon(
  { name, file, ...props },
  ref,
) {
  const icon = name === undefined ? resolveIcon(file ?? "") : toIconName(name);
  return renderIcon(iconData[icon], props, ref);
});

/** Creates a single-icon component (used by the generated `icons` entry). */
export function createIcon(name: IconName, data: IconData): IconComponent {
  // biome-ignore lint/correctness/noComponentHookFactories: called once per icon at module level, never during render
  const Icon = forwardRef<SVGSVGElement, IconProps>((props, ref) => renderIcon(data, props, ref));
  Icon.displayName = iconComponentName(name);
  return Icon;
}
