<!-- <FileIcon name="pdf" /> or <FileIcon file="report.final.pdf" /> -->
<script lang="ts">
  import { resolveIcon, toIconName } from "@filecon/shared";
  import { iconData } from "./generated/variant.js";
  import Icon from "./Icon.svelte";
  import type { FileIconProps } from "./types.js";

  let { name, file, ...rest }: FileIconProps = $props();

  const data = $derived(iconData[name === undefined ? resolveIcon(file ?? "") : toIconName(name)]);
</script>

<Icon {data} {...rest} />
