import {
  type IconData,
  type IconName,
  iconComponentName,
  renderSvg,
  resolveIcon,
  type Style,
  type Theme,
  toIconName,
} from "@filecon/shared";
import { createElement, type ForwardRefExoticComponent, forwardRef, type Ref, type RefAttributes } from "react";
import { useColorScheme } from "react-native";
import { SvgXml, type XmlProps } from "react-native-svg";
import { FIXED_STYLE, iconData, type MultiStyle, type StyleOption } from "./generated/variant";

/** `SvgXml` props. In the all-styles package `style` selects the icon style instead of a view style. */
type NativeProps = Omit<
  XmlProps,
  "xml" | "width" | "height" | "children" | "override" | (MultiStyle extends true ? "style" : never)
>;

export type IconProps = NativeProps &
  StyleOption & {
    /** `light` (default), `dark` or `auto` (follows the system color scheme via `useColorScheme`). */
    theme?: Theme | undefined;
    /** Width and height, default 40. */
    size?: number | string | undefined;
    /** Accessible name: sets `accessibilityLabel` and adds `<title>`. Without it the icon is hidden from a11y. */
    title?: string | undefined;
  };

export type FileIconProps = IconProps &
  (
    | { /** Icon name or extension, e.g. `pdf`, `db-sqlite`. */ name: IconName | (string & {}); file?: undefined }
    | { /** File name; the icon is picked by the resolver. */ file: string; name?: undefined }
  );

// biome-ignore lint/suspicious/noExplicitAny: the ref type of SvgXml differs between react-native-svg versions
export type IconComponent = ForwardRefExoticComponent<IconProps & RefAttributes<any>>;

function useIcon(data: IconData, props: IconProps, ref: Ref<unknown>) {
  const scheme = useColorScheme();
  const { theme = "light", size = 40, title, ...rest } = props as IconProps & Record<string, unknown>;
  let style: Style = FIXED_STYLE ?? "default";
  if (FIXED_STYLE === null) {
    style = (rest.style as Style | undefined) ?? "default";
    delete rest.style;
  }
  // react-native-svg has no CSS media queries: "auto" is resolved with the system color scheme instead.
  const resolvedTheme: Theme = theme === "auto" ? (scheme === "dark" ? "dark" : "light") : theme;
  return createElement(SvgXml, {
    xml: renderSvg(data, { style, theme: resolvedTheme, size, title }),
    width: size,
    height: size,
    accessible: Boolean(title),
    accessibilityLabel: title,
    accessibilityRole: title ? "image" : undefined,
    importantForAccessibility: title ? "auto" : "no-hide-descendants",
    ...rest,
    ref,
  } as XmlProps);
}

/** Renders the icon for `name` (icon name / extension) or `file` (file name, via the resolver). */
export const FileIcon = forwardRef<unknown, FileIconProps>(function FileIcon({ name, file, ...props }, ref) {
  const icon = name === undefined ? resolveIcon(file ?? "") : toIconName(name);
  return useIcon(iconData[icon], props, ref);
});

/** Creates a single-icon component (used by the generated `icons` entry). */
export function createIcon(name: IconName, data: IconData): IconComponent {
  // biome-ignore lint/correctness/noComponentHookFactories: called once per icon at module level, never during render
  const Icon = forwardRef<unknown, IconProps>((props, ref) => useIcon(data, props, ref));
  Icon.displayName = iconComponentName(name);
  return Icon as IconComponent;
}
