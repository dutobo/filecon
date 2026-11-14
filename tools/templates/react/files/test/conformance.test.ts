import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { type ComponentType, createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";
import * as icons from "../src/icons";
import { FileIcon, iconComponentName } from "../src/index";

const toProps = ({ style, ...rest }: RenderProps): Record<string, unknown> => (FIXED_STYLE ? rest : { ...rest, style });

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) =>
    renderToStaticMarkup(createElement(FileIcon as unknown as ComponentType<Record<string, unknown>>, toProps(props))),
  renderSingle: (exportName, props) =>
    renderToStaticMarkup(
      createElement(
        (icons as unknown as Record<string, ComponentType<Record<string, unknown>>>)[exportName] as ComponentType,
        toProps(props),
      ),
    ),
  singleExports: icons,
  iconComponentName,
});
