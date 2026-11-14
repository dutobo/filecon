import { ChangeDetectionStrategy, Component, computed, inject, input } from "@angular/core";
import { DomSanitizer, type SafeHtml } from "@angular/platform-browser";
import { type IconName, renderSvg, resolveIcon, type Theme, toIconName } from "@filecon/shared";
import { FIXED_STYLE, iconData } from "./generated/variant";
import type { FileconIcon } from "./icon-def";

/**
 * `<filecon-icon name="pdf" />`, `<filecon-icon file="report.final.pdf" />` or `<filecon-icon [icon]="PdfIcon" />`.
 * Renders the `<svg>` inside the host element; `class`/`style` on the host style the wrapper.
 */
@Component({
  selector: "filecon-icon",
  standalone: true,
  template: "",
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { "[innerHTML]": "html()", style: "display:inline-flex;line-height:0" },
})
export class FileconIconComponent {
  private readonly sanitizer = inject(DomSanitizer);

  /** Icon name or extension, e.g. `pdf`, `db-sqlite` (exclusive with `file` and `icon`). */
  readonly name = input<IconName | (string & {}) | undefined>(undefined);
  /** File name; the icon is picked by the resolver (exclusive with `name` and `icon`). */
  readonly file = input<string | undefined>(undefined);
  /** A single icon from the `icons` entry, e.g. `PdfIcon` (exclusive with `name` and `file`). */
  readonly icon = input<FileconIcon | undefined>(undefined);
  /** `light` (default), `dark` or `auto` (follows `prefers-color-scheme`, SSR-safe). */
  readonly theme = input<Theme>("light");
  /** Width and height, default 40. */
  readonly size = input<number | string>(40);
  /** Accessible name: adds `<title>` and `role="img"`. Without it the icon is `aria-hidden`. */
  readonly title = input<string | undefined>(undefined);

  /** The rendered SVG. Icon data is static package content; `title` is escaped, so bypassing sanitization is safe. */
  protected readonly html = computed<SafeHtml>(() => {
    const icon = this.icon();
    const name = this.name();
    const data = icon?.data ?? iconData[name === undefined ? resolveIcon(this.file() ?? "") : toIconName(name)];
    const svg = renderSvg(data, {
      style: FIXED_STYLE ?? "default",
      theme: this.theme(),
      size: this.size(),
      title: this.title(),
    });
    return this.sanitizer.bypassSecurityTrustHtml(svg);
  });
}
