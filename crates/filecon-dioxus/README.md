# filecon-dioxus

[Dioxus](https://dioxuslabs.com) component for the [Filecon](https://filecon.dev) file-type icons:
**703 formats** in nine styles, rendered as inline SVG. Built on the [`filecon`](https://crates.io/crates/filecon)
crate (embedded SVGs + file-type resolver).

![The same file icons in all nine Filecon styles, light and dark](https://raw.githubusercontent.com/dutobo/filecon/main/docs/previews/styles.png)

More previews (a grid and a category overview per style): [docs/previews](https://github.com/dutobo/filecon/tree/main/docs/previews#readme).

```toml
[dependencies]
filecon-dioxus = "0.3"
# only one style (smaller binary):
# filecon-dioxus = { version = "0.3", default-features = false, features = ["style-solid"] }
```

## Usage

```rust
use dioxus::prelude::*;
use filecon_dioxus::{FileIcon, Style, Theme};

#[component]
fn FileRow(file_name: String) -> Element {
    rsx! {
        div { class: "row",
            // picked by the resolver from the file name (name → extension → "empty")
            FileIcon { file: file_name.clone(), size: 24 }
            span { "{file_name}" }
        }
    }
}

#[component]
fn Examples() -> Element {
    rsx! {
        FileIcon { name: "pdf" }                                          // decorative: aria-hidden="true"
        FileIcon { name: "db-sqlite", style: Style::Gray, theme: Theme::Dark }
        FileIcon { name: "zip", style: Style::Solid, size: 32, class: "icon" }
        FileIcon { name: "docx", title: "Word document" }                 // role="img" + <title>
    }
}
```

The component only renders an `<svg>` element, so it works the same with every Dioxus renderer:

| Platform | Setup |
|---|---|
| Web (WASM) | `dioxus = { version = "0.7", features = ["web"] }`, `dx serve --platform web` |
| Desktop (Windows, macOS, Linux) | `dioxus = { version = "0.7", features = ["desktop"] }`, `dx serve --platform desktop` |
| Mobile (iOS, Android) | `dioxus = { version = "0.7", features = ["mobile"] }`, `dx serve --platform ios` / `android` |
| SSR / fullstack | rendered on the server, hydrated on the client |

No assets, fonts or network requests are needed: the SVG markup is embedded in the binary.

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `Option<String>` | – | icon name or extension (`"pdf"`, `".PDF"`, `"db-sqlite"`); wins over `file` |
| `file` | `Option<String>` | – | file name or path, resolved with `filecon::resolve(file, None)` |
| `style` | `Style` | `Style::Default` | `Default`, `Gray`, `Solid`, `Papered`, `PaperedFlat`, `PaperedCraft`, `Scratch`, `Chalk`, `Iconic` |
| `theme` | `Theme` | `Theme::Light` | `Light`, `Dark` (ignored by `Solid`) |
| `size` | `u32` | `40` | width and height in pixels |
| `title` | `Option<String>` | – | accessible name: adds `role="img"` and an escaped `<title>` |
| `class` | `Option<String>` | – | CSS class of the `<svg>` |

Unknown names render the `empty` icon. Output:

```html
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true">…</svg>
```

There is no `auto` theme: pick `Theme::Light` / `Theme::Dark` from your UI state.

## Other exports

| Item | |
|---|---|
| `icon_markup(name, style, theme) -> Option<&'static str>` | inner SVG markup (no `<svg>`, no `<title>`) |
| `to_icon_name(name_or_extension) -> &'static str` | normalizes `".PDF"` → `"pdf"`, unknown → `"empty"` |
| `resolve`, `names`, `is_icon_name`, `Style`, `Theme` | re-exported from `filecon` |

## Features

| Feature | Default | Embeds |
|---|---|---|
| `style-default` | yes | `default/light`, `default/dark` |
| `style-gray` | yes | `gray/light`, `gray/dark` |
| `style-solid` | yes | `solid` |
| `style-papered` | yes | `papered/light`, `papered/dark` |
| `style-papered-flat` | yes | `papered-flat/light`, `papered-flat/dark` |
| `style-papered-craft` | yes | `papered-craft/light`, `papered-craft/dark` |
| `style-scratch` | yes | `scratch/light`, `scratch/dark` |
| `style-chalk` | yes | `chalk/light`, `chalk/dark` |
| `style-iconic` | yes | `iconic/light`, `iconic/dark` |

If the requested style is disabled, the first enabled style is rendered instead.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
