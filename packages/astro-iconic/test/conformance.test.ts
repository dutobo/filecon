import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { experimental_AstroContainer as AstroContainer } from "astro/container";
import FileIcon from "../src/FileIcon.astro";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant.js";
import * as icons from "../src/icons.js";
import { iconComponentName } from "../src/index.js";

const container = await AstroContainer.create();
type AstroComponent = Parameters<typeof container.renderToString>[0];

const toProps = ({ style, className, ...rest }: RenderProps): Record<string, unknown> => ({
  ...rest,
  ...(className === undefined ? {} : { class: className }),
  ...(FIXED_STYLE ? {} : { style }),
});

const render = (component: AstroComponent, props: RenderProps) =>
  container.renderToString(component, { props: toProps(props) });

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => render(FileIcon, props),
  renderSingle: (exportName, props) =>
    render((icons as unknown as Record<string, AstroComponent>)[exportName] as AstroComponent, props),
  singleExports: icons,
  iconComponentName,
});
