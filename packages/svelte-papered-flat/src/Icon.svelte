<!-- Renders one icon from its data. Used by FileIcon and every single-icon component. -->
<script lang="ts">
  import { type IconData, iconContent, type Style, svgAttributes } from "@filecon/shared";
  import { FIXED_STYLE } from "./generated/variant.js";
  import type { IconProps } from "./types.js";

  let { data, theme = "light", size = 40, title, ...rest }: IconProps & { data: IconData } = $props();

  const style: Style = $derived(FIXED_STYLE ?? (rest as { style?: Style }).style ?? "default");
  const attributes = $derived.by(() => {
    const result: Record<string, unknown> = { ...rest };
    if (FIXED_STYLE === null) delete result.style;
    return result;
  });
</script>

<svg {...svgAttributes({ size, title })} {...attributes}>{@html iconContent(data, { style, theme, title })}</svg>
