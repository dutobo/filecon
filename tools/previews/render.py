"""Renders the README preview images into docs/previews/.

The images live only in the GitHub repository; READMEs (also the ones published to npm, crates.io and the
VS Code Marketplace) link to them through raw.githubusercontent.com, so they are never part of a package.

Every image shows the light and the dark theme side by side:

- styles.png             the same sample icons in all nine styles
- style-<style>.png       a grid of 24 icons of one style, with captions
- categories-<style>.png  a few icons of every category of one style
- vscode-<style>.png      the VS Code explorer with the "Filecon <Style>" icon theme

Requirements: Python 3.10+, Pillow, Google Chrome or Chromium (set CHROME to its path if it is not found),
and `pnpm codegen` for the VS Code themes. Run with `python tools/previews/render.py` (or `pnpm previews`).
"""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "previews")
STYLES = ["default", "gray", "solid", "papered", "papered-flat", "papered-craft", "scratch", "chalk", "iconic"]
TITLES = {
    "default": "Default", "gray": "Gray", "solid": "Solid", "papered": "Papered", "papered-flat": "Papered Flat",
    "papered-craft": "Papered Craft", "scratch": "Scratch", "chalk": "Chalk", "iconic": "Iconic",
}
PACK_STYLES = {"default", "gray", "solid"}
SCALE = 2

STYLE_SAMPLES = ["pdf", "docx", "xlsx", "png", "mp3", "zip", "js", "py"]
GRID_SAMPLES = [
    "pdf", "docx", "xlsx", "pptx", "txt", "md",
    "png", "svg", "mp3", "mp4", "zip", "ttf",
    "ts", "js", "py", "rs", "go", "html",
    "css", "json", "yaml", "sql", "exe", "iso",
]
CATEGORIES = [
    (None, "Generic"), ("docs", "Documents"), ("text", "Text and markup"), ("sheet", "Spreadsheets"),
    ("slides", "Presentations"), ("book", "E-books"), ("mail", "Mail"), ("archive", "Archives"),
    ("img", "Images"), ("audio", "Audio"), ("video", "Video"), ("font", "Fonts"),
    ("lang", "Programming languages"), ("data", "Data and config"), ("db", "Databases"), ("web", "Web"),
    ("shell", "Shell"), ("exec", "Executables"), ("pkg", "Packages"), ("cert", "Keys and certificates"),
    ("disk", "Disk images"), ("net", "Network"), ("misc", "Misc"), ("design", "Design"), ("3d", "3D"),
    ("cad", "CAD"), ("gis", "GIS"), ("game", "Games"), ("ml", "Machine learning"),
]
CATEGORY_ICONS = 10

# (depth, name, kind) – kind is "open", "closed" or "file"; the selected row is highlighted like in VS Code.
EXPLORER = [
    (0, "src", "open"), (1, "components", "open"), (2, "Button.vue", "file"), (2, "Card.svelte", "file"),
    (1, "App.tsx", "file"), (1, "index.ts", "file"), (1, "main.rs", "file"), (1, "server.go", "file"),
    (1, "script.py", "file"), (1, "styles.css", "file"), (0, "assets", "closed"), (0, "docs", "closed"),
    (0, ".env", "file"), (0, ".gitignore", "file"), (0, "Cargo.toml", "file"), (0, "config.yaml", "file"),
    (0, "data.json", "file"), (0, "Dockerfile", "file"), (0, "LICENSE", "file"), (0, "package.json", "file"),
    (0, "query.sql", "file"), (0, "README.md", "file"), (0, "report.pdf", "file"), (0, "run.sh", "file"),
]
SELECTED = "Button.vue"

THEMES = {
    "light": {"bg": "#FFFFFF", "fg": "#191D25", "muted": "#5F687A", "line": "#E4E7EC"},
    "dark": {"bg": "#0E1014", "fg": "#E6E8EC", "muted": "#9AA3B4", "line": "#2B303A"},
}
VSCODE = {
    "light": {"bg": "#F8F8F8", "fg": "#3B3B3B", "head": "#616161", "sel": "#E4E6F1", "guide": "#D3D3D3"},
    "dark": {"bg": "#181818", "fg": "#CCCCCC", "head": "#9D9D9D", "sel": "#37373D", "guide": "#404040"},
}
FONT = '"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif'


def icon_file(style: str, theme: str, name: str) -> str:
    if style == "solid":
        return os.path.join(ROOT, "icon-pack", "solid", name + ".svg")
    base = os.path.join(ROOT, "icon-pack") if style in PACK_STYLES else os.path.join(ROOT, "icon-styles")
    return os.path.join(base, style, theme, name + ".svg")


def svg(path: str, px: int) -> str:
    with open(path, encoding="utf8") as handle:
        text = handle.read().strip()
    start = text.index("<svg")
    text = text[start:]
    head_end = text.index(">")
    head = text[:head_end]
    for attr in ("width", "height"):
        head = _drop_attr(head, attr)
    head += f' width="{px}" height="{px}" aria-hidden="true"'
    body = text[head_end:]
    if "<title>" in body:
        body = body[: body.index("<title>")] + body[body.index("</title>") + len("</title>") :]
    return head + body


def _drop_attr(head: str, attr: str) -> str:
    key = f' {attr}="'
    if key not in head:
        return head
    i = head.index(key)
    j = head.index('"', i + len(key))
    return head[:i] + head[j + 1 :]


def page(width: int, height: int, css: str, body: str) -> str:
    return (
        f'<!doctype html><html><head><meta charset="utf-8"><style>'
        f"html,body{{margin:0;padding:0;width:{width}px;height:{height}px;overflow:hidden}}"
        f"body{{font-family:{FONT};display:flex}}"
        f"svg{{display:block;flex:none}}"
        f"{css}</style></head><body>{body}</body></html>"
    )


def panel_css() -> str:
    out = []
    for theme, c in THEMES.items():
        out.append(f".p.{theme}{{background:{c['bg']};color:{c['fg']}}}")
        out.append(f".p.{theme} .muted{{color:{c['muted']}}}")
    return "".join(out) + ".p{box-sizing:border-box;padding:20px;flex:1 1 0}.h{font-size:13px;font-weight:600;height:24px}"


def styles_overview() -> tuple[str, int, int]:
    width, row = 1040, 52
    height = 20 + 24 + len(STYLES) * row - 12 + 20
    css = panel_css() + ".r{display:flex;align-items:center;height:40px;margin-bottom:12px}.l{width:104px;font-size:13px}.r svg{margin-right:8px}"
    panels = []
    for theme in THEMES:
        rows = "".join(
            f'<div class="r"><div class="l muted">{TITLES[s]}</div>'
            + "".join(svg(icon_file(s, theme, n), 40) for n in STYLE_SAMPLES)
            + "</div>"
            for s in STYLES
        )
        panels.append(f'<div class="p {theme}"><div class="h">{theme.title()}</div>{rows}</div>')
    return page(width, height, css, "".join(panels)), width, height


def style_grid(style: str) -> tuple[str, int, int]:
    cols, cell_w, cell_h = 6, 76, 74
    rows = (len(GRID_SAMPLES) + cols - 1) // cols
    width = 2 * (20 + cols * cell_w + 20)
    height = 20 + 24 + rows * cell_h + 8
    css = panel_css() + (
        f".g{{display:grid;grid-template-columns:repeat({cols},{cell_w}px);grid-auto-rows:{cell_h}px}}"
        ".c{display:flex;flex-direction:column;align-items:center;gap:6px}.c span{font-size:11px}"
    )
    panels = []
    for theme in THEMES:
        cells = "".join(
            f'<div class="c">{svg(icon_file(style, theme, n), 44)}<span class="muted">{n}</span></div>'
            for n in GRID_SAMPLES
        )
        label = f"{TITLES[style]} · {theme}"
        panels.append(f'<div class="p {theme}"><div class="h">{html.escape(label)}</div><div class="g">{cells}</div></div>')
    return page(width, height, css, "".join(panels)), width, height


def category_overview(style: str, manifest: dict) -> tuple[str, int, int]:
    row = 36
    width = 2 * (20 + 160 + CATEGORY_ICONS * 34 + 20)
    height = 20 + 24 + len(CATEGORIES) * row + 12
    css = panel_css() + (
        f".r{{display:flex;align-items:center;height:{row}px}}.l{{width:160px;font-size:12px;flex:none}}"
        ".r svg{margin-right:6px}"
    )
    panels = []
    for theme in THEMES:
        rows = []
        for cat, title in CATEGORIES:
            names = [n for n, v in manifest.items() if v.get("category") == cat][:CATEGORY_ICONS]
            icons = "".join(svg(icon_file(style, theme, n), 28) for n in names)
            rows.append(f'<div class="r"><div class="l muted">{title}</div>{icons}</div>')
        label = f"{TITLES[style]} · {theme} · by category"
        panels.append(f'<div class="p {theme}"><div class="h">{html.escape(label)}</div>{"".join(rows)}</div>')
    return page(width, height, css, "".join(panels)), width, height


def theme_icon(theme_json: dict, theme: str, file_name: str, kind: str) -> str:
    """Resolves an explorer entry like VS Code does: file name, then the longest extension, then the default."""
    light = theme_json.get("light", {}) if theme == "light" else {}

    def lookup(section: str, key: str) -> str | None:
        return light.get(section, {}).get(key) or theme_json.get(section, {}).get(key)

    if kind == "open":
        icon_id = light.get("folderExpanded") or theme_json["folderExpanded"]
    elif kind == "closed":
        icon_id = light.get("folder") or theme_json["folder"]
    else:
        lower = file_name.lower()
        icon_id = lookup("fileNames", lower)
        parts = lower.split(".")
        for i in range(1, len(parts)):
            if icon_id:
                break
            icon_id = lookup("fileExtensions", ".".join(parts[i:]))
        icon_id = icon_id or light.get("file") or theme_json["file"]
    return theme_json["iconDefinitions"][icon_id]["iconPath"]


def vscode(style: str) -> tuple[str, int, int]:
    themes_dir = os.path.join(ROOT, "extensions", "vscode", "themes")
    with open(os.path.join(themes_dir, f"filecon-{style}.json"), encoding="utf8") as handle:
        theme_json = json.load(handle)
    row, panel_w = 22, 300
    width = 2 * panel_w
    height = 36 + 22 + len(EXPLORER) * row + 10
    css = (
        ".v{box-sizing:border-box;width:300px;flex:none;font-size:13px}"
        ".t{height:36px;line-height:36px;padding-left:20px;font-size:11px;letter-spacing:.04em}"
        ".w{height:22px;line-height:22px;padding-left:8px;font-size:11px;font-weight:700}"
        ".e{display:flex;align-items:center;height:22px;white-space:nowrap}"
        ".e .k{width:16px;height:16px;flex:none;margin-right:2px}"
        ".e svg{margin-right:6px}"
    )
    for theme, c in VSCODE.items():
        css += (
            f".v.{theme}{{background:{c['bg']};color:{c['fg']}}}.v.{theme} .t,.v.{theme} .w{{color:{c['head']}}}"
            f".v.{theme} .s{{background:{c['sel']}}}.v.{theme} .k path{{stroke:{c['fg']}}}"
        )
    panels = []
    for theme in VSCODE:
        rows = []
        for depth, name, kind in EXPLORER:
            path = os.path.normpath(os.path.join(themes_dir, theme_icon(theme_json, theme, name, kind)))
            caret = ""
            if kind != "file":
                d = "M6 4l4 4-4 4" if kind == "closed" else "M4 6l4 4 4-4"
                caret = f'<path d="{d}" fill="none" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>'
            twistie = f'<svg class="k" viewBox="0 0 16 16" width="16" height="16">{caret}</svg>'
            pad = 8 + depth * 16
            selected = " s" if name == SELECTED else ""
            rows.append(
                f'<div class="e{selected}" style="padding-left:{pad}px">{twistie}{svg(path, 16)}'
                f"<span>{html.escape(name)}</span></div>"
            )
        root_caret = (
            '<svg class="k" viewBox="0 0 16 16" width="16" height="16"><path d="M4 6l4 4 4-4" fill="none"'
            ' stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )
        panels.append(
            f'<div class="v {theme}"><div class="t">EXPLORER</div>'
            f'<div class="e w">{root_caret}<span>FILECON-DEMO</span></div>{"".join(rows)}</div>'
        )
    return page(width, height, css, "".join(panels)), width, height


def find_chrome() -> str:
    candidates = [
        os.environ.get("CHROME"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    sys.exit("Chrome not found; set CHROME to the browser executable")


def render(chrome: str, work: str, name: str, doc: str, width: int, height: int) -> None:
    html_path = os.path.join(work, name + ".html")
    raw = os.path.join(work, name + ".png")
    with open(html_path, "w", encoding="utf8") as handle:
        handle.write(doc)
    subprocess.run(
        [
            chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            f"--user-data-dir={os.path.join(work, 'profile')}", f"--force-device-scale-factor={SCALE}",
            f"--window-size={width},{height}", f"--screenshot={raw}", "file:///" + html_path.replace(os.sep, "/"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    image = Image.open(raw).convert("RGB")
    image = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    image.save(os.path.join(OUT, name + ".png"), optimize=True)
    print(f"{name}.png {image.size[0]}x{image.size[1]} {os.path.getsize(os.path.join(OUT, name + '.png')) // 1024} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("only", nargs="*", help="image names without .png (default: all)")
    args = parser.parse_args()
    with open(os.path.join(ROOT, "icon-pack", "manifest.json"), encoding="utf8") as handle:
        manifest = json.load(handle)
    jobs = {"styles": styles_overview}
    for style in STYLES:
        jobs[f"style-{style}"] = lambda s=style: style_grid(s)
        jobs[f"categories-{style}"] = lambda s=style: category_overview(s, manifest)
        jobs[f"vscode-{style}"] = lambda s=style: vscode(s)
    os.makedirs(OUT, exist_ok=True)
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as work:
        for name, job in jobs.items():
            if args.only and name not in args.only:
                continue
            render(chrome, work, name, *job())


if __name__ == "__main__":
    main()
