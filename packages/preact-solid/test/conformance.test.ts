import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { type ComponentType, h } from "preact";
import { renderToString } from "preact-render-to-string";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";
import * as icons from "../src/icons";
import { FileIcon, iconComponentName } from "../src/index";

type AnyComponent = ComponentType<Record<string, unknown>>;
const toProps = ({ style, ...rest }: RenderProps): Record<string, unknown> => (FIXED_STYLE ? rest : { ...rest, style });

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => renderToString(h(FileIcon as unknown as AnyComponent, toProps(props))),
  renderSingle: (exportName, props) =>
    renderToString(h((icons as unknown as Record<string, AnyComponent>)[exportName] as AnyComponent, toProps(props))),
  singleExports: icons,
  iconComponentName,
});
