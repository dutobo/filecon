# {{packageName}}

[Filecon](https://filecon.dev) file icons for React Native and Expo – {{iconCount}} file types, {{styleLabel}}.
Rendered with `react-native-svg`, tree-shakable.

Part of the Filecon family: {{siblings}}.
{{#isSingle}}This package only contains the `{{fixedStyle}}` style, so it is smaller than `{{allPackage}}`; the API is identical except that there is no `style` prop (`style` is the regular view style here).{{/isSingle}}

```sh
npm install {{packageName}} react-native-svg
```

## Usage

```tsx
import { FileIcon } from "{{packageName}}";
import { PdfIcon, TsStreamIcon, Icon7z } from "{{packageName}}/icons";

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" {{#isAll}}style="solid" {{/isAll}}theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />   // follows the system color scheme
<PdfIcon size={24} />
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
{{#isAll}}| `style` | `Style`: `"default"`, `"gray"`, `"solid"`, `"papered"`, `"papered-flat"`, `"papered-craft"`, `"scratch"`, `"chalk"` | `"default"` | icon style (not a view style) |
{{/isAll}}| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` uses `useColorScheme()` |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | `accessibilityLabel` + `<title>`; without it the icon is hidden from screen readers |
| other | `SvgXml` props | – | forwarded to `SvgXml`, `ref` too |

## Deviations from the web packages

- **`theme="auto"`** cannot use CSS media queries (react-native-svg ignores `<style>`); it resolves the theme with
  `useColorScheme()` and re-renders when the system scheme changes.
- **Accessibility** uses React Native props (`accessible`, `accessibilityLabel`, `accessibilityRole="image"`,
  `importantForAccessibility`) in addition to `role`/`aria-hidden` in the SVG markup.
- Peer dependencies: `react`, `react-native`, `react-native-svg` (≥ 13). Built with `tsup`.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
