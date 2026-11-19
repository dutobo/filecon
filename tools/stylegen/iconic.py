#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Iconic style: one standalone, self-drawn symbol per file type (no page shape), 40x40, in the icon's color.

Duotone language shared by every symbol:
- main: the icon color (lighter in the dark theme) for outlines, solid parts and details,
- mid:  a half tint for secondary details,
- tint: a light wash (dark wash in the dark theme) for body fills.
Strokes are 2.2 px with round caps and joins; symbols fill roughly 31x31 px of the 40x40 box.

Light and dark differ only in color values (same structure), like the other styles. Symbols are added block by block
(category by category) after review; the current block is listed in SYMBOLS.

Usage: python tools/stylegen/iconic.py [--out DIR] [--names a,b]
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "icon-pack"
SW = 2.2  # default stroke width
DARK_BG = (0x10, 0x18, 0x28)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def mix(a: str, b: tuple[int, int, int] | str, t: float) -> str:
    """Mixes color a towards b by t (0 = a, 1 = b)."""
    ra = hex_rgb(a)
    rb = hex_rgb(b) if isinstance(b, str) else b
    return rgb_hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def palette(color: str, theme: str) -> dict[str, str]:
    if theme == "light":
        return {"main": color, "mid": mix(color, "#FFFFFF", 0.5), "tint": mix(color, "#FFFFFF", 0.84)}
    return {"main": mix(color, "#FFFFFF", 0.3), "mid": mix(color, DARK_BG, 0.25), "tint": mix(color, DARK_BG, 0.68)}


class Draw:
    """Collects SVG elements; colors are given as palette roles ('main', 'mid', 'tint')."""

    def __init__(self, pal: dict[str, str]):
        self.pal = pal
        self.parts: list[str] = []

    def _paint(self, fill: str | None, stroke: str | None, width: float | None) -> str:
        attrs = []
        if fill:
            attrs.append(f'fill="{self.pal[fill]}"')
        if stroke:
            attrs.append(f'stroke="{self.pal[stroke]}" stroke-width="{width or SW:g}"')
            attrs.append('stroke-linecap="round" stroke-linejoin="round"')
        return " ".join(attrs)

    def path(self, d: str, fill: str | None = None, stroke: str | None = None, width: float | None = None) -> None:
        self.parts.append(f'<path d="{d}" {self._paint(fill, stroke, width)}/>')

    def circle(self, cx: float, cy: float, r: float, fill=None, stroke=None, width=None) -> None:
        self.parts.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" {self._paint(fill, stroke, width)}/>')

    def rect(self, x, y, w, h, rx=0.0, fill=None, stroke=None, width=None) -> None:
        r = f' rx="{rx:g}"' if rx else ""
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{r} {self._paint(fill, stroke, width)}/>')

    def ellipse(self, cx, cy, rx, ry, fill=None, stroke=None, width=None) -> None:
        self.parts.append(
            f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="{rx:g}" ry="{ry:g}" {self._paint(fill, stroke, width)}/>'
        )


# ------------------------------------------------------------------ shared shapes

PAGE = "M12 4.5h11l8.5 8.5v20a2.5 2.5 0 0 1-2.5 2.5H12a2.5 2.5 0 0 1-2.5-2.5V7A2.5 2.5 0 0 1 12 4.5z"
PAGE_FOLD = "M23 4.5V10.5a2.5 2.5 0 0 0 2.5 2.5h6"


def page(d: Draw, lines: bool = True) -> None:
    d.path(PAGE, fill="tint", stroke="main")
    d.path(PAGE_FOLD, stroke="main")
    if lines:
        d.path("M14.5 20h11M14.5 25h11M14.5 30h6.5", stroke="main")


def gear_path(cx: float, cy: float, r_out: float, r_in: float, teeth: int) -> str:
    """Gear outline with trapezoid teeth."""
    pts = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a = i * step - math.pi / 2
        for da, r in ((-0.30, r_in), (-0.17, r_out), (0.17, r_out), (0.30, r_in)):
            ang = a + da * step * 1.6
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "z"


# ------------------------------------------------------------------ block 1: generic symbols


def s_document(d: Draw) -> None:
    page(d)


def s_empty(d: Draw) -> None:
    page(d, lines=False)


def s_folder(d: Draw) -> None:
    d.path("M5 11a3 3 0 0 1 3-3h8l3.5 3.5H32a3 3 0 0 1 3 3V30a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z", fill="tint", stroke="main")
    d.path("M5 18.5a2.5 2.5 0 0 1 2.5-2.5h25a2.5 2.5 0 0 1 2.5 2.5V30a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z", fill="main")


def s_archive(d: Draw) -> None:
    d.rect(8.5, 4.5, 23, 31, 4, fill="tint", stroke="main")
    for i in range(5):
        y = 7 + i * 2.6
        d.rect(17.6 if i % 2 == 0 else 20, y, 2.4, 1.7, 0.5, fill="main")
    d.rect(16.8, 20.5, 6.4, 9, 2, fill="main")
    d.rect(18.8, 24.6, 2.4, 2.8, 0.8, fill="tint")


def s_package(d: Draw) -> None:
    d.path("M6.5 15h27v16a3 3 0 0 1-3 3h-21a3 3 0 0 1-3-3z", fill="tint", stroke="main")
    d.path("M5 10a2 2 0 0 1 2-2h26a2 2 0 0 1 2 2v5H5z", fill="main", stroke="main")
    d.rect(16.5, 8, 7, 7, fill="mid")
    d.path("M16.5 15h7v8l-3.5-2.2-3.5 2.2z", fill="mid")
    d.path("M10.5 29.5h6", stroke="main")


def s_audio(d: Draw) -> None:
    d.path("M15.5 27.5V10.8l16-3.6v16.8", stroke="main", width=2.6)
    d.path("M15.5 10.8l16-3.6v4.6l-16 3.6z", fill="main", stroke="main", width=1.2)
    d.circle(11.5, 28, 4.5, fill="main")
    d.circle(27.5, 24.5, 4.5, fill="main")
    d.circle(11.5, 28, 1.6, fill="mid")
    d.circle(27.5, 24.5, 1.6, fill="mid")


def s_video(d: Draw) -> None:
    d.rect(6, 5, 28, 30, 3.5, fill="main")
    d.rect(12, 8.5, 16, 23, 1.5, fill="tint")
    for y in (8.5, 14.6, 20.7, 26.8):
        d.rect(7.9, y, 2.4, 3.2, 0.7, fill="tint")
        d.rect(29.7, y, 2.4, 3.2, 0.7, fill="tint")
    d.path("M17.5 15.5v9l7.5-4.5z", fill="main", stroke="main", width=1.4)


def s_video_play(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="tint", stroke="main")
    d.path("M16.5 13.2v13.6L27.5 20z", fill="main", stroke="main", width=1.8)


def s_image(d: Draw) -> None:
    d.rect(4.5, 7.5, 31, 25, 3.5, fill="tint", stroke="main")
    d.circle(14, 15.5, 3.2, fill="mid")
    d.path("M6 29.5l8.5-9.5 6.5 6.5 4.5-4.5 8.5 8.5v.5a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z", fill="main")


def s_code(d: Draw) -> None:
    d.path("M13.5 11.5L5 20l8.5 8.5M26.5 11.5L35 20l-8.5 8.5", stroke="main", width=3)
    d.path("M23 8.5l-6 23", stroke="mid", width=3)


def s_terminal(d: Draw) -> None:
    d.rect(4.5, 7, 31, 26, 4, fill="main")
    d.path("M11 15l5 5-5 5", stroke="tint", width=2.6)
    d.path("M19.5 25.5h9", stroke="mid", width=2.6)


def s_binary(d: Draw) -> None:
    # 1 0 1 / 0 1 0 as rounded bars and capsules
    d.rect(7.2, 7, 3.4, 11, 1.7, fill="main")
    d.rect(15.4, 8.1, 7.2, 8.8, 3.6, stroke="main", width=2.2)
    d.rect(29.4, 7, 3.4, 11, 1.7, fill="main")
    d.rect(5.9, 23.1, 7.2, 8.8, 3.6, stroke="mid", width=2.2)
    d.rect(18.3, 22, 3.4, 11, 1.7, fill="mid")
    d.rect(26.9, 23.1, 7.2, 8.8, 3.6, stroke="mid", width=2.2)


def s_config(d: Draw) -> None:
    d.path(gear_path(20, 20, 15.5, 11.6, 8), fill="main", stroke="main", width=1.6)
    d.circle(20, 20, 5.4, fill="tint")


def s_database(d: Draw) -> None:
    d.path("M7 10.5v19c0 2.5 5.8 4.8 13 4.8s13-2.3 13-4.8v-19", fill="tint", stroke="main")
    d.path("M7 17c0 2.5 5.8 4.8 13 4.8S33 19.5 33 17M7 23.5c0 2.5 5.8 4.8 13 4.8s13-2.3 13-4.8", stroke="main")
    d.ellipse(20, 10.5, 13, 4.8, fill="main", stroke="main")


def s_spreadsheet(d: Draw) -> None:
    d.rect(5.5, 6.5, 29, 27, 3.5, fill="tint", stroke="main")
    d.path("M5.5 10a3.5 3.5 0 0 1 3.5-3.5h22a3.5 3.5 0 0 1 3.5 3.5v4h-29z", fill="main", stroke="main")
    d.path("M5.5 20.5h29M5.5 27h29M15.5 14v19.5", stroke="main", width=1.8)
    d.rect(17.3, 21.9, 15.8, 3.7, 0.6, fill="mid")


def s_presentation(d: Draw) -> None:
    d.path("M4 6.5h32", stroke="main", width=2.6)
    d.rect(6, 6.5, 28, 19.5, 2, fill="tint", stroke="main")
    d.path("M20 26v5M14 35l6-4 6 4", stroke="main")
    d.rect(11, 17, 3.6, 5.5, 0.8, fill="mid")
    d.rect(18.2, 13, 3.6, 9.5, 0.8, fill="main")
    d.rect(25.4, 15, 3.6, 7.5, 0.8, fill="mid")


def s_mail(d: Draw) -> None:
    d.rect(4.5, 8.5, 31, 23, 3.5, fill="tint", stroke="main")
    d.path("M6 11l14 10.5L34 11", stroke="main")


def s_book(d: Draw) -> None:
    d.path("M20 11.5c-3.4-2.6-8.4-3.6-15-3.2v22.5c6.6-.4 11.6.6 15 3.2 3.4-2.6 8.4-3.6 15-3.2V8.3c-6.6-.4-11.6.6-15 3.2z",
           fill="tint", stroke="main")
    d.path("M20 11.5V34", stroke="main")
    d.path("M9 15c2.6 0 5 .4 7 1.3M9 20c2.6 0 5 .4 7 1.3M24 16.3c2-.9 4.4-1.3 7-1.3M24 21.3c2-.9 4.4-1.3 7-1.3",
           stroke="mid", width=1.8)


def s_font(d: Draw) -> None:
    d.path("M5 32l9-24 9 24M8.4 23h11.2", stroke="main", width=3)
    d.circle(29.6, 27.2, 4.3, stroke="mid", width=2.6)
    d.path("M33.9 22.4v9.6", stroke="mid", width=2.6)


def s_3d(d: Draw) -> None:
    d.path("M20 4.5L33.5 12 20 19.5 6.5 12z", fill="mid", stroke="main", width=1.6)
    d.path("M6.5 12L20 19.5v16L6.5 28z", fill="tint", stroke="main", width=1.6)
    d.path("M33.5 12v16L20 35.5v-16z", fill="main", stroke="main", width=1.6)


def s_cad(d: Draw) -> None:
    d.path("M6 34V7l27 27z", fill="tint", stroke="main")
    d.path("M11 29.5V19l10.5 10.5z", fill="mid", stroke="main", width=1.8)
    d.path("M6 12h3M6 17h3M6 22h3M14 34v-3M19 34v-3M24 34v-3", stroke="main", width=1.8)


def s_disc(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="tint", stroke="main")
    d.path("M20 9a11 11 0 0 1 11 11", stroke="mid", width=2.2)
    d.path("M9 20a11 11 0 0 0 11 11", stroke="mid", width=2.2)
    d.circle(20, 20, 5.6, fill="main")
    d.circle(20, 20, 2, fill="tint")


def s_game(d: Draw) -> None:
    d.path("M12.2 11.5h15.6a7 7 0 0 1 6.8 5.4l1.7 7.6a4.6 4.6 0 0 1-7.8 4.2L25.5 26h-11l-3 2.7a4.6 4.6 0 0 1-7.8-4.2l1.7-7.6a7 7 0 0 1 6.8-5.4z",
           fill="main", stroke="main", width=1.4)
    d.path("M13 15.6v6.4M9.8 18.8h6.4", stroke="tint", width=2.4)
    d.circle(26.6, 16.6, 1.7, fill="tint")
    d.circle(30, 20.4, 1.7, fill="mid")


def s_map_pin(d: Draw) -> None:
    d.ellipse(20, 35, 6.5, 1.8, fill="mid")
    d.path("M20 34.5s11-9.8 11-18a11 11 0 0 0-22 0c0 8.2 11 18 11 18z", fill="main", stroke="main", width=1.4)
    d.circle(20, 16.5, 4.4, fill="tint")


def s_network(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="tint", stroke="main")
    d.ellipse(20, 20, 6.5, 15.5, stroke="main", width=1.9)
    d.path("M4.5 20h31M7 12.5h26M7 27.5h26", stroke="main", width=1.9)


def s_neural(d: Draw) -> None:
    left, middle, right = [(8, 12.5), (8, 27.5)], [(20, 7.5), (20, 20), (20, 32.5)], [(32, 13.5), (32, 26.5)]
    edges = [(a, b) for a in left for b in middle] + [(a, b) for a in middle for b in right]
    d.path("".join(f"M{a[0]:g} {a[1]:g}L{b[0]:g} {b[1]:g}" for a, b in edges), stroke="mid", width=1.6)
    for x, y in left + right:
        d.circle(x, y, 3.6, fill="main")
    for x, y in middle:
        d.circle(x, y, 3.6, fill="tint", stroke="main", width=2)


def s_secret_key(d: Draw) -> None:
    d.circle(12.5, 20, 7.8, fill="main")
    d.circle(12.5, 20, 2.8, fill="tint")
    d.path("M19 17.6h16.2v4.8H32v4.2h-4.6v-4.2H19z", fill="main", stroke="main", width=1.2)


SYMBOLS = {
    "3d": s_3d,
    "archive": s_archive,
    "audio": s_audio,
    "binary": s_binary,
    "book": s_book,
    "cad": s_cad,
    "code": s_code,
    "config": s_config,
    "database": s_database,
    "disc": s_disc,
    "document": s_document,
    "empty": s_empty,
    "folder": s_folder,
    "font": s_font,
    "game": s_game,
    "image": s_image,
    "mail": s_mail,
    "map-pin": s_map_pin,
    "network": s_network,
    "neural": s_neural,
    "package": s_package,
    "presentation": s_presentation,
    "secret-key": s_secret_key,
    "spreadsheet": s_spreadsheet,
    "terminal": s_terminal,
    "video": s_video,
    "video-play": s_video_play,
}


def render(name: str, color: str, theme: str) -> str:
    d = Draw(palette(color, theme))
    SYMBOLS[name](d)
    body = "".join(d.parts)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40" fill="none">'
        f"<title>{name}</title>{body}</svg>\n"
    )


def structure(svg: str) -> str:
    return re.sub(r'(fill|stroke)="#[0-9A-F]{6}"', r'\1="#"', svg)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", default=str(ROOT / "icon-styles"), help="output root (writes iconic/<theme>/)")
    parser.add_argument("--names", help="comma-separated subset")
    args = parser.parse_args()
    manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    names = args.names.split(",") if args.names else sorted(SYMBOLS)
    out = Path(args.out)
    for name in names:
        color = manifest[name]["color"]
        svgs = {theme: render(name, color, theme) for theme in ("light", "dark")}
        assert structure(svgs["light"]) == structure(svgs["dark"]), name
        assert "id=" not in svgs["light"] and "<defs" not in svgs["light"], name
        for theme, svg in svgs.items():
            target = out / "iconic" / theme / f"{name}.svg"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(svg, encoding="utf-8", newline="\n")
    print(f"iconic: {len(names)} symbols x 2 themes -> {out / 'iconic'}")


if __name__ == "__main__":
    main()
