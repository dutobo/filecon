import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import type { ReactElement } from "react";
import { vi } from "vitest";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";

// react-native itself cannot run in Node; the platform pieces are mocked and the rendered element is inspected.
const platform = vi.hoisted(() => ({ scheme: "light" as "light" | "dark" }));
vi.mock("react-native", () => ({ useColorScheme: () => platform.scheme }));
vi.mock("react-native-svg", () => ({ SvgXml: "SvgXml" }));

const icons = await import("../src/icons");
const { FileIcon, iconComponentName } = await import("../src/index");

type ForwardRef = { render(props: Record<string, unknown>, ref: unknown): ReactElement<{ xml: string }> };
const toProps = ({ style, className: _className, ...rest }: RenderProps): Record<string, unknown> =>
  FIXED_STYLE ? rest : { ...rest, style };
const render = (component: unknown, props: RenderProps) =>
  (component as ForwardRef).render(toProps(props), null).props.xml;

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => render(FileIcon, props),
  renderSingle: (exportName, props) => render((icons as Record<string, unknown>)[exportName], props),
  singleExports: icons,
  iconComponentName,
  autoMode: "color-scheme",
  setColorScheme: (scheme) => {
    platform.scheme = scheme;
  },
  classOnSvg: false,
});
