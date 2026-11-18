import { type IconData, type IconName, renderSvg, type Style, type Theme } from "@filecon/shared";
import { FIXED_STYLE } from "./generated/variant";

/** `HTMLElement` in browsers; a plain class during SSR so that importing the package never throws. */
const ElementBase: typeof HTMLElement =
  typeof HTMLElement === "undefined" ? (class {} as unknown as typeof HTMLElement) : HTMLElement;

/** Attributes understood by every Filecon element. */
export const ICON_ATTRIBUTES = ["icon-style", "theme", "size", "label", "svg-class"] as const;

/**
 * Base class of all Filecon elements. Renders an `<svg>` into the light DOM (no shadow root), so the icon can be
 * styled with normal CSS and is visible to `innerHTML` based SSR.
 */
export abstract class FileconElementBase extends ElementBase {
  static get observedAttributes(): string[] {
    return [...ICON_ATTRIBUTES];
  }

  /** Icon data to render, or `undefined` while nothing is selected. */
  protected abstract iconData(): IconData | undefined;

  connectedCallback(): void {
    this.render();
  }

  attributeChangedCallback(): void {
    if (this.isConnected) this.render();
  }

  /** Re-renders the `<svg>` from the current attributes. */
  render(): void {
    const data = this.iconData();
    if (!data) {
      this.innerHTML = "";
      return;
    }
    const style = (FIXED_STYLE ?? this.getAttribute("icon-style") ?? "default") as Style;
    this.innerHTML = renderSvg(data, {
      style,
      theme: (this.getAttribute("theme") ?? undefined) as Theme | undefined,
      size: this.getAttribute("size") ?? undefined,
      title: this.getAttribute("label") ?? undefined,
      className: this.getAttribute("svg-class") ?? undefined,
    });
  }

  /** `light` (default), `dark` or `auto` (`prefers-color-scheme`). Reflects the `theme` attribute. */
  get theme(): Theme | null {
    return this.getAttribute("theme") as Theme | null;
  }
  set theme(value: Theme | null) {
    this.reflect("theme", value);
  }

  /** Width and height (default 40). Reflects the `size` attribute. */
  get size(): string | null {
    return this.getAttribute("size");
  }
  set size(value: number | string | null) {
    this.reflect("size", value);
  }

  /** Accessible name (`<title>` + `role="img"`); without it the SVG is `aria-hidden`. Reflects `label`. */
  get label(): string | null {
    return this.getAttribute("label");
  }
  set label(value: string | null) {
    this.reflect("label", value);
  }

  protected reflect(attribute: string, value: number | string | null | undefined): void {
    if (value === null || value === undefined || value === "") this.removeAttribute(attribute);
    else this.setAttribute(attribute, String(value));
  }
}

/** A custom element class that always renders one icon (see `@filecon/elements/icons`). */
export type IconElementClass = (new () => FileconElementBase) & {
  /** Icon name, e.g. `pdf`. */
  readonly iconName: IconName;
  /** Suggested tag name, e.g. `filecon-pdf`. */
  readonly tagName: string;
};

/** Creates a single-icon custom element class (used by the generated `icons` entry). */
export function createIconElement(name: IconName, data: IconData): IconElementClass {
  return class extends FileconElementBase {
    static readonly iconName = name;
    static readonly tagName = `filecon-${name}`;
    protected iconData(): IconData {
      return data;
    }
  } as unknown as IconElementClass;
}

/**
 * Registers single-icon elements under their suggested tag names (`PdfIcon` -> `<filecon-pdf>`).
 * Already registered tags are skipped.
 */
export function defineIcons(...elements: IconElementClass[]): void {
  if (typeof customElements === "undefined") return;
  for (const element of elements) {
    if (!customElements.get(element.tagName)) customElements.define(element.tagName, element);
  }
}
