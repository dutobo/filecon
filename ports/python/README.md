# filecon

File-type icons for **703 formats** in nine styles for Python – the SVGs of the [Filecon](https://filecon.dev)
icon pack as package data, plus the Filecon file-type resolver. No dependencies, fully typed.

```sh
pip install filecon
```

```python
import filecon

name = filecon.resolve("report.final.pdf")             # "pdf"
icon = filecon.svg(name)                               # SVG document (default style, light theme)
dark = filecon.svg(name, style="gray", theme="dark")

with open("app.db", "rb") as f:
    name = filecon.resolve("app.db", f.read(1024))     # "db-sqlite" for SQLite files

filecon.svg(".PDF") == filecon.svg("pdf")              # extensions are normalized
filecon.svg("no-such-type") == filecon.svg("empty")    # unknown names give the empty icon

html = f'<img src="{filecon.data_uri(icon)}" width="20" height="20" alt="PDF">'
len(filecon.names())                                   # 703
```

## API

| Function | |
|---|---|
| `svg(name, style="default", theme="light") -> str` | the SVG document; `name` may be an extension (`".PDF"`); unknown names give the `empty` icon; `ValueError` for an unknown style/theme |
| `resolve(file_name, head: bytes \| None = None) -> str` | file name → magic bytes (first 1 KB of `head`) → extension → `"empty"` |
| `names() -> tuple[str, ...]` | all icon names, sorted |
| `is_icon_name(name) -> bool` | exact membership test |
| `to_icon_name(name_or_extension) -> str` | `"PDF"`/`".pdf"` → `"pdf"`, unknown → `"empty"` |
| `data_uri(svg) -> str` | `data:image/svg+xml,…` URI (percent-encoded like JavaScript's `encodeURIComponent`) |
| `Style`, `Theme`, `STYLES`, `THEMES` | `"default"` (outline, colored label), `"gray"` (filled gray page), `"solid"` (filled colored page, identical in both themes), `"papered"`, `"papered-flat"`, `"papered-craft"`, `"scratch"`, `"chalk"`, `"iconic"`; `"light"`, `"dark"` |

The SVGs are the unmodified pack files: 40×40, `viewBox="0 0 40 40"`, label text as paths (no font needed), with a
`<title>` containing the icon name. There is no `auto` theme – pick `"light"` or `"dark"` from your UI state.

`resolve` follows the reference implementation of the icon pack (`resolve_icon.py`, included as
`filecon._reference_resolve`): an extension-less file named like an icon (`Dockerfile`) wins, then content rules for
ambiguous extensions (`.db` → `db-sqlite`/`db-thumbs`/`db-bdb`, `.ts` → `ts-stream`, `.key`, `.m`, `.pl`, `.v`,
`.obj`, `.vhd`, `.img`, …), then the extension, `Makefile` → `mk`, and finally `"empty"`.

The same icons exist for JavaScript frameworks (`@filecon/*` on npm), Rust (`filecon` crate) and VS Code
(Filecon Icons).

## Links

- Website: <https://filecon.dev>
- Source and issues: <https://github.com/dutobo/filecon> (`ports/python`)

Maintained by [dutobo](https://github.com/dutobo); contributor: [rafaelk-f](https://github.com/rafaelk-f).

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
