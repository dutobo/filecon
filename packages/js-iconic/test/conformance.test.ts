import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";
import * as icons from "../src/icons";
import { getFileIcon, getIcon, type IconFunction, type IconOptions, iconComponentName } from "../src/index";

const toOptions = ({ style, ...rest }: Omit<RenderProps, "name" | "file">): IconOptions =>
  (FIXED_STYLE ? rest : { ...rest, style }) as IconOptions;

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: ({ name, file, ...props }) =>
    file === undefined ? getIcon(name ?? "", toOptions(props)) : getFileIcon(file, toOptions(props)),
  renderSingle: (exportName, props) =>
    (icons as unknown as Record<string, IconFunction>)[exportName]?.(toOptions(props)) ?? "",
  singleExports: icons,
  iconComponentName,
});
