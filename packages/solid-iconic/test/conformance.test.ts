import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { type Component, createComponent } from "solid-js";
import { renderToString } from "solid-js/web";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";
import * as icons from "../src/icons";
import { FileIcon, iconComponentName } from "../src/index";

type AnyComponent = Component<Record<string, unknown>>;
const toProps = ({ style, className, ...rest }: RenderProps): Record<string, unknown> => ({
  ...rest,
  ...(className === undefined ? {} : { class: className }),
  ...(FIXED_STYLE ? {} : { style }),
});

const render = (component: AnyComponent, props: RenderProps) =>
  renderToString(() => createComponent(component, toProps(props)));

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => render(FileIcon as unknown as AnyComponent, props),
  renderSingle: (exportName, props) =>
    render((icons as unknown as Record<string, AnyComponent>)[exportName] as AnyComponent, props),
  singleExports: icons,
  iconComponentName,
});
