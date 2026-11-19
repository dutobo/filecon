# filecon

File-type icons for **703 formats** in nine styles for Rust – the SVGs of the [Filecon](https://filecon.dev)
icon pack embedded with `include_str!`, plus the Filecon file-type resolver.

```toml
[dependencies]
filecon = "0.3"
# only one style (smaller binary):
# filecon = { version = "0.3", default-features = false, features = ["style-solid"] }
```

```rust
use filecon::{names, resolve, svg, Style, Theme};

let name = resolve("report.final.pdf", None);                 // "pdf"
let icon: &'static str = svg(name, Style::Default, Theme::Light).unwrap();

let head = std::fs::read("app.db").unwrap_or_default();
let name = resolve("app.db", Some(&head));                    // "db-sqlite" for SQLite files
let dark = svg(name, Style::Gray, Theme::Dark);

assert_eq!(names().len(), 703);
```

## API

| Item | |
|---|---|
| `svg(name, style, theme) -> Option<&'static str>` | the SVG document; `None` for unknown names or disabled styles |
| `resolve(file_name, head: Option<&[u8]>) -> &'static str` | file name → magic bytes (first 1 KB) → extension → `"empty"` |
| `names() -> &'static [&'static str]` | all icon names, sorted |
| `is_icon_name(name)` | membership test |
| `Style::{Default, Gray, Solid, Papered, PaperedFlat, PaperedCraft, Scratch, Chalk, Iconic}` (also `Style::ALL`), `Theme::{Light, Dark}` | `Solid` is identical in both themes |

The SVGs are the unmodified pack files: 40×40, `viewBox="0 0 40 40"`, label text as paths (no font needed),
with a `<title>` containing the icon name. Unlike the JavaScript packages there is no `auto` theme (pick
`Theme::Light`/`Theme::Dark` from your UI state).

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

The resolver is a port of `icon-pack/resolve_icon.py` and is tested against the pack's `resolve-cases.json`.
No dependencies, `#![forbid(unsafe_code)]`.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
