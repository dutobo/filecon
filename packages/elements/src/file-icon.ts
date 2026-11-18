import { type IconData, type IconName, resolveIcon, toIconName } from "@filecon/shared";
import { FileconElementBase, ICON_ATTRIBUTES } from "./element";
import { iconData } from "./generated/variant";

/** Default tag name of {@link FileconIconElement}. */
export const FILECON_ICON_TAG = "filecon-icon";

/**
 * `<filecon-icon name="pdf">` or `<filecon-icon file="report.pdf">` (resolved by file name).
 * Contains the data of every icon of this package; use `@filecon/elements/icons` for single icons.
 */
export class FileconIconElement extends FileconElementBase {
  static override get observedAttributes(): string[] {
    return ["name", "file", ...ICON_ATTRIBUTES];
  }

  protected iconData(): IconData {
    const name = this.getAttribute("name");
    const icon = name !== null ? toIconName(name) : resolveIcon(this.getAttribute("file") ?? "");
    return iconData[icon];
  }

  /** Icon name or extension. Reflects the `name` attribute. */
  get name(): IconName | (string & {}) | null {
    return this.getAttribute("name");
  }
  set name(value: IconName | (string & {}) | null) {
    this.reflect("name", value);
  }

  /** File name; the icon is picked by the resolver (ignored when `name` is set). Reflects `file`. */
  get file(): string | null {
    return this.getAttribute("file");
  }
  set file(value: string | null) {
    this.reflect("file", value);
  }
}

/** Registers {@link FileconIconElement} (default tag `filecon-icon`). Safe to call more than once and during SSR. */
export function defineFileconIcon(tagName: string = FILECON_ICON_TAG): void {
  if (typeof customElements === "undefined" || customElements.get(tagName)) return;
  // A subclass per tag name: one constructor can only be registered once.
  customElements.define(
    tagName,
    tagName === FILECON_ICON_TAG ? FileconIconElement : class extends FileconIconElement {},
  );
}

declare global {
  interface HTMLElementTagNameMap {
    "filecon-icon": FileconIconElement;
  }
}
