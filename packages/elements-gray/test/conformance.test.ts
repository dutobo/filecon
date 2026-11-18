import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";
import * as icons from "../src/icons";
import { defineFileconIcon, defineIcons, type IconElementClass, iconComponentName } from "../src/index";

defineFileconIcon();

function attributesOf({ name, file, style, theme, size, title, className }: RenderProps): Record<string, string> {
  const attributes: Record<string, string> = {};
  if (name !== undefined) attributes.name = name;
  if (file !== undefined) attributes.file = file;
  if (style !== undefined && FIXED_STYLE === null) attributes["icon-style"] = style;
  if (theme !== undefined) attributes.theme = theme;
  if (size !== undefined) attributes.size = String(size);
  if (title !== undefined) attributes.label = title;
  if (className !== undefined) attributes["svg-class"] = className;
  return attributes;
}

function renderTag(tagName: string, attributes: Record<string, string>): string {
  const element = document.createElement(tagName);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  document.body.append(element);
  const html = element.innerHTML;
  element.remove();
  return html;
}

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => renderTag("filecon-icon", attributesOf(props)),
  renderSingle: (exportName, props) => {
    const element = (icons as unknown as Record<string, IconElementClass>)[exportName];
    if (!element) return "";
    defineIcons(element);
    return renderTag(element.tagName, attributesOf(props));
  },
  singleExports: icons,
  iconComponentName,
});
