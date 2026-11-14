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
import { type DefineComponent, defineComponent, h, type PropType } from "vue";
import { styleProps } from "./generated/style-props";
import { FIXED_STYLE, iconData } from "./generated/variant";

const iconProps = {
  /** `light` (default), `dark` or `auto` (follows `prefers-color-scheme`, SSR-safe). */
  theme: { type: String as PropType<Theme>, default: "light" },
  /** Width and height, default 40. */
  size: { type: [Number, String] as PropType<number | string>, default: 40 },
  /** Accessible name: adds `<title>` and `role="img"`. Without it the icon is `aria-hidden`. */
  title: { type: String, default: undefined },
  ...styleProps,
} as const;

interface RenderProps {
  theme: Theme;
  size: number | string;
  title?: string | undefined;
  iconStyle?: Style | undefined;
}

function renderIcon(data: IconData, props: RenderProps) {
  const style = FIXED_STYLE ?? props.iconStyle ?? "default";
  const { size, title, theme } = props;
  return h("svg", { ...svgAttributes({ size, title }), innerHTML: iconContent(data, { style, theme, title }) });
}

/**
 * `<FileIcon name="pdf" />` or `<FileIcon file="report.final.pdf" />`.
 * Attributes such as `class` fall through to the `<svg>`.
 */
export const FileIcon = defineComponent({
  name: "FileIcon",
  props: {
    /** Icon name or extension, e.g. `pdf`, `db-sqlite` (exclusive with `file`). */
    // Typed as string: the 703-member IconName union is too complex for Vue's prop inference.
    name: { type: String, default: undefined },
    /** File name; the icon is picked by the resolver (exclusive with `name`). */
    file: { type: String, default: undefined },
    ...iconProps,
  },
  setup(props) {
    return () => {
      const icon = props.name === undefined ? resolveIcon(props.file ?? "") : toIconName(props.name);
      return renderIcon(iconData[icon], props as RenderProps);
    };
  },
});

/** Type of a single-icon component such as `PdfIcon`. */
export type IconComponent = DefineComponent<typeof iconProps>;

/** Creates a single-icon component (used by the generated `icons` entry). */
export function createIcon(name: IconName, data: IconData): IconComponent {
  return defineComponent({
    name: iconComponentName(name),
    props: iconProps,
    setup(props) {
      return () => renderIcon(data, props as RenderProps);
    },
  }) as unknown as IconComponent;
}
