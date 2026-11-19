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
    elif glyph == "gem":
        d.path("M28.6 28.4h4.8l1.8 2.4-4.2 4.6-4.2-4.6z", fill="tint")
    elif glyph == "note":
        d.path("M32.4 34V27.2c1 .9 2.4 1.4 2.6 3", stroke="tint", width=1.5)
        d.circle(30.4, 33.8, 2, fill="tint")
    elif glyph.startswith("letter-"):
        letter = glyph[len("letter-") :]
        if letter == "O":
            d.circle(31, 31, 3.3, stroke="tint", width=1.8)
        else:
            d.path(BADGE_LETTERS[letter], stroke="tint", width=1.8)
    else:
        raise ValueError(glyph)


BADGE_LETTERS = {
    "C": "M33.8 28.6a3.6 3.6 0 1 0 0 4.8",
    "N": "M28.4 34.6v-7.2l5.2 7.2v-7.2",
    "F": "M29.2 34.6v-7.2h4.6M29.2 30.8h3.6",
    "L": "M29.2 27.4v7.2h4.6",
    "alpha": "M34.6 27.8c-.7 3.6-2 6.4-3.8 6.4-1.6 0-2.6-1.4-2.6-3.2s1-3.2 2.6-3.2c2 0 2.4 4.6 3.8 6.4",
}


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


# ------------------------------------------------------------------ block 3: media (images, audio, video, fonts)

MOUNTAIN = [(0.04, 0.94), (0.3, 0.56), (0.5, 0.8), (0.66, 0.62), (0.96, 0.94)]


def scene(d: Draw, x: float, y: float, w: float, h: float, r: float, frame: str | None = "tint", sun: str = "mid",
          outline: bool = True) -> None:
    """Small photo: frame, sun and mountains scaled into the box."""
    if frame:
        d.rect(x, y, w, h, r, fill=frame, stroke="main" if outline else None)
    pad = 1.6
    ix, iy, iw, ih = x + pad, y + pad, w - 2 * pad, h - 2 * pad
    d.circle(round(ix + iw * 0.3, 2), round(iy + ih * 0.3, 2), round(min(iw, ih) * 0.12, 2), fill=sun)
    pts = [(ix + iw * px, iy + ih * py) for px, py in MOUNTAIN]
    d.path("M" + "L".join(f"{px:.2f} {py:.2f}" for px, py in pts) + "z", fill="main")


def s_photo_alpha(d: Draw) -> None:
    d.rect(4.5, 7.5, 31, 25, 3.5, fill="tint", stroke="main")
    cw, ch = 26 / 6, 20 / 5
    for row in range(5):
        for col in range(6):
            if (row + col) % 2:
                d.rect(round(7 + col * cw, 2), 10 + row * ch, round(cw, 2), ch, fill="mid")
    d.path("M6 29.5l8.5-9.5 6.5 6.5 4.5-4.5 8.5 8.5v.5a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z", fill="main")


def s_frames(d: Draw) -> None:
    d.rect(14, 4.5, 21, 16, 2.5, fill="tint", stroke="main", width=1.8)
    d.rect(9.5, 11, 21, 16, 2.5, fill="tint", stroke="main", width=1.8)
    scene(d, 5, 17.5, 21, 16, 2.5)


def s_pixel_art(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 3, fill="tint", stroke="main")
    rows = ["......", ".s....", "....m.", "...mmm", ".m.mmm", "mmmmmm"]
    step = 27.6 / 6
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                d.rect(round(6.2 + c * step, 2), round(6.2 + r * step, 2), 4.2, 4.2, 0.6,
                       fill="main" if ch == "m" else "mid")


def s_icon_sizes(d: Draw) -> None:
    d.rect(4.5, 4.5, 31, 31, 3.5, fill="tint", stroke="main")
    d.rect(9, 13, 18, 18, 2.5, fill="mid")
    d.rect(9, 22, 9, 9, 2, fill="main")


def s_icon_squircles(d: Draw) -> None:
    d.rect(4.5, 4.5, 31, 31, 9.5, fill="tint", stroke="main")
    d.rect(10, 10, 20, 20, 6.5, fill="mid")
    d.rect(15, 15, 10, 10, 3.5, fill="main")


def s_cursor(d: Draw) -> None:
    d.path("M10 4.5v26l6.6-6.2 4.6 10.4 4.6-2-4.6-10.2h9z", fill="main", stroke="main", width=2)
    d.path("M13.5 13l9.5 8.6", stroke="mid", width=1.6)


def s_crop(d: Draw) -> None:
    scene(d, 9.5, 9.5, 21, 21, 1.5)
    d.path("M3.5 9.5H7M9.5 3.5V7M33 9.5h3.5M30.5 3.5V7M3.5 30.5H7M9.5 33v3.5M33 30.5h3.5M30.5 33v3.5",
           stroke="main", width=2)


def phone(d: Draw) -> None:
    d.rect(10, 3.5, 20, 33, 4.5, fill="main")
    d.rect(12.5, 7, 15, 24, 1.5, fill="tint")
    d.path("M17.5 33.6h5", stroke="tint", width=1.6)


def s_phone_photo(d: Draw) -> None:
    phone(d)
    scene(d, 12.5, 11, 15, 16, 0, frame=None)


def s_phone_play(d: Draw) -> None:
    phone(d)
    d.path("M17.5 14.5v9l7-4.5z", fill="main", stroke="main", width=1.4)


def s_photo_circle(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="tint", stroke="main")
    d.circle(15, 13, 2.8, fill="mid")
    d.path("M7.3 26.5L14.5 18l5.5 5.5 4.5-4.5 8.2 7.5A14.27 14.27 0 0 1 7.3 26.5z", fill="main")


def s_photo_hexagon(d: Draw) -> None:
    d.path("M35.5 20l-7.75 13.42h-15.5L4.5 20l7.75-13.42h15.5z", fill="tint", stroke="main")
    d.circle(15, 13.5, 2.6, fill="mid")
    d.path("M8.25 26.5L14.5 19l5 5.5 4-4 7.75 6-3.5 6.92h-15.5z", fill="main")


def s_photo_wave(d: Draw) -> None:
    d.rect(4.5, 7.5, 31, 25, 3.5, fill="tint", stroke="main")
    d.path("M8.5 15c2.5-4 5-4 7.5 0s5 4 7.5 0 5-4 7.5 0", stroke="mid", width=2.2)
    d.path("M6 29.5l8.5-8 6.5 5.5 4.5-4 8.5 7v.5a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z", fill="main")


def s_target(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="tint", stroke="main")
    d.circle(20, 20, 10, fill="mid", stroke="main")
    d.circle(20, 20, 4.5, fill="main")


def s_paintbrush(d: Draw) -> None:
    d.path("M34 6L22 18", stroke="main", width=3.6)
    d.path(rotated([(-3.6, -2.6), (3.6, -2.6), (3.6, 2.6), (-3.6, 2.6)], -45, 20.2, 19.8), fill="mid")
    d.path("M17.8 18.6c-3.2-.4-5.8 1.6-6.2 4.8-.3 2.4-1.6 4-4.1 4.6 4.4 3 11.6 1.4 12.5-4.4z", fill="main")
    d.path("M7 34c6-.6 12-1.6 18-4", stroke="mid", width=2.4)


def pixel_grid(d: Draw, role) -> None:
    d.rect(5, 5, 30, 30, 3, fill="tint", stroke="main")
    for r in range(4):
        for c in range(4):
            fill = role(r, c)
            if fill:
                d.rect(8 + c * 6.25, 8 + r * 6.25, 5.5, 5.5, 0.8, fill=fill)


def s_pixels_bw(d: Draw) -> None:
    pixel_grid(d, lambda r, c: "main" if (r + c) % 2 else None)


def s_pixels_gray(d: Draw) -> None:
    pixel_grid(d, lambda r, c: "main" if r + c <= 2 else ("mid" if r + c <= 4 else None))


def s_pixels_color(d: Draw) -> None:
    pixel_grid(d, lambda r, c: "main" if (r + c) % 2 else "mid")


def s_gpu_chip(d: Draw) -> None:
    pins = "".join(f"M{x:g} 4.5v4M{x:g} 31.5v4M4.5 {x:g}h4M31.5 {x:g}h4" for x in (14, 20, 26))
    d.path(pins, stroke="main", width=2)
    d.rect(8.5, 8.5, 23, 23, 3, fill="main")
    d.rect(13, 13, 7, 7, 0.8, fill="tint")
    d.rect(20, 20, 7, 7, 0.8, fill="tint")
    d.rect(20, 13, 7, 7, 0.8, fill="mid")
    d.rect(13, 20, 7, 7, 0.8, fill="mid")


def s_mipmaps(d: Draw) -> None:
    d.rect(4.5, 10, 19, 19, 2.5, fill="tint", stroke="main")
    d.rect(7.5, 13, 6.5, 6.5, 0.8, fill="mid")
    d.rect(14, 19.5, 6.5, 6.5, 0.8, fill="mid")
    d.rect(26, 10, 9.5, 9.5, 1.8, fill="main")
    d.rect(26, 22, 5, 5, 1.2, fill="main")
    d.rect(33, 22, 2.6, 2.6, 0.6, fill="main")


def s_aperture(d: Draw) -> None:
    cx = cy = 20.0
    d.circle(cx, cy, 15.5, fill="main")
    r_in, r_out = 5.4, 14.6
    hexagon = [(cx + r_in * math.cos(math.radians(60 * k)), cy + r_in * math.sin(math.radians(60 * k))) for k in range(6)]
    d.path("M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in hexagon) + "z", fill="tint")
    lines = []
    for k in range(6):
        (ax, ay), (bx, by) = hexagon[k], hexagon[(k + 1) % 6]
        ux, uy = bx - ax, by - ay
        n = math.hypot(ux, uy)
        ux, uy = ux / n, uy / n
        px, py = bx - cx, by - cy
        b = px * ux + py * uy
        t = -b + math.sqrt(b * b - (px * px + py * py - r_out * r_out))
        lines.append(f"M{bx:.2f} {by:.2f}L{bx + ux * t:.2f} {by + uy * t:.2f}")
    d.path("".join(lines), stroke="tint", width=1.8)


def s_sun_hdr(d: Draw) -> None:
    rays = "".join(
        f"M{20 + 10.5 * math.cos(a):.2f} {20 + 10.5 * math.sin(a):.2f}L{20 + 15.5 * math.cos(a):.2f} {20 + 15.5 * math.sin(a):.2f}"
        for a in (math.pi * k / 4 for k in range(8))
    )
    d.path(rays, stroke="main", width=2.6)
    d.circle(20, 20, 7.2, fill="main")
    d.path("M20 12.8a7.2 7.2 0 0 1 0 14.4z", fill="mid")


def s_camera(d: Draw) -> None:
    d.path("M13 11.5l2.5-4.5h9l2.5 4.5", fill="main", stroke="main")
    d.rect(4.5, 11, 31, 22, 4, fill="main")
    d.circle(20, 22, 7.4, fill="tint")
    d.circle(20, 22, 3.8, fill="mid")
    d.rect(27.5, 14, 4.5, 2.6, 1, fill="tint")


def s_negative(d: Draw) -> None:
    d.rect(4.5, 8.5, 31, 23, 2.5, fill="main")
    holes = "".join(f"M{x:g} 11h2M{x:g} 29h2" for x in (8, 13, 18, 23, 28))
    d.path(holes, stroke="tint", width=1.8)
    for x in (7.5, 20.5):
        d.rect(x, 14, 12, 12, 1, fill="tint")
        d.path(f"M{x + 1:g} 25l3.6-4.2 2.6 2.6 1.8-1.8 3 3.4z", fill="mid")
        d.circle(x + 8.5, 17.5, 1.4, fill="mid")


def s_bezier(d: Draw) -> None:
    d.path("M7 31V18M33 9v13", stroke="mid", width=1.6)
    d.circle(7, 17, 2.2, fill="mid")
    d.circle(33, 23, 2.2, fill="mid")
    d.path("M7 31C7 18 33 22 33 9", stroke="main", width=2.8)
    d.rect(4.2, 28.2, 5.6, 5.6, 1, fill="tint", stroke="main", width=1.8)
    d.rect(30.2, 6.2, 5.6, 5.6, 1, fill="tint", stroke="main", width=1.8)


def s_polaroid(d: Draw) -> None:
    d.rect(6.5, 4.5, 27, 31, 2.5, fill="tint", stroke="main")
    scene(d, 10.5, 8.5, 19, 17, 1, frame="mid", sun="tint", outline=False)
    d.path("M14 30.5h8", stroke="mid", width=2)


def s_shapes(d: Draw) -> None:
    d.circle(14, 14, 8.5, fill="tint", stroke="main")
    d.rect(18.5, 18.5, 16, 16, 2.5, fill="main")
    d.path("M4.5 34.5l5.5-9 5.5 9z", fill="mid", stroke="mid", width=1.4)


# audio


def bars(d: Draw, heights: list[float], x0: float, step: float, cy: float, role: str, width: float) -> None:
    d.path("".join(f"M{x0 + i * step:g} {cy - h / 2:g}v{h:g}" for i, h in enumerate(heights)), stroke=role, width=width)


def s_waveform(d: Draw) -> None:
    bars(d, [6, 14, 24, 30, 18, 10, 20, 8], 5.5, 4.15, 20, "main", 2.8)


def s_speaker(d: Draw) -> None:
    d.path("M5.5 15h5l7.5-6.5v23L10.5 25h-5z", fill="main", stroke="main")
    d.path("M23 14.5a8 8 0 0 1 0 11", stroke="main", width=2.6)
    d.path("M28 10a14.5 14.5 0 0 1 0 20", stroke="mid", width=2.6)


def s_fish(d: Draw) -> None:
    d.path("M4.5 20c3.5-6 9-9 16-9 4.5 0 7.5 2.5 10 5.5l5-4.5v16l-5-4.5c-2.5 3-5.5 5.5-10 5.5-7 0-12.5-3-16-9z",
           fill="main")
    d.circle(11, 18.5, 1.8, fill="tint")
    d.path("M16 14.5c1.6 3.6 1.6 7.4 0 11", stroke="tint", width=1.8)
    d.path("M21 15.5c1 2.8 1 6.2 0 9", stroke="mid", width=1.6)


def note(d: Draw, role: str) -> None:
    d.path("M23 10.5V25", stroke=role, width=2.6)
    d.path("M23 10.5c1.4 2.4 5.2 3.4 5.2 7.4", stroke=role, width=2.4)
    d.circle(19.5, 25.4, 3.8, fill=role)


def s_note_circle(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    note(d, "tint")


def s_note_squircle(d: Draw) -> None:
    d.rect(4.5, 4.5, 31, 31, 9, fill="main")
    note(d, "tint")


def s_equalizer(d: Draw) -> None:
    d.path("M10 6.5v27M20 6.5v27M30 6.5v27", stroke="mid", width=2.4)
    for x, y in ((10, 24), (20, 13), (30, 20)):
        d.rect(x - 4, y - 2.6, 8, 5.2, 1.8, fill="main")


def s_wave_squircle(d: Draw) -> None:
    d.rect(4.5, 4.5, 31, 31, 9, fill="main")
    bars(d, [6, 12, 18, 12, 16, 8], 10, 4, 20, "tint", 2.4)


def s_piano(d: Draw) -> None:
    d.rect(4.5, 7.5, 31, 25, 3, fill="tint", stroke="main")
    d.path("M12.25 7.5v25M20 7.5v25M27.75 7.5v25", stroke="main", width=1.6)
    for x in (12.25, 20, 27.75):
        d.rect(x - 2.2, 7.5, 4.4, 14, 1, fill="main")


def s_opus(d: Draw) -> None:
    d.circle(20, 20, 12.5, stroke="main", width=4)
    d.path("M4 20c2.7-5 5.3-5 8 0s5.3 5 8 0 5.3-5 8 0 5.3 5 8 0", stroke="mid", width=2.4)


def s_microphone(d: Draw) -> None:
    d.rect(14, 4.5, 12, 19, 6, fill="main")
    d.path("M14 11.5h5M14 15.5h5", stroke="tint", width=1.6)
    d.path("M9 18a11 11 0 0 0 22 0", stroke="main")
    d.path("M20 29v6M14 35.5h12", stroke="main")


def s_monkey(d: Draw) -> None:
    d.circle(7.5, 18, 4.5, fill="mid", stroke="main", width=2)
    d.circle(32.5, 18, 4.5, fill="mid", stroke="main", width=2)
    d.circle(20, 19.5, 12.5, fill="main")
    d.circle(15.6, 17, 4.4, fill="tint")
    d.circle(24.4, 17, 4.4, fill="tint")
    d.ellipse(20, 25.5, 7.6, 5.6, fill="tint")
    d.circle(15.8, 17.6, 1.5, fill="main")
    d.circle(24.2, 17.6, 1.5, fill="main")
    d.path("M17 26.5c2 1.6 4 1.6 6 0", stroke="main", width=1.6)


def s_wave_box(d: Draw) -> None:
    d.path("M5 14l4-7h22l4 7z", fill="mid", stroke="main")
    d.rect(5, 14, 30, 21, 3, fill="tint", stroke="main")
    bars(d, [4, 9, 13, 7, 11, 5], 10, 4, 24.5, "main", 2.4)


def s_matroska(d: Draw) -> None:
    d.path(
        "M20 4.5c-4 0-6.6 3-6.6 6.6 0 1.6.5 3 1.3 4-4 2.2-6.4 6.2-6.4 11 0 5.8 4.9 9.4 11.7 9.4s11.7-3.6 11.7-9.4"
        "c0-4.8-2.4-8.8-6.4-11 .8-1 1.3-2.4 1.3-4 0-3.6-2.6-6.6-6.6-6.6z",
        fill="main",
    )
    d.circle(20, 11.2, 3.7, fill="tint")
    d.path("M12.6 20.4c4.6 1.6 10.2 1.6 14.8 0", stroke="tint", width=1.4)
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        d.circle(round(20 + 3 * math.cos(a), 2), round(27.5 + 3 * math.sin(a), 2), 2.2, fill="mid")
    d.circle(20, 27.5, 1.5, fill="tint")


def s_surround(d: Draw) -> None:
    d.circle(20, 20, 13, stroke="mid", width=1.6)
    d.circle(20, 17.5, 3.2, fill="main")
    d.path("M14.5 26.5c0-3.2 2.5-5 5.5-5s5.5 1.8 5.5 5z", fill="main")
    for angle in (-150, -90, -30, 30, 150):
        a = math.radians(angle)
        x, y = round(20 + 13 * math.cos(a), 2), round(20 + 13 * math.sin(a), 2)
        d.circle(x, y, 3.8, fill="main", stroke="tint", width=1.6)
        d.circle(x, y, 1.3, fill="tint")


def s_speaker_cabinet(d: Draw) -> None:
    d.rect(9, 4.5, 22, 31, 3, fill="tint", stroke="main")
    d.circle(20, 12, 3, fill="main")
    d.circle(20, 24.5, 7, fill="main")
    d.circle(20, 24.5, 2.6, fill="mid")


def s_vinyl(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.circle(20, 20, 12, stroke="mid", width=1)
    d.circle(20, 20, 9, stroke="mid", width=1)
    d.circle(20, 20, 5.2, fill="tint")
    d.circle(20, 20, 1.3, fill="main")


def s_telephone(d: Draw) -> None:
    d.path("M10.5 6.5c-2.5 0-4.5 2-4.5 4.5 0 12.7 10.3 23 23 23 2.5 0 4.5-2 4.5-4.5V26l-7-2.6-3.2 3.2"
           "c-4.4-2-7.9-5.5-9.9-9.9l3.2-3.2L14 6.5z", fill="main", stroke="main", width=1.6)
    d.path("M24 6.5a9.5 9.5 0 0 1 9.5 9.5M24 11.5a4.5 4.5 0 0 1 4.5 4.5", stroke="mid", width=2.2)


def playlist_note(d: Draw) -> None:
    d.path("M30.5 13v15", stroke="main", width=2.6)
    d.path("M30.5 13c1.4 1.8 4.6 2.6 4.6 6", stroke="main", width=2.2)
    d.circle(27, 28.5, 3.8, fill="main")


def s_playlist(d: Draw) -> None:
    d.path("M5 9h21M5 16h17M5 23h12", stroke="main", width=2.6)
    d.path("M5 30h12", stroke="mid", width=2.6)
    playlist_note(d)


def s_playlist_play(d: Draw) -> None:
    for y in (9, 20, 31):
        d.path(f"M5 {y - 3.4:g}v6.8l5.6-3.4z", fill="main", stroke="main", width=1.2)
        d.path(f"M15 {y:g}h20", stroke="main" if y == 9 else "mid", width=2.6)


def s_sound_bank(d: Draw) -> None:
    d.rect(4.5, 5, 31, 30, 3.5, fill="tint", stroke="main")
    wave = "c2-3.2 4-3.2 6 0s4 3.2 6 0 4-3.2 6 0 4 3.2 6 0"
    d.path(f"M8 13{wave}M8 27{wave}", stroke="main", width=2.2)
    d.path(f"M8 20{wave}", stroke="mid", width=2.2)


def s_sfz(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.path("M21.5 13v12", stroke="mid", width=2.4)
    d.path("M21.5 13c1 1.6 3 2 3 4.4", stroke="mid", width=2)
    d.circle(19, 25.3, 2.8, fill="mid")


def s_ableton(d: Draw) -> None:
    d.path("M5.5 8v24M10.5 8v24M15.5 8v24M20.5 8v24", stroke="main", width=2.6)
    d.path("M25 8h10M25 16h10M25 24h10M25 32h10", stroke="main", width=2.6)


def s_fruit(d: Draw) -> None:
    d.path("M20 13.5c-7 0-12 4-12 9.5 0 6.8 6.8 12.5 12 12.5s12-5.7 12-12.5c0-5.5-5-9.5-12-9.5z", fill="main")
    d.path("M20 13.5c-2-3.6-6-5.6-10-5 2 3.2 6 5 10 5zM20 13.5c2-3.6 6-5.6 10-5-2 3.2-6 5-10 5z", fill="mid")
    d.path("M20 13.5V4.5", stroke="mid", width=2.2)
    for x, y in ((15, 20), (20, 19), (25, 20), (13.5, 25.5), (18, 25), (22.5, 25), (26.5, 25.5), (16, 30), (24, 30),
                 (20, 30.5)):
        d.circle(x, y, 1, fill="tint")


def s_metronome(d: Draw) -> None:
    d.path("M15 4.5h10l6.5 30.5h-23z", fill="tint", stroke="main")
    d.path("M10 28h20", stroke="main")
    d.path("M20 28L28.5 8", stroke="main", width=2.4)
    d.rect(23.6, 13.4, 5, 3.6, 1, fill="main")
    d.path("M15.5 12h3M14.5 17h3M13.5 22h3", stroke="mid", width=1.6)


def s_console(d: Draw) -> None:
    d.path("M8 13l3.5-6.5h17L32 13z", fill="mid", stroke="main")
    d.rect(4.5, 13, 31, 21, 3, fill="tint", stroke="main")
    for x in (11, 20, 29):
        d.circle(x, 18, 2, fill="main")
        d.path(f"M{x:g} 23v7.5", stroke="mid", width=2)
    for x, y in ((11, 28), (20, 25), (29, 27)):
        d.rect(x - 2.6, y - 1.5, 5.2, 3, 1, fill="main")


def s_cubase(d: Draw) -> None:
    d.path("M30.5 11.5a13.5 13.5 0 1 0 0 17", stroke="main", width=4)
    d.path("M12.5 20c1.5-4 3-4 4.5 0s3 4 4.5 0 3-4 4.5 0", stroke="mid", width=2.4)


def s_knob(d: Draw) -> None:
    ticks = "".join(
        f"M{20 + 14 * math.cos(a):.2f} {20 + 14 * math.sin(a):.2f}L{20 + 16 * math.cos(a):.2f} {20 + 16 * math.sin(a):.2f}"
        for a in (math.radians(135 + 30 * k) for k in range(10))
    )
    d.path(ticks, stroke="mid", width=2)
    d.circle(20, 20, 11, fill="main")
    d.path("M20 20l-5.6-5.6", stroke="tint", width=2.6)


def s_headphones_wave(d: Draw) -> None:
    d.path("M7.5 24v-4a12.5 12.5 0 0 1 25 0v4", stroke="main", width=3)
    d.rect(4.5, 22, 6.5, 12, 2.5, fill="main")
    d.rect(29, 22, 6.5, 12, 2.5, fill="main")
    bars(d, [5, 10, 6, 12, 7], 14, 3, 27, "mid", 2.2)


def s_guitar(d: Draw) -> None:
    d.path("M21 19L32.5 7.5", stroke="main", width=3)
    d.path(rotated([(-2, -3.6), (2, -3.6), (2, 3.6), (-2, 3.6)], 45, 33.4, 6.6), fill="main")
    d.circle(19.5, 20.5, 5.6, fill="main")
    d.circle(14, 26, 8.6, fill="main")
    d.circle(15.6, 24.4, 2.4, fill="tint")
    d.path("M9.5 27.5l3 3", stroke="mid", width=2)


# video


def s_quicktime(d: Draw) -> None:
    d.circle(18.5, 18.5, 12.5, fill="tint", stroke="main", width=4.4)
    d.path("M26.5 26.5l7.5 7.5", stroke="main", width=4.4)
    d.path("M15.5 12.5v12l9.5-6z", fill="main", stroke="main", width=1.4)


def s_film_reel(d: Draw) -> None:
    d.path("M20 35.5h15.5", stroke="mid", width=2.4)
    d.circle(20, 20, 15.5, fill="main")
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        d.circle(round(20 + 8.6 * math.cos(a), 2), round(20 + 8.6 * math.sin(a), 2), 3.6, fill="tint")
    d.circle(20, 20, 1.8, fill="tint")


def s_play_tile(d: Draw) -> None:
    d.rect(4.5, 4.5, 31, 31, 8, fill="tint", stroke="main")
    d.path("M16 12.5v15l12-7.5z", fill="main", stroke="main", width=1.8)


def s_flash(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 5, fill="main")
    d.path("M27 11.5c-5.4 0-7.5 2.6-7.5 7.4v11.6M14 19.5h11", stroke="tint", width=3.4)


def s_monitor_play(d: Draw) -> None:
    d.rect(4.5, 5.5, 31, 22, 3, fill="tint", stroke="main")
    d.path("M20 27.5v5M13 34.5h14", stroke="main")
    d.path("M17 11.5v10l8.5-5z", fill="main", stroke="main", width=1.6)


def s_clapper(d: Draw) -> None:
    d.rect(5, 16.5, 30, 18.5, 2.5, fill="main")
    d.path("M5.4 13.8l28.4-7.6 1.2 4.4-28.4 7.6z", fill="main", stroke="main", width=1.6)
    d.path("M11 12.4l3.6 3.2M18.2 10.4l3.6 3.2M25.4 8.5l3.6 3.2", stroke="tint", width=2.2)
    d.path("M17 21v9l7.5-4.5z", fill="tint")


def s_movie_camera(d: Draw) -> None:
    d.circle(10.5, 11, 5.5, fill="tint", stroke="main")
    d.circle(21.5, 11, 5.5, fill="tint", stroke="main")
    d.rect(4.5, 17, 23, 15, 3, fill="main")
    d.path("M27.5 21.5l8-4.5v15l-8-4.5z", fill="mid", stroke="main", width=1.8)


def s_stream(d: Draw) -> None:
    d.path("M5.5 12v16l12.5-8z", fill="main", stroke="main", width=1.8)
    d.path("M23 13a9.5 9.5 0 0 1 0 14", stroke="main", width=2.6)
    d.path("M28.5 8.5a16 16 0 0 1 0 23", stroke="mid", width=2.6)


def s_real(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.path("M15.5 28.5V15.5M15.5 20c1.6-3 4.6-4.6 9-4.5", stroke="tint", width=3.4)


def s_adaptive(d: Draw) -> None:
    for i, (h, role) in enumerate(((8, "mid"), (14, "mid"), (20, "main"), (27, "main"))):
        d.rect(5 + i * 8, 34 - h, 6, h, 1.6, fill=role)
    d.path("M5 13.5v-8l6.5 4z", fill="main")


def s_broadcast(d: Draw) -> None:
    d.path("M20 16v18M13.5 35.5L20 16l6.5 19.5M15.6 29h8.8", stroke="main")
    d.circle(20, 12.5, 3.2, fill="main")
    d.path("M13.2 7.5a9 9 0 0 0 0 10M26.8 7.5a9 9 0 0 1 0 10", stroke="mid", width=2.2)
    d.path("M8.5 4a15 15 0 0 0 0 17M31.5 4a15 15 0 0 1 0 17", stroke="mid", width=2.2)


def s_camcorder(d: Draw) -> None:
    d.rect(4.5, 12, 22, 16, 3, fill="main")
    d.path("M26.5 16.5l9-4.5v16l-9-4.5z", fill="mid", stroke="main", width=1.8)
    d.rect(8, 6, 10, 6, 1.2, fill="mid", stroke="main", width=1.6)
    d.circle(10.5, 20, 2.2, fill="tint")
    d.path("M15 31.5h8", stroke="main", width=2.6)


# fonts


def s_font_tt(d: Draw) -> None:
    d.path("M5 9h17M13.5 9v22", stroke="main", width=3.4)
    d.path("M27 14v13.5a3 3 0 0 0 3 3h3.5M23.5 19h9", stroke="mid", width=2.8)


AMPERSAND = (
    "M30.5 33L15 16c-2-2.3-2.5-3.5-2.5-5 0-3 2.4-5 5.3-5s5.2 2 5.2 4.8c0 2.6-2 4.2-5.5 6.4"
    "-4.2 2.6-7 4.7-7 8.6 0 4 3.3 7.2 8 7.2 4.6 0 8-3 10.5-8.5"
)


def s_ampersand(d: Draw) -> None:
    d.path(AMPERSAND, stroke="main", width=3.2)


def s_font_tile(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 5, fill="main")
    d.path("M12 29l8-19 8 19M15.2 23h9.6", stroke="tint", width=3)


def card_stack(d: Draw) -> None:
    d.rect(13, 4.5, 22, 24, 3, fill="tint", stroke="main", width=1.8)
    d.rect(9, 8, 22, 24, 3, fill="tint", stroke="main", width=1.8)
    d.rect(5, 11.5, 22, 24, 3, fill="tint", stroke="main")


def s_stack_t(d: Draw) -> None:
    card_stack(d)
    d.path("M10 17.5h12M16 17.5v13", stroke="main", width=3)


def s_stack_o(d: Draw) -> None:
    card_stack(d)
    d.circle(16, 23.5, 6, stroke="main", width=3)


PIXEL_A = [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"]


def pixel_a(d: Draw, role: str) -> None:
    for r, line in enumerate(PIXEL_A):
        for c, ch in enumerate(line):
            if ch == "X":
                d.rect(round(11.6 + c * 3.4, 2), round(8.3 + r * 3.4, 2), 3.1, 3.1, 0.4, fill=role)


def s_pixel_font(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 3.5, fill="tint", stroke="main")
    pixel_a(d, "main")


def s_pixel_font_tile(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 5, fill="main")
    pixel_a(d, "tint")


def s_glyph_outline(d: Draw) -> None:
    d.path("M7.5 33.5L16.5 6.5h7l9 27h-6.5L24 27.5h-8l-2 6zM17.6 22h4.8L20 14z", fill="tint", stroke="main", width=1.8)
    for x, y in ((7.5, 33.5), (16.5, 6.5), (23.5, 6.5), (32.5, 33.5)):
        d.rect(x - 1.8, y - 1.8, 3.6, 3.6, 0.6, fill="main")


SYMBOLS.update(
    {
        "photo-alpha": s_photo_alpha,
        "frames": s_frames,
        "pixel-art": s_pixel_art,
        "icon-sizes": s_icon_sizes,
        "icon-squircles": s_icon_squircles,
        "cursor": s_cursor,
        "crop": s_crop,
        "phone-photo": s_phone_photo,
        "phone-play": s_phone_play,
        "photo-circle": s_photo_circle,
        "photo-hexagon": s_photo_hexagon,
        "photo-wave": s_photo_wave,
        "target": s_target,
        "paintbrush": s_paintbrush,
        "pixels-bw": s_pixels_bw,
        "pixels-gray": s_pixels_gray,
        "pixels-color": s_pixels_color,
        "gpu-chip": s_gpu_chip,
        "mipmaps": s_mipmaps,
        "aperture": s_aperture,
        "sun-hdr": s_sun_hdr,
        "camera": s_camera,
        "negative": s_negative,
        "bezier": s_bezier,
        "polaroid": s_polaroid,
        "shapes": s_shapes,
        "waveform": s_waveform,
        "speaker": s_speaker,
        "xiph-fish": s_fish,
        "note-circle": s_note_circle,
        "note-squircle": s_note_squircle,
        "equalizer": s_equalizer,
        "wave-squircle": s_wave_squircle,
        "piano": s_piano,
        "opus-ring": s_opus,
        "microphone": s_microphone,
        "monkey": s_monkey,
        "wave-box": s_wave_box,
        "matroska": s_matroska,
        "surround": s_surround,
        "speaker-cabinet": s_speaker_cabinet,
        "vinyl": s_vinyl,
        "telephone": s_telephone,
        "playlist": s_playlist,
        "playlist-play": s_playlist_play,
        "sound-bank": s_sound_bank,
        "sfz-braces": s_sfz,
        "ableton": s_ableton,
        "fruit": s_fruit,
        "metronome": s_metronome,
        "console": s_console,
        "cubase": s_cubase,
        "knob": s_knob,
        "headphones-wave": s_headphones_wave,
        "guitar": s_guitar,
        "quicktime": s_quicktime,
        "film-reel": s_film_reel,
        "play-tile": s_play_tile,
        "flash": s_flash,
        "monitor-play": s_monitor_play,
        "clapper": s_clapper,
        "movie-camera": s_movie_camera,
        "stream": s_stream,
        "real": s_real,
        "adaptive": s_adaptive,
        "broadcast": s_broadcast,
        "camcorder": s_camcorder,
        "font-tt": s_font_tt,
        "ampersand": s_ampersand,
        "font-tile": s_font_tile,
        "stack-t": s_stack_t,
        "stack-o": s_stack_o,
        "pixel-font": s_pixel_font,
        "pixel-font-tile": s_pixel_font_tile,
        "glyph-outline": s_glyph_outline,
    }
)

ICONS.update(
    {
        # img
        "png": ("photo-alpha", None),
        "jpg": ("image", None),
        "jpeg": ("image", None),
        "gif": ("frames", None),
        "webp": ("image", "web"),
        "bmp": ("pixel-art", None),
        "ico": ("icon-sizes", None),
        "icns": ("icon-squircles", None),
        "cur": ("cursor", None),
        "tiff": ("crop", None),
        "tif": ("crop", None),
        "heic": ("phone-photo", None),
        "heif": ("phone-photo", None),
        "avif": ("photo-circle", None),
        "jxl": ("photo-hexagon", None),
        "jp2": ("photo-wave", None),
        "tga": ("target", None),
        "pcx": ("paintbrush", None),
        "pbm": ("pixels-bw", None),
        "pgm": ("pixels-gray", None),
        "ppm": ("pixels-color", None),
        "dds": ("gpu-chip", None),
        "ktx": ("mipmaps", None),
        "ktx2": ("mipmaps", "plus"),
        "exr": ("aperture", None),
        "hdr": ("sun-hdr", None),
        "raw": ("camera", None),
        "cr2": ("camera", "letter-C"),
        "cr3": ("camera", "letter-C"),
        "nef": ("camera", "letter-N"),
        "arw": ("camera", "letter-alpha"),
        "dng": ("negative", None),
        "orf": ("camera", "letter-O"),
        "raf": ("camera", "letter-F"),
        "rw2": ("camera", "letter-L"),
        "svg": ("bezier", None),
        "svgz": ("bezier", "spring"),
        "img": ("polaroid", None),
        "wmf": ("shapes", None),
        "emf": ("shapes", "plus"),
        # audio
        "mp3": ("audio", None),
        "wav": ("waveform", None),
        "flac": ("waveform", "gem"),
        "aac": ("speaker", None),
        "ogg": ("xiph-fish", None),
        "m4a": ("note-circle", None),
        "wma": ("equalizer", None),
        "aiff": ("wave-squircle", None),
        "aif": ("wave-squircle", None),
        "mid": ("piano", None),
        "midi": ("piano", None),
        "opus": ("opus-ring", None),
        "amr": ("microphone", None),
        "ape": ("monkey", None),
        "alac": ("note-squircle", "gem"),
        "wv": ("wave-box", None),
        "mka": ("matroska", "note"),
        "ac3": ("surround", None),
        "dts": ("speaker-cabinet", None),
        "caf": ("vinyl", None),
        "au": ("telephone", None),
        "m3u": ("playlist", None),
        "m3u8": ("playlist", "web"),
        "pls": ("playlist-play", None),
        "sf2": ("sound-bank", None),
        "sfz": ("sfz-braces", None),
        "als": ("ableton", None),
        "flp": ("fruit", None),
        "logicx": ("metronome", None),
        "ptx": ("console", None),
        "cpr": ("cubase", None),
        "rpp": ("knob", None),
        "aup3": ("headphones-wave", None),
        "band": ("guitar", None),
        # video
        "mp4": ("video", None),
        "mov": ("quicktime", None),
        "avi": ("film-reel", None),
        "mkv": ("matroska", "play"),
        "webm": ("play-tile", "web"),
        "flv": ("flash", None),
        "wmv": ("monitor-play", None),
        "mpeg": ("clapper", None),
        "mpg": ("clapper", None),
        "m4v": ("video-play", None),
        "3gp": ("phone-play", None),
        "m2ts": ("disc", "play"),
        "ogv": ("xiph-fish", "play"),
        "vob": ("folder", "play"),
        "divx": ("movie-camera", None),
        "asf": ("stream", None),
        "rm": ("real", None),
        "rmvb": ("real", "bars"),
        "mpd": ("adaptive", None),
        "ts-stream": ("broadcast", None),
        "mts-video": ("camcorder", None),
        # font
        "ttf": ("font-tt", None),
        "otf": ("ampersand", None),
        "woff": ("font", "web"),
        "woff2": ("font", "plus"),
        "eot": ("font-tile", None),
        "ttc": ("stack-t", None),
        "otc": ("stack-o", None),
        "fon": ("pixel-font-tile", None),
        "bdf": ("pixel-font", None),
        "pcf": ("pixel-font", "binary"),
        "pfb": ("glyph-outline", None),
    }
)


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
