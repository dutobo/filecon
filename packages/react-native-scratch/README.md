# @filecon/react-native-scratch

[Filecon](https://filecon.dev) file icons for React Native and Expo – 703 file types, the scratch style (pencil sketch on a note sheet).
Rendered with `react-native-svg`, tree-shakable.

Part of the Filecon family: `@filecon/react-native`, `@filecon/react-native-default`, `@filecon/react-native-gray`, `@filecon/react-native-solid`, `@filecon/react-native-papered`, `@filecon/react-native-papered-flat`, `@filecon/react-native-papered-craft`, `@filecon/react-native-scratch`, `@filecon/react-native-chalk`, `@filecon/react-native-iconic`.
This package only contains the `scratch` style, so it is smaller than `@filecon/react-native`; the API is identical except that there is no `style` prop (`style` is the regular view style here).

```sh
npm install @filecon/react-native-scratch react-native-svg
```

## Usage

```tsx
import { FileIcon } from "@filecon/react-native-scratch";
import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/react-native-scratch/icons";

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />   // follows the system color scheme
<PdfIcon size={24} />
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
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
