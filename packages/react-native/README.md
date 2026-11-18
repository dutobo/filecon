# @filecon/react-native

[Filecon](https://filecon.dev) file icons for React Native and Expo – 703 file types, all eight styles (default, gray, solid, papered, papered-flat, papered-craft, scratch, chalk).
Rendered with `react-native-svg`, tree-shakable.

Part of the Filecon family: `@filecon/react-native`, `@filecon/react-native-default`, `@filecon/react-native-gray`, `@filecon/react-native-solid`, `@filecon/react-native-papered`, `@filecon/react-native-papered-flat`, `@filecon/react-native-papered-craft`, `@filecon/react-native-scratch`, `@filecon/react-native-chalk`.


```sh
npm install @filecon/react-native react-native-svg
```

## Usage

```tsx
import { FileIcon } from "@filecon/react-native";
import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/react-native/icons";

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" style="solid" theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />   // follows the system color scheme
<PdfIcon size={24} />
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
| `style` | `Style`: `"default"`, `"gray"`, `"solid"`, `"papered"`, `"papered-flat"`, `"papered-craft"`, `"scratch"`, `"chalk"` | `"default"` | icon style (not a view style) |
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` uses `useColorScheme()` |
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
