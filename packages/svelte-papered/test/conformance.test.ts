import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import type { Component } from "svelte";
import { render } from "svelte/server";
import FileIcon from "../src/FileIcon.svelte";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant.js";
import * as icons from "../src/icons.js";
import { iconComponentName } from "../src/index.js";

type AnyComponent = Component<Record<string, unknown>>;
const toProps = ({ style, className, ...rest }: RenderProps): Record<string, unknown> => ({
  ...rest,
  ...(className === undefined ? {} : { class: className }),
  ...(FIXED_STYLE ? {} : { style }),
});

const renderSvg = (component: AnyComponent, props: RenderProps) => render(component, { props: toProps(props) }).body;

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => renderSvg(FileIcon as unknown as AnyComponent, props),
  renderSingle: (exportName, props) =>
    renderSvg((icons as unknown as Record<string, AnyComponent>)[exportName] as AnyComponent, props),
  singleExports: icons,
  iconComponentName,
});
