import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { type Component, createSSRApp, h } from "vue";
import { renderToString } from "vue/server-renderer";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";
import * as icons from "../src/icons";
import { FileIcon, iconComponentName } from "../src/index";

const toProps = ({ style, className, ...rest }: RenderProps): Record<string, unknown> => ({
  ...rest,
  ...(className === undefined ? {} : { class: className }),
  ...(FIXED_STYLE ? {} : { iconStyle: style }),
});

const render = (component: Component, props: RenderProps) =>
  renderToString(createSSRApp({ render: () => h(component, toProps(props)) }));

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => render(FileIcon, props),
  renderSingle: (exportName, props) =>
    render((icons as unknown as Record<string, Component>)[exportName] as Component, props),
  singleExports: icons,
  iconComponentName,
});
