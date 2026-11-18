import type { IconData, IconName } from "@filecon/shared";

/** A single icon for `<filecon-icon [icon]="PdfIcon" />` (tree-shakable alternative to `name`). */
export interface FileconIcon {
  readonly name: IconName;
  readonly data: IconData;
}
