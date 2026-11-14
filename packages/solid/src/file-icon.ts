import {
  DEFAULT_SIZE,
  type IconData,
  type IconName,
  iconContent,
  resolveIcon,
  type Style,
  SVG_NAMESPACE,
  type Theme,
  toIconName,
  VIEW_BOX,
} from "@filecon/shared";
import { type Component, createComponent, type JSX, mergeProps, splitProps } from "solid-js";
import { Dynamic } from "solid-js/web";
import { FIXED_STYLE, iconData, type MultiStyle, type StyleOption } from "./generated/variant";

/** Native SVG props. In the all-styles package `style` selects the icon style instead of inline CSS. */
type NativeSvgProps = Omit<
  JSX.SvgSVGAttributes<SVGSVGElement>,
  "children" | "innerHTML" | "textContent" | "name" | (MultiStyle extends true ? "style" : never)
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

export type IconComponent = Component<IconProps>;

const LOCAL_KEYS =
  FIXED_STYLE === null ? (["theme", "size", "title", "style"] as const) : (["theme", "size", "title"] as const);

/** Renders `<svg>` through `Dynamic`, which works for client rendering, SSR and hydration without a JSX transform. */
function renderIcon(data: () => IconData, props: IconProps): JSX.Element {
  const [local, others] = splitProps(props as IconProps & { style?: unknown }, LOCAL_KEYS);
  const style = (): Style => FIXED_STYLE ?? ((local as { style?: Style }).style || "default");
  const size = () => String(local.size ?? DEFAULT_SIZE);
  return createComponent(
    Dynamic,
    mergeProps(
      {
        component: "svg",
        xmlns: SVG_NAMESPACE,
        viewBox: VIEW_BOX,
        fill: "none",
        get width() {
          return size();
        },
        get height() {
          return size();
        },
        get role() {
          return local.title ? "img" : undefined;
        },
        get "aria-hidden"() {
          return local.title ? undefined : "true";
        },
      },
      others,
      {
        get innerHTML() {
          return iconContent(data(), { style: style(), theme: local.theme, title: local.title });
        },
      },
    ),
  );
}

/** Renders the icon for `name` (icon name / extension) or `file` (file name, via the resolver). */
export function FileIcon(props: FileIconProps): JSX.Element {
  const [selection, rest] = splitProps(props, ["name", "file"]);
  const data = () =>
    iconData[selection.name === undefined ? resolveIcon(selection.file ?? "") : toIconName(selection.name)];
  return renderIcon(data, rest as IconProps);
}

/** Creates a single-icon component (used by the generated `icons` entry). */
export function createIcon(_name: IconName, data: IconData): IconComponent {
  return (props) => renderIcon(() => data, props);
}
