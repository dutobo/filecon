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


# ------------------------------------------------------------------ badges (variants such as macro or template files)

BADGE_C = 31.0


def badge(d: Draw, glyph: str) -> None:
    """Small round badge at the bottom right; the tint ring separates it from the symbol below."""
    d.circle(BADGE_C, BADGE_C, 7.6, fill="main", stroke="tint", width=2.2)
    if glyph == "macro":
        d.path("M32.2 26.2l-4.4 5.6h3l-1 4.2 4.4-5.6h-3z", fill="tint")
    elif glyph == "template":
        d.rect(27.2, 27.2, 5, 5, 1, stroke="tint", width=1.5)
        d.rect(29.8, 29.8, 5, 5, 1, fill="tint")
    elif glyph == "binary":
        d.rect(27.4, 27.3, 1.9, 7.4, 0.95, fill="tint")
        d.rect(31.2, 28, 3.6, 6, 1.8, stroke="tint", width=1.5)
    elif glyph == "play":
        d.path("M29 27.4v7.2l5.8-3.6z", fill="tint")
    elif glyph == "database":
        d.ellipse(31, 28.2, 3.8, 1.5, fill="tint")
        d.path("M27.2 28.6v4.8c0 .9 1.7 1.6 3.8 1.6s3.8-.7 3.8-1.6v-4.8", stroke="tint", width=1.4)
    elif glyph == "sync":
        d.path("M34.4 29a3.8 3.8 0 1 0 .3 3.4", stroke="tint", width=1.6)
        d.path("M35 26.6v2.8h-2.8", stroke="tint", width=1.6)
    elif glyph == "web":
        d.circle(31, 31, 3.9, stroke="tint", width=1.4)
        d.ellipse(31, 31, 1.6, 3.9, stroke="tint", width=1.2)
        d.path("M27.1 31h7.8", stroke="tint", width=1.2)
    elif glyph == "sparkle":
        d.path(
            "M31 26.2c.5 2.6 2.2 4.3 4.8 4.8-2.6.5-4.3 2.2-4.8 4.8-.5-2.6-2.2-4.3-4.8-4.8 2.6-.5 4.3-2.2 4.8-4.8z",
            fill="tint",
        )
    elif glyph == "spring":
        d.path("M27.4 26.8h7.2M27.4 35.2h7.2", stroke="tint", width=1.4)
        d.path("M31 28.2l-2.6 1 5.2 1.8-5.2 1.8 2.6 1", stroke="tint", width=1.4)
    elif glyph == "bars":
        d.path("M27.6 28h3M27.6 31h4.8M27.6 34h6.8", stroke="tint", width=1.6)
    elif glyph == "funnel":
        d.path("M27 27.6h8l-3 3.4v3.4l-2 1.2v-4.6z", fill="tint")
    elif glyph == "plus":
        d.path("M31 27.2v7.6M27.2 31h7.6", stroke="tint", width=2)
    else:
        raise ValueError(glyph)


def rotated(points: list[tuple[float, float]], angle: float, cx: float, cy: float) -> str:
    """Closed polygon path of points (around 0/0) rotated by angle degrees and moved to cx/cy."""
    a = math.radians(angle)
    out = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in points]
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in out) + "z"


def star_path(cx: float, cy: float, r_out: float, r_in: float, points: int) -> str:
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "z"


# ------------------------------------------------------------------ block 2: documents and text

# Office-like apps: a back sheet with app-specific art and a front tile with the app letter.
LETTERS = {
    "W": "M7.8 15.5l1.9 9 3.3-6.5 3.3 6.5 1.9-9",
    "X": "M9 15.8l8 8.4M17 15.8l-8 8.4",
    "P": "M10.2 24.5v-9h3.6a2.8 2.8 0 0 1 0 5.6h-3.6",
    "V": "M8.8 15.5l4.2 9 4.2-9",
    "N": "M9.3 24.5v-9l7.4 9v-9",
}


def office_tile(d: Draw, letter: str) -> None:
    d.rect(4, 11, 18, 18, 3.2, fill="main", stroke="tint", width=1.6)
    if letter == "O":
        d.circle(13, 20, 4.4, stroke="tint", width=2.4)
    else:
        d.path(LETTERS[letter], stroke="tint", width=2.4)


def back_sheet(d: Draw) -> None:
    d.rect(13, 5, 22, 30, 3, fill="tint", stroke="main")


def s_word(d: Draw) -> None:
    back_sheet(d)
    d.path("M24 10.5h7M24 15.5h7M24 20.5h7M24 25.5h7M24 30.5h7", stroke="mid", width=2)
    office_tile(d, "W")


def s_excel(d: Draw) -> None:
    back_sheet(d)
    d.path("M28.5 5v30M22 12.5h13M22 20h13M22 27.5h13", stroke="mid", width=1.8)
    office_tile(d, "X")


def s_powerpoint(d: Draw) -> None:
    d.circle(23, 20, 13, fill="tint", stroke="main")
    d.path("M23 20V7a13 13 0 0 1 13 13z", fill="mid", stroke="main", width=1.6)
    office_tile(d, "P")


def s_visio(d: Draw) -> None:
    back_sheet(d)
    d.path("M28.5 13v14", stroke="main", width=1.6)
    d.rect(25, 8.5, 7, 5, 1, fill="mid")
    d.rect(25, 26.5, 7, 5, 1, fill="mid")
    d.path("M28.5 17l3 3-3 3-3-3z", fill="main")
    office_tile(d, "V")


def s_onenote(d: Draw) -> None:
    for y in (8.5, 15.5, 22.5):
        d.rect(31, y, 6, 5, 1.2, fill="mid")
    back_sheet(d)
    d.path("M24 11h6M24 16.5h6M24 22h6M24 27.5h6", stroke="mid", width=2)
    office_tile(d, "N")


def s_publisher(d: Draw) -> None:
    back_sheet(d)
    d.rect(24, 8.5, 8, 7.5, 1.2, fill="mid")
    d.path("M24 21h8M24 25.5h8M24 30h5", stroke="mid", width=1.8)
    office_tile(d, "P")


def s_project(d: Draw) -> None:
    back_sheet(d)
    d.rect(23, 8.5, 6, 3.4, 1.2, fill="mid")
    d.rect(25.5, 14.5, 7, 3.4, 1.2, fill="main")
    d.rect(23, 20.5, 9, 3.4, 1.2, fill="mid")
    d.rect(27, 26.5, 5.5, 3.4, 1.2, fill="main")
    office_tile(d, "P")


def s_outlook(d: Draw) -> None:
    d.rect(13, 8, 22, 23, 3, fill="tint", stroke="main")
    d.path("M14 10l10.5 8.5L35 10", stroke="main")
    office_tile(d, "O")


def odf_page(d: Draw) -> None:
    """OpenDocument family: page with a filled fold and a colored foot band."""
    d.path(PAGE, fill="tint", stroke="main")
    d.path("M23 4.5l8.5 8.5h-6a2.5 2.5 0 0 1-2.5-2.5z", fill="main", stroke="main", width=1.6)
    d.path("M9.5 29h22v4a2.5 2.5 0 0 1-2.5 2.5H12A2.5 2.5 0 0 1 9.5 33z", fill="main")


def s_odf_text(d: Draw) -> None:
    odf_page(d)
    d.path("M14 13.5h6.5", stroke="main", width=2.4)
    d.path("M14 18.5h13M14 23.5h10", stroke="mid", width=2.2)


def s_odf_sheet(d: Draw) -> None:
    odf_page(d)
    for row, y in enumerate((14.5, 20)):
        for col, x in enumerate((13.5, 18.8, 24.1)):
            d.rect(x, y, 4.2, 4, 0.8, fill="main" if (row, col) == (1, 2) else "mid")


def s_odf_slides(d: Draw) -> None:
    odf_page(d)
    d.rect(13.5, 14, 14, 10, 1.4, fill="mid")
    d.path("M20.5 19v-3.4a3.4 3.4 0 1 1-3.4 3.4z", fill="main")


def s_quill(d: Draw) -> None:
    d.path("M33.5 5.5C22 6.5 13.5 13.5 11.8 26.5l-.3 2.4 2.5-.4c12.6-1.8 19.7-10.6 19.5-23z", fill="tint", stroke="main")
    d.path("M30.5 8.5L6 34.5", stroke="main")
    d.path("M17.5 21.5h7.5M21.5 16.5h7.5M14.5 26.5h5", stroke="mid", width=1.8)


def s_acrobat(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 7, fill="main")
    d.path(
        "M19.6 9.6c-1.6 0-1.7 2.6-.6 5.8 1.9 5.5 6.4 10.6 10.7 11.2 2.3.3 2.9-1.3 1.4-2.2-2.4-1.4-9.5-.3-15.5 3.2"
        "-4.2 2.5-5.3 4.7-3.8 5.1 1.6.4 4-3.2 6.2-8.4 2.2-5.2 3-9.7 2.4-12.5-.2-1.4-.4-2.2-.8-2.2z",
        stroke="tint",
        width=2,
    )


def s_pages(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 7, fill="main")
    nib = [(-4.2, -9), (4.2, -9), (4.2, -3), (0, 8), (-4.2, -3)]
    d.path(rotated(nib, 45, 22.5, 17.5), fill="tint")
    d.path("M17.3 22.7l-6.8 6.8", stroke="mid", width=2.2)
    d.circle(24.3, 15.7, 1.4, fill="main")


def s_printer(d: Draw) -> None:
    d.rect(12, 4.5, 16, 10, 1.5, fill="tint", stroke="main")
    d.rect(5, 13, 30, 13, 3.5, fill="main")
    d.circle(30, 17.5, 1.4, fill="tint")
    d.path("M11 22h18v11a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 11 33z", fill="tint", stroke="main")
    d.path("M15 27h10M15 31h6.5", stroke="mid", width=2)


def s_scan(d: Draw) -> None:
    page(d, lines=False)
    d.circle(16, 16.5, 2, fill="mid")
    d.path("M13 27l5-5.5 3.5 3.5 2.6-2.6L28.5 27z", fill="mid")
    d.path("M14.5 31h10", stroke="mid", width=2)
    d.path("M4.5 21.5h31", stroke="main", width=2.6)


def s_text(d: Draw) -> None:
    d.path("M7 9h26M7 16h21M7 23h26M7 30h12", stroke="main", width=2.6)
    d.path("M23.5 25.5v9M21.5 25.5h4M21.5 34.5h4", stroke="mid", width=2.2)


def s_markdown(d: Draw) -> None:
    d.rect(3.5, 10, 33, 20, 3.5, fill="tint", stroke="main")
    d.path("M9 25V15l4.5 5 4.5-5v10", stroke="main", width=2.6)
    d.path("M27.5 15v10M23.5 21l4 4 4-4", stroke="main", width=2.6)


def s_mdx(d: Draw) -> None:
    d.rect(3.5, 10, 33, 20, 3.5, fill="tint", stroke="main")
    d.path("M9 25V15l4.5 5 4.5-5v10", stroke="main", width=2.6)
    d.path("M23.5 15.5l8 9M31.5 15.5l-8 9", stroke="main", width=2.6)


def s_rst(d: Draw) -> None:
    d.path("M7 8.5h18", stroke="main", width=3.2)
    d.path("M7 13.5h18M7 17h18", stroke="main", width=1.6)
    d.path("M7 24h26M7 29.5h26M7 35h15", stroke="mid", width=2.2)


def s_asciidoc(d: Draw) -> None:
    d.path("M7 10h5M7 14h5", stroke="main", width=2)
    d.path("M16.5 12h16.5", stroke="main", width=3.2)
    d.path("M7 21.5h26M7 27h26M7 32.5h17", stroke="mid", width=2.2)


def asterisk(d: Draw, x: float, y: float) -> None:
    d.path(
        f"M{x:g} {y - 2.6:g}v5.2M{x - 2.25:g} {y - 1.3:g}l4.5 2.6M{x - 2.25:g} {y + 1.3:g}l4.5-2.6",
        stroke="main",
        width=1.6,
    )


def s_org(d: Draw) -> None:
    asterisk(d, 8, 9)
    d.path("M13 9h20", stroke="main", width=2.6)
    asterisk(d, 13, 20)
    d.path("M18 20h15", stroke="mid", width=2.2)
    asterisk(d, 18, 31)
    d.path("M23 31h10", stroke="mid", width=2.2)


def s_rich_text(d: Draw) -> None:
    d.path("M7 8.5h20", stroke="main", width=3.8)
    d.rect(5.5, 13.5, 26, 6.2, 1.6, fill="mid")
    d.path("M7.5 16.6h21", stroke="main", width=2.2)
    d.path("M7 24.5h26", stroke="main", width=2.2)
    d.path("M7 30h15", stroke="main", width=2.2)
    d.path("M7 34h15", stroke="mid", width=1.8)


def s_tex(d: Draw) -> None:
    d.path("M4.5 12.5h10M9.5 12.5v15", stroke="main", width=2.8)
    d.path("M21.5 18h-5v12.5h5M16.5 24.2h4", stroke="main", width=2.8)
    d.path("M24.5 12.5l10 15M34.5 12.5l-10 15", stroke="main", width=2.8)


def s_bib(d: Draw) -> None:
    d.rect(6, 10, 6.5, 24.5, 1.2, fill="tint", stroke="main")
    d.rect(14.5, 6.5, 6.5, 28, 1.2, fill="main", stroke="main")
    d.path(rotated([(-3.25, -13), (3.25, -13), (3.25, 13), (-3.25, 13)], 16, 28.2, 21.6), fill="mid", stroke="main")
    d.path("M7.5 15h3.5M16 12h3.5", stroke="mid", width=1.6)


BRACES = (
    "M14 7.5c-3 0-3.8 1.5-3.8 4v4.2c0 2-1 3.6-3.2 4.3 2.2.7 3.2 2.3 3.2 4.3v4.2c0 2.5.8 4 3.8 4"
    "M26 7.5c3 0 3.8 1.5 3.8 4v4.2c0 2 1 3.6 3.2 4.3-2.2.7-3.2 2.3-3.2 4.3v4.2c0 2.5-.8 4-3.8 4"
)


def s_tex_class(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.rect(15.5, 12.5, 9, 15, 1.4, fill="tint", stroke="main", width=1.8)
    d.path("M18 17.5h4M18 21h4M18 24.5h2.5", stroke="mid", width=1.4)


def s_tex_style(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.path("M16.5 13l7 14", stroke="mid", width=2.8)


def s_subtitles(d: Draw) -> None:
    d.rect(4.5, 7.5, 31, 25, 3.5, fill="tint", stroke="main")
    d.path("M10 21.5h12M25.5 21.5h4.5M10 26.5h6.5M19.5 26.5h10.5", stroke="main", width=2.6)


def s_subtitle_bubble(d: Draw) -> None:
    d.path(
        "M8 6h24a3.5 3.5 0 0 1 3.5 3.5v15A3.5 3.5 0 0 1 32 28H17.5L10 34.5V28H8a3.5 3.5 0 0 1-3.5-3.5v-15A3.5 3.5 0 0 1 8 6z",
        fill="tint",
        stroke="main",
    )
    d.path("M11 14.5h18M11 20.5h11", stroke="main", width=2.6)


def s_numbers(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 7, fill="main")
    d.rect(10.5, 19, 5, 10.5, 1.2, fill="tint")
    d.rect(17.5, 10.5, 5, 19, 1.2, fill="tint")
    d.rect(24.5, 15, 5, 14.5, 1.2, fill="mid")


def s_keynote(d: Draw) -> None:
    d.path("M27.5 11.5l3-5.5", stroke="mid", width=1.8)
    d.circle(31, 5.5, 1.8, fill="mid")
    d.path("M14 18.5h12l-2.2 13.5h-7.6z", fill="tint", stroke="main")
    d.path("M7.5 11.5h25L30 18.5H10z", fill="main", stroke="main", width=1.6)
    d.path("M11 34.5h18", stroke="main", width=2.8)


def s_epub(d: Draw) -> None:
    d.path("M13 27L20 34 34 20 20 6 6 20", stroke="main", width=3.4)
    d.path("M20 13.2l6.8 6.8-6.8 6.8-6.8-6.8z", fill="mid")


def ereader(d: Draw) -> None:
    d.rect(8.5, 4.5, 23, 31, 4, fill="main")
    d.rect(11.5, 8, 17, 21.5, 1.2, fill="tint")
    d.path("M17.5 32.4h5", stroke="tint", width=1.6)


def s_ereader(d: Draw) -> None:
    ereader(d)
    d.path("M14.5 12.5h11M14.5 16.5h11M14.5 20.5h11M14.5 24.5h7", stroke="mid", width=1.8)


def s_ereader_cover(d: Draw) -> None:
    ereader(d)
    d.circle(17, 13.5, 2, fill="main")
    d.path("M11.5 26.5l6-6.5 3.8 3.8 2.6-2.6 4.6 4.8v3.5h-17z", fill="mid")


def s_fb2(d: Draw) -> None:
    d.rect(8.5, 4.5, 23, 31, 2.5, fill="tint", stroke="main")
    d.path("M13 4.5v31", stroke="main")
    d.path("M22.5 4.5v12l3-2.4 3 2.4v-12z", fill="main", stroke="main", width=1.4)
    d.path("M17 23h10M17 28h6.5", stroke="mid", width=2)


def comic_page(d: Draw) -> None:
    d.rect(6.5, 4.5, 27, 31, 2.5, fill="tint", stroke="main")
    d.path("M6.5 18h27M19 4.5V18M23 18v17.5", stroke="main", width=2)


def s_comic(d: Draw) -> None:
    comic_page(d)
    d.ellipse(12.8, 10.6, 4.2, 3, fill="main")
    d.path("M10.6 12.8l-1.6 3.2 3.8-2.2z", fill="main")
    d.circle(28.2, 26.8, 3, fill="mid")


def s_comic_burst(d: Draw) -> None:
    comic_page(d)
    d.circle(12.8, 11.2, 3, fill="mid")
    d.path(star_path(28.2, 26.8, 4.6, 2.3, 8), fill="main")


def s_calendar(d: Draw) -> None:
    d.rect(5.5, 8, 29, 26.5, 3.5, fill="tint", stroke="main")
    d.path("M5.5 11.5A3.5 3.5 0 0 1 9 8h22a3.5 3.5 0 0 1 3.5 3.5V16h-29z", fill="main", stroke="main")
    d.path("M13 5v6M27 5v6", stroke="main", width=2.6)
    for row, y in enumerate((19.5, 25.8)):
        for col, x in enumerate((10.5, 18, 25.5)):
            d.rect(x, y, 4, 3.6, 0.8, fill="main" if (row, col) == (1, 2) else "mid")


def s_contact(d: Draw) -> None:
    d.rect(4.5, 8.5, 31, 23, 3.5, fill="tint", stroke="main")
    d.circle(13.5, 17, 3.4, fill="main")
    d.path("M8 27.5c0-3.5 2.4-5.5 5.5-5.5s5.5 2 5.5 5.5z", fill="main")
    d.path("M23 16h8M23 21h8M23 26h5", stroke="mid", width=2)


def s_letter(d: Draw) -> None:
    d.path("M5 18L20 7.5 35 18z", fill="mid", stroke="main")
    d.rect(10, 6, 20, 18, 1.5, fill="tint", stroke="main")
    d.path("M14 11.5h12M14 15.5h12M14 19.5h7", stroke="mid", width=1.8)
    d.path("M5 18l15 10.5L35 18v14a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z", fill="main", stroke="main")


def s_envelope_stamp(d: Draw) -> None:
    d.rect(4.5, 8.5, 31, 23, 3.5, fill="tint", stroke="main")
    d.rect(25, 12.5, 6.5, 7, 1, fill="mid", stroke="main", width=1.6)
    d.path("M10 22.5h11M10 27h7.5", stroke="main", width=2)


def s_mailbox(d: Draw) -> None:
    d.path("M28 20V9h6v5h-6", fill="mid", stroke="main", width=1.8)
    d.path("M14 11h14a8 8 0 0 1 8 8v13H6V19a8 8 0 0 1 8-8z", fill="tint", stroke="main")
    d.path("M6 32V19a8 8 0 0 1 16 0v13z", fill="main", stroke="main")
    d.path("M10 20h8", stroke="tint", width=2)
    d.path("M14 32v4", stroke="main", width=3)


# ------------------------------------------------------------------ block 2: archives


def s_books_strap(d: Draw) -> None:
    d.rect(6, 6.5, 28, 8, 1.6, fill="tint", stroke="main")
    d.rect(6, 16, 28, 8, 1.6, fill="mid", stroke="main")
    d.rect(6, 25.5, 28, 8, 1.6, fill="tint", stroke="main")
    d.rect(16.5, 4.5, 7, 31, 1.2, fill="main")
    d.rect(17.8, 17.6, 4.4, 4.8, 0.8, stroke="tint", width=1.4)


def s_seven_zip(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 4, fill="main")
    d.path("M10.5 11.5h12L15.5 29", stroke="tint", width=3.2)
    d.path("M23.5 20.5h6.5l-6.5 8h6.5", stroke="mid", width=2.4)


def s_tape(d: Draw) -> None:
    d.rect(4.5, 8, 31, 24, 3.5, fill="main")
    d.rect(10, 12.5, 20, 9.5, 2, fill="tint")
    d.circle(14.8, 17.2, 2.7, fill="main")
    d.circle(25.2, 17.2, 2.7, fill="main")
    d.path("M12 32l2-5h12l2 5", fill="mid")


def s_spring(d: Draw) -> None:
    d.path("M8 6h24M8 34h24", stroke="main", width=3.2)
    d.path("M20 8.5L12 12l16 4-16 4 16 4-16 4 8 3.5", stroke="mid", width=2.2)


def s_sorted_blocks(d: Draw) -> None:
    for i, (w, role) in enumerate(((11, "mid"), (17, "main"), (23, "mid"), (29, "main"))):
        d.rect(5.5, 6 + i * 7.4, w, 5, 1.5, fill=role)


def s_funnel(d: Draw) -> None:
    d.path("M5.5 8h29L24 20.5v9.5l-8 4.5V20.5z", fill="tint", stroke="main")
    d.circle(12.5, 12, 1.7, fill="mid")
    d.circle(20, 13.5, 1.7, fill="main")
    d.circle(27.5, 11.5, 1.7, fill="mid")


def s_bolt(d: Draw) -> None:
    d.path("M23.5 4.5L10 22.5h9.5l-3 13 14.5-19h-9.5z", fill="main", stroke="main", width=1.6)
    d.path("M4.5 14h5M3.5 20h4M30.5 26h5M32 32h3.5", stroke="mid", width=2)


def s_fast_forward(d: Draw) -> None:
    d.path("M5.5 10.5l13 9.5-13 9.5z", fill="mid", stroke="mid", width=2)
    d.path("M20 10.5l13 9.5-13 9.5z", fill="main", stroke="main", width=2)


def s_press(d: Draw) -> None:
    d.path("M20 4v7.5M15.5 7.5l4.5 4.5 4.5-4.5M20 36v-7.5M15.5 32.5l4.5-4.5 4.5 4.5", stroke="main", width=2.4)
    d.rect(5, 15, 30, 10, 2.5, fill="main")
    d.path("M10.5 20h19", stroke="tint", width=2)


def s_cabinet(d: Draw) -> None:
    d.rect(8, 4.5, 24, 31, 3, fill="tint", stroke="main")
    d.path("M8 15h24M8 25h24", stroke="main")
    for y in (8.6, 18.6, 28.6):
        d.rect(16.5, y, 7, 2.6, 1.3, fill="main")


def s_crate(d: Draw) -> None:
    d.rect(5.5, 8, 29, 25.5, 2, fill="tint", stroke="main")
    d.path("M5.5 16.5L34.5 25", stroke="mid", width=2.4)
    d.path("M5.5 16.5h29M5.5 25h29", stroke="main")
    d.path("M11 8v25.5M29 8v25.5", stroke="main", width=1.6)


def s_jar(d: Draw) -> None:
    d.path(
        "M13.5 10.5h13v3c4.2 2 6.5 6 6.5 11 0 6.2-3.8 11-8.5 11h-9c-4.7 0-8.5-4.8-8.5-11 0-5 2.3-9 6.5-11z",
        fill="tint",
        stroke="main",
    )
    d.rect(11.5, 4.5, 17, 6, 1.8, fill="main", stroke="main", width=1.6)
    d.rect(12, 20.5, 16, 8, 1.5, fill="mid")


def s_z_letter(d: Draw) -> None:
    d.path("M11.5 9.5h17l-17 21h17", stroke="main", width=3.6)
    d.path("M4 15.5l3 4.5-3 4.5M36 15.5l-3 4.5 3 4.5", stroke="mid", width=2.2)


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
    # block 2
    "acrobat": s_acrobat,
    "asciidoc": s_asciidoc,
    "bib": s_bib,
    "bolt": s_bolt,
    "books-strap": s_books_strap,
    "cabinet": s_cabinet,
    "calendar": s_calendar,
    "press": s_press,
    "comic": s_comic,
    "comic-burst": s_comic_burst,
    "contact": s_contact,
    "crate": s_crate,
    "envelope-stamp": s_envelope_stamp,
    "epub": s_epub,
    "ereader": s_ereader,
    "ereader-cover": s_ereader_cover,
    "excel": s_excel,
    "fast-forward": s_fast_forward,
    "fb2": s_fb2,
    "funnel": s_funnel,
    "storage-jar": s_jar,
    "keynote": s_keynote,
    "letter": s_letter,
    "mailbox": s_mailbox,
    "markdown": s_markdown,
    "mdx": s_mdx,
    "numbers": s_numbers,
    "odf-sheet": s_odf_sheet,
    "odf-slides": s_odf_slides,
    "odf-text": s_odf_text,
    "onenote": s_onenote,
    "org": s_org,
    "outlook": s_outlook,
    "pages": s_pages,
    "powerpoint": s_powerpoint,
    "printer": s_printer,
    "project": s_project,
    "publisher": s_publisher,
    "quill": s_quill,
    "rich-text": s_rich_text,
    "rst": s_rst,
    "scan": s_scan,
    "seven-zip": s_seven_zip,
    "sorted-blocks": s_sorted_blocks,
    "spring": s_spring,
    "subtitle-bubble": s_subtitle_bubble,
    "subtitles": s_subtitles,
    "tape": s_tape,
    "tex": s_tex,
    "tex-class": s_tex_class,
    "tex-style": s_tex_style,
    "text": s_text,
    "visio": s_visio,
    "word": s_word,
    "z-letter": s_z_letter,
}

# Icon name -> (symbol, badge). Icons not listed here use the symbol of the same name without a badge. Aliases share a
# symbol; variants of one format (macro, template, binary, slide show, ...) add a badge to it.
ICONS: dict[str, tuple[str, str | None]] = {
    # docs
    "doc": ("word", None),
    "docx": ("word", None),
    "docm": ("word", "macro"),
    "dot": ("word", "template"),
    "dotx": ("word", "template"),
    "odt": ("odf-text", None),
    "ott": ("odf-text", "template"),
    "wpd": ("quill", None),
    "pdf": ("acrobat", None),
    "pages": ("pages", None),
    "xps": ("printer", None),
    "oxps": ("printer", None),
    "djvu": ("scan", None),
    "vsd": ("visio", None),
    "vsdx": ("visio", None),
    "one": ("onenote", None),
    "pub": ("publisher", None),
    "mpp": ("project", None),
    # text
    "txt": ("text", None),
    "text": ("text", None),
    "md": ("markdown", None),
    "markdown": ("markdown", None),
    "mdx": ("mdx", None),
    "rst": ("rst", None),
    "adoc": ("asciidoc", None),
    "org": ("org", None),
    "rtf": ("rich-text", None),
    "tex": ("tex", None),
    "bib": ("bib", None),
    "cls": ("tex-class", None),
    "sty": ("tex-style", None),
    "srt": ("subtitles", None),
    "vtt": ("subtitles", "web"),
    "ass": ("subtitles", "sparkle"),
    "ssa": ("subtitles", "sparkle"),
    "sub": ("subtitle-bubble", None),
    # sheet
    "xls": ("excel", None),
    "xlsx": ("excel", None),
    "xlsm": ("excel", "macro"),
    "xlsb": ("excel", "binary"),
    "xltx": ("excel", "template"),
    "ods": ("odf-sheet", None),
    "numbers": ("numbers", None),
    # slides
    "ppt": ("powerpoint", None),
    "pptx": ("powerpoint", None),
    "pptm": ("powerpoint", "macro"),
    "pps": ("powerpoint", "play"),
    "ppsx": ("powerpoint", "play"),
    "potx": ("powerpoint", "template"),
    "odp": ("odf-slides", None),
    "key-keynote": ("keynote", None),
    # book
    "epub": ("epub", None),
    "mobi": ("ereader", None),
    "azw3": ("ereader-cover", None),
    "fb2": ("fb2", None),
    "cbz": ("comic", None),
    "cbr": ("comic-burst", None),
    # mail
    "ics": ("calendar", None),
    "vcf": ("contact", None),
    "eml": ("letter", None),
    "emlx": ("envelope-stamp", None),
    "msg": ("outlook", None),
    "pst": ("outlook", "database"),
    "ost": ("outlook", "sync"),
    "mbox": ("mailbox", None),
    # archive
    "zip": ("archive", None),
    "zipx": ("archive", "plus"),
    "rar": ("books-strap", None),
    "7z": ("seven-zip", None),
    "tar": ("tape", None),
    "tgz": ("tape", "spring"),
    "tbz2": ("tape", "bars"),
    "txz": ("tape", "funnel"),
    "gz": ("spring", None),
    "bz2": ("sorted-blocks", None),
    "xz": ("funnel", None),
    "zst": ("bolt", None),
    "lz4": ("fast-forward", None),
    "lzma": ("press", None),
    "cab": ("cabinet", None),
    "arj": ("crate", None),
    "lzh": ("storage-jar", None),
    "z": ("z-letter", None),
}


def render(name: str, color: str, theme: str) -> str:
    d = Draw(palette(color, theme))
    symbol, glyph = ICONS.get(name, (name, None))
    SYMBOLS[symbol](d)
    if glyph:
        badge(d, glyph)
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
    names = args.names.split(",") if args.names else sorted(n for n in manifest if n in ICONS or n in SYMBOLS)
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
