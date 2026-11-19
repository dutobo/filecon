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
    elif glyph.startswith("text-"):
        text_badge(d, glyph[len("text-") :])
    elif glyph == "comment":
        d.path("M28.4 34.6l2.6-7.2M31.8 34.6l2.6-7.2", stroke="tint", width=1.6)
    elif glyph == "link":
        d.path("M30 32.6l-1.2 1.2a2 2 0 0 1-2.8-2.8l2-2a2 2 0 0 1 2.8 0M32 29.4l1.2-1.2a2 2 0 0 1 2.8 2.8l-2 2"
               "a2 2 0 0 1-2.8 0M29.4 32.6l3.2-3.2", stroke="tint", width=1.3)
    elif glyph == "ban":
        d.circle(31, 31, 3.8, stroke="tint", width=1.6)
        d.path("M28.3 33.7l5.4-5.4", stroke="tint", width=1.6)
    elif glyph == "gear":
        d.path(gear_path(31, 31, 4.4, 3.3, 8), fill="tint")
        d.circle(31, 31, 1.3, fill="main")
    elif glyph == "search":
        d.circle(30.2, 30.2, 2.6, stroke="tint", width=1.6)
        d.path("M32.2 32.2l2.4 2.4", stroke="tint", width=1.8)
    elif glyph == "download":
        d.path("M31 27v5.4M28.4 29.8l2.6 2.6 2.6-2.6M27.6 35h6.8", stroke="tint", width=1.6)
    elif glyph == "lock":
        d.rect(28, 30, 6, 4.6, 1, fill="tint")
        d.path("M29.2 30v-1.4a1.8 1.8 0 0 1 3.6 0V30", stroke="tint", width=1.4)
    elif glyph == "key":
        d.circle(29, 31, 2.2, stroke="tint", width=1.5)
        d.path("M31.2 31h4M33.6 31v1.8", stroke="tint", width=1.5)
    elif glyph == "arrow":
        d.path("M27.4 31h7.2M31.8 28.2l2.8 2.8-2.8 2.8", stroke="tint", width=1.6)
    elif glyph == "braces":
        d.path("M29.4 27.4c-1.2 0-1.6.5-1.6 1.6v.8c0 .7-.4 1.1-1 1.2.6.1 1 .5 1 1.2v.8c0 1.1.4 1.6 1.6 1.6"
               "M32.6 27.4c1.2 0 1.6.5 1.6 1.6v.8c0 .7.4 1.1 1 1.2-.6.1-1 .5-1 1.2v.8c0 1.1-.4 1.6-1.6 1.6",
               stroke="tint", width=1.3)
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
    "A": "M8.6 24.5l4.4-9 4.4 9M10.2 21.4h5.6",
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


# ------------------------------------------------------------------ block 4a: programming languages

# Minimal stroke font in a 4x6 box (absolute M/L/H/V/Q/Z only), for letter marks and letter badges.
FONT = {
    "A": "M0 6L2 0L4 6M0.7 4H3.3",
    "B": "M0 3H2.3Q3.7 3 3.7 1.5Q3.7 0 2.3 0H0V6H2.5Q4 6 4 4.5Q4 3 2.5 3",
    "C": "M4 0.9Q3.3 0 2.1 0Q0 0 0 3Q0 6 2.1 6Q3.3 6 4 5.1",
    "D": "M0 0V6H1.7Q4 6 4 3Q4 0 1.7 0Z",
    "E": "M4 0H0V6H4M0 3H3",
    "F": "M4 0H0V6M0 3H3",
    "G": "M4 0.9Q3.3 0 2.1 0Q0 0 0 3Q0 6 2.1 6Q4 6 4 3.6H2.2",
    "H": "M0 0V6M4 0V6M0 3H4",
    "I": "M0.9 0H3.1M2 0V6M0.9 6H3.1",
    "J": "M1 0H4V4.2Q4 6 2.1 6Q0.6 6 0 4.9",
    "L": "M0 0V6H4",
    "M": "M0 6V0L2 3.6L4 0V6",
    "P": "M0 6V0H2.3Q4 0 4 1.75Q4 3.5 2.3 3.5H0",
    "R": "M0 6V0H2.3Q4 0 4 1.75Q4 3.5 2.3 3.5H0M2.2 3.5L4 6",
    "S": "M3.9 0.9Q3.2 0 2 0Q0.2 0 0.2 1.6Q0.2 3 2 3Q3.8 3 3.8 4.4Q3.8 6 2 6Q0.7 6 0 5.1",
    "T": "M0 0H4M2 0V6",
    "V": "M0 0L2 6L4 0",
    "W": "M0 0L1 6L2 2.4L3 6L4 0",
    "+": "M2 1.2V4.8M0.2 3H3.8",
    "#": "M1.4 0.4L0.9 5.6M3.1 0.4L2.6 5.6M0 2H4M0 4H4",
    "0": "M2 0Q0 0 0 3Q0 6 2 6Q4 6 4 3Q4 0 2 0Z",
    "1": "M0.8 1.2L2.4 0V6",
    "3": "M0.2 0.6Q0.9 0 2 0Q3.8 0 3.8 1.5Q3.8 3 2 3Q4 3 4 4.5Q4 6 2 6Q0.8 6 0 5.3M1.4 3H2",
    "5": "M3.8 0H0.5L0.3 2.7Q1 2.3 2 2.3Q4 2.3 4 4.1Q4 6 2 6Q0.7 6 0 5.2",
    "K": "M0 0V6M4 0L0 3.8M1.5 2.6L4 6",
    "N": "M0 6V0L4 6V0",
    "U": "M0 0V4Q0 6 2 6Q4 6 4 4V0",
    "X": "M0 0L4 6M4 0L0 6",
    "$": "M3.8 1.1Q3.2 0.5 2 0.5Q0.3 0.5 0.3 1.9Q0.3 3 2 3Q3.7 3 3.7 4.2Q3.7 5.5 2 5.5Q0.7 5.5 0.1 4.8M2 0V6",
    "%": "M0 6L4 0M1 0.5Q0 0.5 0 1.5Q0 2.5 1 2.5Q2 2.5 2 1.5Q2 0.5 1 0.5ZM3 3.5Q2 3.5 2 4.5Q2 5.5 3 5.5"
    "Q4 5.5 4 4.5Q4 3.5 3 3.5Z",
}


def map_path(path: str, fx, fy) -> str:
    """Maps an absolute path (M/L/H/V/Q/C/Z) through axis-aligned functions fx and fy."""
    out = []
    for cmd, args in re.findall(r"([MLHVQCZ])([^MLHVQCZ]*)", path):
        nums = [float(n) for n in re.findall(r"-?\d*\.?\d+", args)]
        if cmd == "H":
            vals = [fx(n) for n in nums]
        elif cmd == "V":
            vals = [fy(n) for n in nums]
        else:
            vals = [fx(n) if i % 2 == 0 else fy(n) for i, n in enumerate(nums)]
        out.append(cmd + " ".join(f"{v:.2f}".rstrip("0").rstrip(".") for v in vals))
    return "".join(out)


def text_path(text: str, cx: float, cy: float, h: float, gap: float = 1.5) -> str:
    s = h / 6
    width = (len(text) * 4 + (len(text) - 1) * gap) * s
    x0, y0 = cx - width / 2, cy - h / 2
    parts = []
    for i, ch in enumerate(text):
        ox = x0 + i * (4 + gap) * s
        parts.append(map_path(FONT[ch], lambda x, ox=ox: ox + x * s, lambda y: y0 + y * s))
    return "".join(parts)


def text(d: Draw, value: str, cx: float, cy: float, h: float, role: str, width: float) -> None:
    d.path(text_path(value, cx, cy, h), stroke=role, width=width)


def text_badge(d: Draw, value: str) -> None:
    h = 6 if len(value) == 1 else 4.4
    d.path(text_path(value, BADGE_C, BADGE_C, h, gap=1.2), stroke="tint", width=1.6)


def tile(d: Draw, rx: float = 5) -> None:
    d.rect(4.5, 4.5, 31, 31, rx, fill="main")


def letter_tile(value: str):
    def draw(d: Draw) -> None:
        tile(d)
        h = {1: 15, 2: 12, 3: 9, 4: 7}[len(value)]
        text(d, value, 20, 20, h, "tint", 3 if len(value) < 3 else 2.6)

    return draw


def s_js_tile(d: Draw) -> None:
    tile(d, 4)
    text(d, "JS", 19.5, 25.5, 10, "tint", 2.6)


def s_ts_tile(d: Draw) -> None:
    tile(d, 4)
    text(d, "TS", 19.5, 25.5, 10, "tint", 2.6)


def s_react_atom(d: Draw) -> None:
    arcs = []
    for deg in (0, 60, 120):
        a = math.radians(deg)
        px, py = 20 + 15.5 * math.cos(a), 20 + 15.5 * math.sin(a)
        qx, qy = 40 - px, 40 - py
        arcs.append(f"M{px:.2f} {py:.2f}A15.5 6 {deg} 1 0 {qx:.2f} {qy:.2f}A15.5 6 {deg} 1 0 {px:.2f} {py:.2f}")
    d.path("".join(arcs), stroke="main", width=2.2)
    d.circle(20, 20, 3.2, fill="main")


def s_vue(d: Draw) -> None:
    d.path("M3.5 7h7.2L20 23l9.3-16h7.2L20 35z", fill="main", stroke="main", width=1.4)
    d.path("M10.7 7H16l4 6.9L24 7h5.3L20 23z", fill="mid")


def s_svelte(d: Draw) -> None:
    d.path(rotated([(-8.5, -13), (8.5, -13), (8.5, 13), (-8.5, 13)], 30, 20, 20), fill="main", stroke="main", width=5)
    d.path("M24.5 13.5c-2.6-2.2-7-1.6-8 1-1 2.6 1.2 4.2 3.6 5.2s4.6 2.6 3.6 5.2c-1 2.6-5.4 3.2-8 1",
           stroke="tint", width=2.6)


def s_astro(d: Draw) -> None:
    d.path("M12.5 27.5L18 5.5h4l5.5 22c-2.2-1.6-4.7-2.4-7.5-2.4s-5.3.8-7.5 2.4z", fill="main", stroke="main", width=1.4)
    d.path("M15.5 29.5c.2 3 2 5 4.5 6.5 2.5-1.5 4.3-3.5 4.5-6.5-1.3.9-2.8 1.4-4.5 1.4s-3.2-.5-4.5-1.4z", fill="mid")


def s_paper_cup(d: Draw) -> None:
    d.rect(12, 4.5, 16, 4, 1.5, fill="main")
    d.path("M8.5 9h23l-.8 4.5H9.3z", fill="main", stroke="main", width=1.4)
    d.path("M10.5 13.5h19L27 35.5H13z", fill="tint", stroke="main")
    d.path("M11.6 20h16.8l-.8 7.5H12.4z", fill="mid")


def s_ejs(d: Draw) -> None:
    d.path("M14.5 9.5L5.5 20l9 10.5", stroke="main", width=3.2)
    d.circle(22.5, 13.5, 3, stroke="main", width=2.2)
    d.circle(31.5, 26.5, 3, stroke="main", width=2.2)
    d.path("M33.5 9.5l-13 21", stroke="mid", width=2.6)


def s_njk(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.circle(17.2, 15.6, 2, stroke="main", width=1.8)
    d.circle(22.8, 24.4, 2, stroke="main", width=1.8)
    d.path("M24 13l-8 14", stroke="mid", width=2.2)


def s_mustache(d: Draw) -> None:
    d.path(
        "M20 20.5c-2.5-4-6.5-5.5-10-3.5-2.5 1.5-3 4.5-1.2 6-2.4.4-4.3-.8-5.3-2.5 0 5 4.5 8 9.5 7 3.5-.7 5.5-3 7-7"
        " 1.5 4 3.5 6.3 7 7 5 1 9.5-2 9.5-7-1 1.7-2.9 2.9-5.3 2.5 1.8-1.5 1.3-4.5-1.2-6-3.5-2-7.5-.5-10 3.5z",
        fill="main",
    )


def s_pug_dog(d: Draw) -> None:
    d.path("M9 11.5c-3.2-.2-5.4 3-4.4 7.4l5-2.2zM31 11.5c3.2-.2 5.4 3 4.4 7.4l-5-2.2z", fill="main")
    d.circle(20, 21, 13, fill="mid")
    d.ellipse(20, 27, 8.5, 7, fill="main")
    d.circle(13.8, 18, 2.8, fill="main")
    d.circle(26.2, 18, 2.8, fill="main")
    d.circle(14.3, 17.4, 0.9, fill="tint")
    d.circle(26.7, 17.4, 0.9, fill="tint")
    d.ellipse(20, 24.2, 3.2, 2.1, fill="tint")
    d.path("M16.8 29c1.8 1.6 4.6 1.6 6.4 0", stroke="tint", width=1.6)


SNAKE = (
    "M20 4.5C13.5 4.5 11 7 11 11V15H20V16.5H8.5C5 16.5 4 19.5 4 23C4 26.5 5.5 29.5 9 29.5H12V25"
    "C12 21.5 14.7 19 18 19H25.5C28.5 19 30.5 16.5 30.5 13.5V11C30.5 7.4 26.7 4.5 20 4.5Z"
)


def s_python(d: Draw) -> None:
    d.path(SNAKE, fill="main")
    d.path(map_path(SNAKE, lambda x: 40 - x, lambda y: 40 - y), fill="mid")
    d.circle(15.3, 8.6, 1.5, fill="tint")
    d.circle(24.7, 31.4, 1.5, fill="tint")


def s_jupyter(d: Draw) -> None:
    d.path("M7 15.5c4.6-7.5 21.4-7.5 26 0", stroke="main", width=3.4)
    d.path("M7 24.5c4.6 7.5 21.4 7.5 26 0", stroke="main", width=3.4)
    d.circle(31.5, 6.5, 2.4, fill="mid")
    d.circle(8, 7.5, 1.7, fill="mid")
    d.circle(9, 33, 2.8, fill="mid")


def s_java_cup(d: Draw) -> None:
    d.path("M16.5 4c-2 2.5 2 4.5 0 7.5M22.5 4c-2 2.5 2 4.5 0 7.5", stroke="mid", width=2)
    d.path("M30 17.5h1.8a3.6 3.6 0 0 1 0 7.2H29", stroke="main", width=2.4)
    d.path("M8 15h22v6a9.5 9.5 0 0 1-9.5 9.5h-3A9.5 9.5 0 0 1 8 21z", fill="main")
    d.path("M5 34h28", stroke="main", width=2.6)


def s_kotlin(d: Draw) -> None:
    d.path("M5 5h30L20 20l15 15H5z", fill="main")
    d.path("M5 5h15L5 20z", fill="mid")


def s_scala(d: Draw) -> None:
    for i, y in enumerate((10, 20, 30)):
        role = "main" if i % 2 == 0 else "mid"
        d.path(rotated([(-11, -2.4), (11, -2.4), (11, 2.4), (-11, 2.4)], -12, 20, y), fill=role, stroke=role, width=2.4)


def s_groovy(d: Draw) -> None:
    d.path("M4.5 29c9 6.5 23 4 30.5-13", stroke="mid", width=2.6)
    d.path(star_path(18, 18, 11, 4.8, 5), fill="main", stroke="main", width=1.6)


def s_elephant(d: Draw) -> None:
    d.path("M9 19l-4 4", stroke="main", width=2.2)
    d.rect(8, 13, 22, 14, 7, fill="main")
    d.rect(10, 23, 5, 11, 1.8, fill="main")
    d.rect(22, 23, 5, 11, 1.8, fill="main")
    d.path("M33.5 17c2.4 3.4 2.4 8-1 10.5", stroke="main", width=3.2)
    d.circle(29, 15, 6.2, fill="main")
    d.ellipse(25.8, 15.4, 3.2, 4.2, fill="mid")
    d.circle(31.5, 12.8, 1.1, fill="tint")


HEXAGON = "M20 4L33.86 12V28L20 36L6.14 28V12Z"


def hex_mark(value: str, h: float):
    def draw(d: Draw) -> None:
        d.path(HEXAGON, fill="main", stroke="main", width=1.6)
        text(d, value, 20, 20, h, "tint", 2.8 if len(value) < 3 else 2.4)

    return draw


def s_objc(d: Draw) -> None:
    d.path("M11 7H6v26h5M29 7h5v26h-5", stroke="main", width=3)
    d.circle(20, 20, 3.4, stroke="mid", width=2.4)
    d.path("M23.4 20v1.4c0 2.6 3.6 2.6 3.6-1.4a7 7 0 1 0-3 5.8", stroke="mid", width=2.4)


def s_rust(d: Draw) -> None:
    d.path(gear_path(20, 20, 16, 13.2, 16), fill="main", stroke="main", width=1.2)
    d.circle(20, 20, 10, fill="tint")
    text(d, "R", 20.4, 20, 10.5, "main", 2.8)


def s_gopher(d: Draw) -> None:
    d.circle(9.5, 9.5, 3.4, fill="main")
    d.circle(30.5, 9.5, 3.4, fill="main")
    d.path("M7 22c0-9 5.5-14.5 13-14.5S33 13 33 22v13.5H7z", fill="main")
    d.circle(14, 16.5, 4.6, fill="tint")
    d.circle(26, 16.5, 4.6, fill="tint")
    d.circle(15.2, 17, 1.9, fill="main")
    d.circle(27.2, 17, 1.9, fill="main")
    d.ellipse(20, 24.5, 5, 3.6, fill="mid")
    d.ellipse(20, 22.6, 2.4, 1.6, fill="main")
    d.rect(18.3, 27.6, 3.4, 3.2, 0.6, fill="tint")


def s_zig(d: Draw) -> None:
    d.path("M7 8.5h21L12 31.5h21", stroke="main", width=4.6)
    d.path("M3.5 31.5h4.5M32 8.5h4.5", stroke="mid", width=4.6)


def s_dlang(d: Draw) -> None:
    text(d, "D", 16.5, 21, 22, "main", 4)
    d.circle(31.5, 9, 3.6, fill="mid")
    d.circle(33.5, 18, 2.2, fill="mid")


def s_crown(d: Draw) -> None:
    d.path("M5 29V11.5l7.5 7.5L20 7.5l7.5 11.5L35 11.5V29z", fill="main", stroke="main", width=1.6)
    d.rect(5, 29, 30, 5, 1.2, fill="mid")
    for x in (12.5, 20, 27.5):
        d.circle(x, 24.5, 1.8, fill="tint")


def s_crystal(d: Draw) -> None:
    d.path("M20 4l12 9v14L20 36 8 27V13z", fill="main", stroke="main", width=1.6)
    d.path("M8 13l12 6.5L32 13M20 19.5V36", stroke="tint", width=1.6)
    d.path("M20 4v15.5L8 13z", fill="mid")


def s_dip_chip(d: Draw) -> None:
    legs = "".join(f"M7.5 {y:g}h4.5M28 {y:g}h4.5" for y in (9, 15, 21, 27, 33))
    d.path(legs, stroke="main", width=2.2)
    d.rect(11.5, 4.5, 17, 31, 2.5, fill="main")
    d.circle(20, 4.5, 2.6, fill="tint")
    d.path("M15.5 14h9M15.5 19h6M15.5 24h9M15.5 29h5", stroke="mid", width=1.8)


def s_eye(d: Draw) -> None:
    d.path("M3.5 20c4-7 10-10.5 16.5-10.5S32.5 13 36.5 20c-4 7-10 10.5-16.5 10.5S7.5 27 3.5 20z", fill="tint", stroke="main")
    d.circle(20, 20, 6.4, fill="main")
    d.circle(20, 20, 2.2, fill="tint")
    d.path("M27 6l-4 4M13 6l4 4M20 4v5", stroke="mid", width=2)


def s_haskell(d: Draw) -> None:
    d.path("M4.5 33.5L13.5 20 4.5 6.5h6.8l9 13.5-9 13.5z", fill="main")
    d.path("M13.5 33.5l9-13.5-9-13.5h6.8l18 27h-6.8l-5.6-8.4-5.6 8.4z", fill="mid")
    d.path("M28.2 14.6h7.8M31 21.2h5", stroke="main", width=3)


def s_camel(d: Draw) -> None:
    tile(d)
    d.path(
        "M31.5 31v-6c0-3-1.4-5.8-3.6-5.8-1.6 0-2.5 1.4-3.3 2.9-1-2.5-2.4-4.4-4.3-4.4s-3.4 2-4.4 4.4l-2.2-.9-1.6-6.3"
        "c-.3-1.3-1.2-2-2.4-2H8l-.3 1.5 2.3.5 2 8.5c.4 1.9 1.4 3.3 3.2 4.2V31h2.3v-5.6h8.8V31h2.3v-5.5l1.4-1.4V31z",
        fill="tint",
    )


def s_fsharp(d: Draw) -> None:
    d.path("M19 5L4 20l15 15v-7.5L11.5 20 19 12.5z", fill="main")
    d.path("M22 11.5L30.5 20 22 28.5z", fill="mid")
    d.path("M24.5 5L36 20 24.5 35", stroke="main", width=2.2)


def s_elixir(d: Draw) -> None:
    d.path("M20 4c-5 6-10.5 13-10.5 20.5a10.5 10.5 0 0 0 21 0C30.5 17 25 10 20 4z", fill="main")
    d.path("M15 25c0-3.2 1.4-6.4 3-9", stroke="mid", width=2.4)


def s_erlang(d: Draw) -> None:
    tile(d)
    d.path("M11.5 20.5h17c0-5.2-3.6-8.8-8.4-8.8S11.5 15.5 11.5 20.6s3.8 8.8 8.9 8.8c2.7 0 4.8-.9 6.6-2.7",
           stroke="tint", width=3)


LAMBDA = "M11 8c4 0 6 1.4 8 5.8L29 34M18.4 17.2L10.5 34"


def s_clojure(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.path("M20 4.5a15.5 15.5 0 0 0 0 31z", fill="mid")
    d.path(LAMBDA, stroke="tint", width=3)


def s_edn(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    text(d, "#", 20, 20, 10, "mid", 2.2)


def s_elm(d: Draw) -> None:
    d.path("M20 3.5L36.5 20 20 36.5 3.5 20z", fill="main")
    d.path("M20 3.5L28.25 11.75 20 20 11.75 11.75z", fill="mid")
    d.path("M20 20l8.25 8.25L20 36.5z", fill="mid")
    d.path("M3.5 20h33M20 3.5v33M11.75 11.75L28.25 28.25", stroke="tint", width=1.6)


def s_purescript(d: Draw) -> None:
    for y in (11, 20, 29):
        d.path(f"M4.5 {y - 2.2:g}h11l3 2.2-3 2.2h-11z", fill="main")
        d.path(f"M35.5 {y - 2.2:g}h-11l-3 2.2 3 2.2h11z", fill="mid")


def s_gleam(d: Draw) -> None:
    d.path(star_path(20, 21, 15.5, 7.5, 5), fill="main", stroke="main", width=2)
    d.circle(16.6, 20.5, 1.6, fill="tint")
    d.circle(23.4, 20.5, 1.6, fill="tint")
    d.path("M17.6 25c1.4 1 3.4 1 4.8 0", stroke="tint", width=1.4)


def s_lambda(d: Draw) -> None:
    d.path(LAMBDA, stroke="main", width=3.8)


def s_racket(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.path("M4.5 20a15.5 15.5 0 0 0 15.5 15.5V20z", fill="mid")
    d.path(LAMBDA, stroke="tint", width=3)


def s_parens(d: Draw) -> None:
    d.path("M13 5.5c-5.5 4.5-5.5 24.5 0 29M27 5.5c5.5 4.5 5.5 24.5 0 29", stroke="main", width=3.2)
    d.path("M18.5 12c-2.6 2.6-2.6 13.4 0 16M21.5 12c2.6 2.6 2.6 13.4 0 16", stroke="mid", width=2.4)


def s_emacs(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.path("M27.5 10.5c-5-1.2-13.5-.4-13.5 2.4s11.4 2.2 11.4 5.4-13.4 1.6-13.4 5.4 9.6 4.6 16 3.4",
           stroke="tint", width=2.6)


def s_forall(d: Draw) -> None:
    d.path("M7 7l13 27L33 7M12 17.5h16", stroke="main", width=3.6)


def s_pi(d: Draw) -> None:
    d.path("M7 9h26M13.5 9v24M26.5 9v20.5c0 2.2 1 3.5 3.5 3.5", stroke="main", width=3.6)


def s_turnstile(d: Draw) -> None:
    d.path("M10 6v28M10 20h21", stroke="main", width=3.6)
    d.path("M26 13.5l6.5 6.5-6.5 6.5", stroke="mid", width=2.6)


def s_ruby(d: Draw) -> None:
    d.path("M11 6h18l7 9-16 20L4 15z", fill="main", stroke="main", width=1.6)
    d.path("M4 15h32M11 6l4 9 5-9 5 9 4-9M15 15l5 20 5-20", stroke="tint", width=1.4)


def s_rake_tool(d: Draw) -> None:
    d.path("M33 7L15.5 24.5", stroke="mid", width=3)
    d.path("M7 17.5l15.5 15.5", stroke="main", width=3)
    tines = []
    for i in range(5):
        x, y = 7 + i * 3.875, 17.5 + i * 3.875
        tines.append(f"M{x:.2f} {y:.2f}l-3 3")
    d.path("".join(tines), stroke="main", width=2.2)


def s_php(d: Draw) -> None:
    d.ellipse(20, 20, 16, 10.5, fill="main")
    text(d, "PHP", 20, 20, 8, "tint", 2.2)


def s_onion(d: Draw) -> None:
    d.path("M20 4.5c0 3-11 8-11 18a11 11 0 0 0 22 0c0-10-11-15-11-18z", fill="main")
    d.path("M20 9.5c-3.8 4-5.6 8.6-5.6 13.4s1.8 8.8 5.6 10.6M20 9.5c3.8 4 5.6 8.6 5.6 13.4s-1.8 8.8-5.6 10.6",
           stroke="tint", width=1.6)


def s_owl(d: Draw) -> None:
    d.path("M8.5 15L7 5.5l6.5 4.5M31.5 15L33 5.5l-6.5 4.5", fill="main", stroke="main", width=1.6)
    d.path("M8 15c0-5 5-8 12-8s12 3 12 8v9.5c0 7-5 11-12 11S8 31.5 8 24.5z", fill="main")
    d.circle(14.5, 16.5, 4.6, fill="tint")
    d.circle(25.5, 16.5, 4.6, fill="tint")
    d.circle(14.5, 16.5, 2, fill="main")
    d.circle(25.5, 16.5, 2, fill="main")
    d.path("M18.4 21l1.6 3 1.6-3z", fill="mid")
    d.path("M14.5 28.5c1.4 1 3.6 1 5 0 1.4 1 3.6 1 5 0", stroke="mid", width=1.6)


def s_lua(d: Draw) -> None:
    d.path("M30 4.5a12 12 0 0 1 5.5 10", stroke="mid", width=1.6)
    d.circle(18, 22, 13, fill="main")
    d.circle(24, 16, 3.8, fill="tint")
    d.circle(32.5, 7.5, 3.6, fill="main")


def s_rlang(d: Draw) -> None:
    d.ellipse(18.5, 17, 14, 10, stroke="mid", width=3.6)
    text(d, "R", 23, 23.5, 16, "main", 3.6)


def s_r_data(d: Draw) -> None:
    d.ellipse(16.5, 14.5, 12.5, 9, stroke="mid", width=3.2)
    text(d, "R", 19, 19, 14, "main", 3.2)


def s_julia(d: Draw) -> None:
    d.circle(20, 11, 6.5, fill="main")
    d.circle(11, 27, 6.5, fill="mid")
    d.circle(29, 27, 6.5, fill="main")


def s_awk(d: Draw) -> None:
    d.path("M5 31L11 9M12.5 31l6-22", stroke="main", width=2.8)
    d.path("M27 9c-2 0-3 1-3 3v4l-2 4 2 4v4c0 2 1 3 3 3M31 9c2 0 3 1 3 3v4l2 4-2 4v4c0 2-1 3-3 3", stroke="mid", width=2.2)


def s_scroll(d: Draw) -> None:
    d.path("M10 8.5A3.5 3.5 0 0 1 13.5 5H31a3.5 3.5 0 0 1 3.5 3.5V11H29v20a4.5 4.5 0 0 1-4.5 4.5H10a4.5 4.5 0 0 1-4.5-4.5"
           "v-2.5H10z", fill="tint", stroke="main")
    d.path("M14.5 13h10M14.5 18h10M14.5 23h7", stroke="mid", width=1.8)


def s_swift(d: Draw) -> None:
    tile(d, 7)
    d.path(
        "M27.5 9.5c3 4.6 3.6 10 1.2 14.2 1.8 2.4 2.2 4.6 1.8 5.6-1.4-1.8-3.8-2.2-5.6-1.4-5.8 2.8-12.4.6-17.4-4.6"
        " 4.2 2.8 9.4 3.2 12.8 1.4C14.6 21 10.4 16.8 8 13.4c3 2.6 7.6 6.2 10.8 8-2.8-2.8-5.6-6.4-7-9.2 4.2 4.2"
        " 9 8 12.4 9.4 2.6-3.6 2.8-8 3.3-12.1z",
        fill="tint",
    )


def s_dart(d: Draw) -> None:
    d.path("M9 14L21 5.2c1-.7 2.4-.7 3.4.1L35 14.5V28H23l-8.5 7.5L9 30z", fill="main", stroke="main", width=1.6)
    d.path("M9 14l14 14h12", stroke="tint", width=1.8)
    d.path("M9 14l6 21.5L23 28z", fill="mid")


def s_flame(d: Draw) -> None:
    d.path("M20 4c1 6 9.5 9 9.5 18.5a9.5 9.5 0 0 1-19 0c0-4.2 2-7.4 4.6-9.4 0 3 1 5.2 3 6.2-1-5.2 0-10.4 1.9-15.3z",
           fill="main")
    d.path("M20 35c-3 0-5-2.2-5-5 0-2.5 1.6-4.4 3.5-5.5 0 1.8.8 3 2 3.6-.3-2.2.5-4 2-5.4 1.5 2 2.5 4 2.5 7.3"
           " 0 2.8-2.2 5-5 5z", fill="mid")


def s_basic(d: Draw) -> None:
    d.rect(4.5, 5.5, 31, 23, 3, fill="main")
    d.rect(8, 9, 24, 16, 1.5, fill="tint")
    text(d, "10", 14.5, 14.5, 5, "main", 1.6)
    d.rect(11.5, 19.5, 5, 2.4, 0.4, fill="mid")
    d.path("M14 34h12M20 28.5V34", stroke="main", width=2.6)


def s_punch_card(d: Draw) -> None:
    d.path("M10.5 5H35.5V35H4.5V11z", fill="tint", stroke="main")
    holes = [(9, 15), (13, 23), (17, 11), (17, 27), (21, 19), (25, 9), (25, 31), (29, 15), (29, 23), (13, 31), (21, 9),
             (9, 27)]
    for x, y in holes:
        d.rect(x, y, 2.4, 3.6, 0.4, fill="main")


def s_pascal_triangle(d: Draw) -> None:
    for row in range(5):
        for k in range(row + 1):
            x = 20 + (k - row / 2) * 7
            role = "main" if k in (0, row) else "mid"
            d.circle(round(x, 2), 6.5 + row * 6.8, 2.6, fill=role)


def s_temple(d: Draw) -> None:
    d.path("M5 12.5L20 5l15 7.5z", fill="main", stroke="main", width=1.6)
    d.rect(6, 13, 28, 3, 0.6, fill="mid")
    d.path("M9.5 17v13M16.5 17v13M23.5 17v13M30.5 17v13", stroke="main", width=2.8)
    d.rect(5, 31, 30, 4, 1, fill="main")


def s_solidity(d: Draw) -> None:
    d.path("M20 4l9 14-9 5.5-9-5.5z", fill="main")
    d.path("M20 4v19.5l9-5.5z", fill="mid")
    d.path("M20 25.5l9-5.5-9 15.5-9-15.5z", fill="mid")
    d.path("M20 25.5v10l9-15.5z", fill="main")


def s_vyper(d: Draw) -> None:
    d.path("M4 7h32L20 35z", fill="main")
    d.path("M12 7h16l-8 14z", fill="mid")
    d.path("M4 7l8 0 8 14 8-14h8", stroke="tint", width=1.4)


def s_move_arrow(d: Draw) -> None:
    tile(d, 7)
    d.path("M11 20h17M21.5 13l7 7-7 7", stroke="tint", width=3.2)


def s_and_gate(d: Draw) -> None:
    d.path("M3.5 15h4.5M3.5 25h4.5M29 20h7.5", stroke="main")
    d.path("M8 9h10a11 11 0 0 1 0 22H8z", fill="tint", stroke="main")


OR_GATE = "M8 9h8c6 0 11 4 15 11-4 7-9 11-15 11H8c2.5-3 3.5-7 3.5-11S10.5 12 8 9z"


def s_or_gate(d: Draw) -> None:
    d.path("M3.5 15h7M3.5 25h7M31 20h5.5", stroke="main")
    d.path(OR_GATE, fill="tint", stroke="main")


def s_xor_gate(d: Draw) -> None:
    d.path("M3.5 15h7M3.5 25h7M31 20h5.5", stroke="main")
    d.path(OR_GATE, fill="tint", stroke="main")
    d.path("M4.5 9c2.5 3 3.5 7 3.5 11s-1 8-3.5 11", stroke="main")


def s_shader(d: Draw) -> None:
    d.path("M20 6L34 31H6z", fill="mid", stroke="main", width=2)
    d.circle(20, 6, 3.2, fill="main")
    d.circle(34, 31, 3.2, fill="main")
    d.circle(6, 31, 3.2, fill="main")


def s_vertex_mesh(d: Draw) -> None:
    pts = [(20, 5.5), (34.5, 31), (5.5, 31), (20, 22)]
    d.path("M20 5.5L34.5 31H5.5z", fill="tint", stroke="main", width=2)
    d.path("M20 5.5V22M34.5 31L20 22 5.5 31", stroke="mid", width=1.8)
    for x, y in pts:
        d.circle(x, y, 3, fill="main")


def s_fragment(d: Draw) -> None:
    d.path("M20 5L35 32H5z", fill="tint", stroke="main", width=2)
    step = 4.6
    for r in range(6):
        for c in range(7):
            x, y = 6.2 + c * step, 9 + r * step
            cx, cy = x + step / 2, y + step / 2
            if cy > 5 and abs(cx - 20) < (cy - 5) * 15 / 27 - 1.2 and cy < 30:
                d.rect(round(x + 0.3, 2), round(y + 0.3, 2), 3.8, 3.8, 0.5, fill="main" if (r + c) % 2 else "mid")


def s_ingot(d: Draw) -> None:
    d.path("M11 10h18l4 8H7z", fill="mid", stroke="main", width=1.8)
    d.path("M7 18h26l2.5 13h-31z", fill="main", stroke="main", width=1.8)
    d.path("M11 24h6", stroke="tint", width=2)


def s_arduino(d: Draw) -> None:
    d.path("M20 20c-3-5-5.5-7.2-9-7.2a7.2 7.2 0 0 0 0 14.4c3.5 0 6-2.2 9-7.2s5.5-7.2 9-7.2a7.2 7.2 0 0 1 0 14.4"
           "c-3.5 0-6-2.2-9-7.2z", stroke="main", width=3.4)
    d.path("M8.4 20h5.2M26.4 20h5.2M29 17.4v5.2", stroke="mid", width=2)


def s_godot(d: Draw) -> None:
    d.path("M7.5 16c0-2 1-3.4 2.2-4.4l-1-4.2 4.2-1.2 2 3.4c1.6-.6 3.4-1 5.1-1s3.5.4 5.1 1l2-3.4 4.2 1.2-1 4.2"
           "c1.2 1 2.2 2.4 2.2 4.4v14.5c0 3-2.2 5-5 5h-15c-2.8 0-5-2-5-5z", fill="main")
    d.circle(14.2, 21, 4.2, fill="tint")
    d.circle(25.8, 21, 4.2, fill="tint")
    d.circle(14.8, 21.2, 1.8, fill="main")
    d.circle(25.2, 21.2, 1.8, fill="main")
    d.path("M15 30h10", stroke="tint", width=2.2)


def s_schema(d: Draw) -> None:
    d.rect(5, 5, 30, 30, 3.5, fill="tint", stroke="main")
    d.path("M5 8.5A3.5 3.5 0 0 1 8.5 5h23A3.5 3.5 0 0 1 35 8.5V12H5z", fill="main", stroke="main")
    for y in (18, 24, 30):
        d.circle(10.5, y, 1.8, fill="main")
        d.path(f"M15 {y:g}h15", stroke="mid", width=2)


def s_graphql(d: Draw) -> None:
    pts = [(20 + 14 * math.cos(math.radians(-90 + 60 * k)), 20 + 14 * math.sin(math.radians(-90 + 60 * k)))
           for k in range(6)]
    hexagon = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "z"
    tri = "M" + "L".join(f"{pts[k][0]:.2f} {pts[k][1]:.2f}" for k in (0, 2, 4)) + "z"
    d.path(hexagon, stroke="main", width=1.8)
    d.path(tri, stroke="main", width=1.8)
    for x, y in pts:
        d.circle(round(x, 2), round(y, 2), 2.8, fill="main")


def s_prisma(d: Draw) -> None:
    d.path("M18.5 4L34 30.5 15 36 6 27.5z", fill="main", stroke="main", width=1.8)
    d.path("M18.5 4L15 36", stroke="tint", width=1.8)
    d.path("M18.5 4L6 27.5 15 36z", fill="mid")


def s_terraform(d: Draw) -> None:
    d.path("M5 4.5l8 4.6v9.2L5 13.7z", fill="main")
    d.path("M14.5 10l8 4.6v9.2l-8-4.6z", fill="main")
    d.path("M24 14.6l8-4.6v9.2l-8 4.6z", fill="mid")
    d.path("M14.5 20.8l8 4.6v9.2l-8-4.6z", fill="main")


def s_hcl(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.path("M15 17h10M15 23h10", stroke="mid", width=2.6)


def s_nix(d: Draw) -> None:
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        b = math.radians(-90 + 60 * k + 110)
        p = (20 + 15 * math.cos(a), 20 + 15 * math.sin(a))
        q = (20 + 6 * math.cos(b), 20 + 6 * math.sin(b))
        d.path(f"M{p[0]:.2f} {p[1]:.2f}L{q[0]:.2f} {q[1]:.2f}", stroke="main" if k % 2 == 0 else "mid", width=3.6)


def s_cmake(d: Draw) -> None:
    d.path("M20 4L4 34h14z", fill="main")
    d.path("M20 4l16 30-16-11.5z", fill="mid")
    d.path("M20 23.5L36 34H18z", fill="main")


def s_docker(d: Draw) -> None:
    for x, y in ((9, 15), (14, 15), (19, 15), (24, 15), (14, 10), (19, 10), (19, 5)):
        d.rect(x, y, 4.4, 4.4, 0.6, fill="mid")
    d.path("M4.5 20.5h29.5c1 0 1.6-1 3-1.2-1 2-2.6 3-4.2 3.2-2 7-8 12.5-17 12.5-7.2 0-11-4-11.3-14.5z", fill="main")
    d.circle(11, 25.5, 1.2, fill="tint")


def s_hammer(d: Draw) -> None:
    d.path("M24.5 15.5L8 32", stroke="mid", width=3.8)
    d.path(rotated([(-9.5, -3.6), (9.5, -3.6), (9.5, 3.6), (-9.5, 3.6)], 45, 26, 13), fill="main", stroke="main",
           width=1.6)


def s_bazel(d: Draw) -> None:
    def rhomb(cx: float, cy: float) -> str:
        return f"M{cx:g} {cy - 7:g}l6.5 7-6.5 7-6.5-7z"

    d.path(rhomb(20, 11), fill="mid")
    d.path(rhomb(13, 19) + rhomb(27, 19), fill="main")
    d.path(rhomb(20, 27.5), fill="main")


def s_shuriken(d: Draw) -> None:
    d.path(star_path(20, 20, 16, 5, 4), fill="main", stroke="main", width=1.4)
    d.circle(20, 20, 2.4, fill="tint")


def s_shield_check(d: Draw) -> None:
    d.path("M20 4l13 5v9c0 8-5.5 14-13 17.5C12.5 32 7 26 7 18V9z", fill="main")
    d.path("M14 19.5l4.5 4.5 8-8.5", stroke="tint", width=3)


def s_cue(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.path("M15 20.5l3.5 3.5 6.5-7", stroke="mid", width=2.6)


def s_dhall(d: Draw) -> None:
    d.path(HEXAGON, fill="tint", stroke="main")
    d.path("M14 11c2.6 0 4 1 5.4 4l6.6 14M18.8 17.4L13.6 29", stroke="main", width=2.8)


def s_jsonnet(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.path("M20 15v10M15 20h10", stroke="mid", width=2.6)


def s_wasm(d: Draw) -> None:
    d.path("M4.5 7.5a3 3 0 0 1 3-3h7a5.5 5.5 0 0 0 11 0h7a3 3 0 0 1 3 3v25a3 3 0 0 1-3 3h-25a3 3 0 0 1-3-3z", fill="main")
    text(d, "WA", 20, 25, 9, "tint", 2.6)


def s_vlang(d: Draw) -> None:
    tile(d, 7)
    d.path("M11 11l9 18 9-18", stroke="tint", width=4)


def s_membrane(d: Draw) -> None:
    d.path("M4 25l9-5.5 4.5 2.5 6-15 5.5 10 7 3.5-12 9.5z", fill="main", stroke="main", width=1.6)
    d.path("M23.5 7l-2 22.5L4 25l9-5.5 4.5 2.5z", fill="mid")


def s_rooster(d: Draw) -> None:
    d.path("M11 14.5c-1.6-3.6 1.4-6.2 3.8-4.2.2-3 4.2-4 5.2-1 1.2-2 5-.8 4 2.2-.8 1.6-3 3.2-6 3.4z", fill="mid")
    d.path("M8 33.5c0-4 1.5-7 4-9.5-1.6-1.6-2.5-3.6-2.5-6 0-4.4 3.6-7.5 8-7.5s8 3.1 8 7.5c0 2.6-1.2 5-3.2 6.4"
           "C24 26 25 29.5 25 33.5z", fill="main")
    d.path("M25.4 16.5l6 2-6 2z", fill="mid")
    d.ellipse(23.6, 23.5, 1.8, 3.2, fill="mid")
    d.circle(20.5, 16.5, 1.4, fill="tint")


BLOCK4A_TILES = {"M": "M", "ADA": "ADA", "H": "H", "VB": "VB", "F": "F", "SAS": "SAS"}
for _value in BLOCK4A_TILES.values():
    SYMBOLS[f"tile-{_value}"] = letter_tile(_value)

SYMBOLS.update(
    {
        "js-tile": s_js_tile,
        "ts-tile": s_ts_tile,
        "react-atom": s_react_atom,
        "vue-mark": s_vue,
        "svelte-mark": s_svelte,
        "astro-mark": s_astro,
        "paper-cup": s_paper_cup,
        "ejs-mark": s_ejs,
        "njk-mark": s_njk,
        "mustache": s_mustache,
        "pug-dog": s_pug_dog,
        "python-snakes": s_python,
        "jupyter-mark": s_jupyter,
        "java-cup": s_java_cup,
        "kotlin-mark": s_kotlin,
        "scala-mark": s_scala,
        "groovy-mark": s_groovy,
        "elephant": s_elephant,
        "hex-c": hex_mark("C", 14),
        "hex-cpp": hex_mark("C++", 9),
        "hex-cs": hex_mark("C#", 11),
        "objc-mark": s_objc,
        "rust-gear": s_rust,
        "gopher": s_gopher,
        "zig-mark": s_zig,
        "d-mark": s_dlang,
        "crown": s_crown,
        "crystal-mark": s_crystal,
        "dip-chip": s_dip_chip,
        "eye": s_eye,
        "haskell-mark": s_haskell,
        "camel": s_camel,
        "fsharp-mark": s_fsharp,
        "elixir-drop": s_elixir,
        "erlang-mark": s_erlang,
        "clojure-mark": s_clojure,
        "edn-mark": s_edn,
        "elm-tangram": s_elm,
        "purescript-mark": s_purescript,
        "gleam-star": s_gleam,
        "lambda": s_lambda,
        "racket-mark": s_racket,
        "parens": s_parens,
        "emacs-mark": s_emacs,
        "forall": s_forall,
        "pi-mark": s_pi,
        "turnstile": s_turnstile,
        "ruby-gem": s_ruby,
        "rake-tool": s_rake_tool,
        "php-mark": s_php,
        "onion": s_onion,
        "prolog-owl": s_owl,
        "lua-mark": s_lua,
        "r-mark": s_rlang,
        "r-data": s_r_data,
        "julia-dots": s_julia,
        "awk-mark": s_awk,
        "script-scroll": s_scroll,
        "swift-bird": s_swift,
        "dart-mark": s_dart,
        "flame": s_flame,
        "basic-crt": s_basic,
        "punch-card": s_punch_card,
        "pascal-triangle": s_pascal_triangle,
        "temple": s_temple,
        "solidity-mark": s_solidity,
        "vyper-mark": s_vyper,
        "move-arrow": s_move_arrow,
        "and-gate": s_and_gate,
        "or-gate": s_or_gate,
        "xor-gate": s_xor_gate,
        "shader-triangle": s_shader,
        "vertex-mesh": s_vertex_mesh,
        "fragment-pixels": s_fragment,
        "ingot": s_ingot,
        "arduino-mark": s_arduino,
        "godot-mark": s_godot,
        "schema": s_schema,
        "graphql-mark": s_graphql,
        "prisma-mark": s_prisma,
        "terraform-mark": s_terraform,
        "hcl-mark": s_hcl,
        "nix-snowflake": s_nix,
        "cmake-mark": s_cmake,
        "docker-whale": s_docker,
        "hammer": s_hammer,
        "bazel-mark": s_bazel,
        "shuriken": s_shuriken,
        "shield-check": s_shield_check,
        "cue-mark": s_cue,
        "dhall-mark": s_dhall,
        "jsonnet-mark": s_jsonnet,
        "wasm-mark": s_wasm,
        "vlang-mark": s_vlang,
        "membrane": s_membrane,
        "rooster": s_rooster,
    }
)

ICONS.update(
    {
        "v": ("vlang-mark", None),
        "v-vlang": ("vlang-mark", None),
        "v-verilog": ("or-gate", None),
        "v-coq": ("rooster", None),
        "m": ("tile-M", None),
        "m-objc": ("objc-mark", None),
        "m-matlab": ("membrane", None),
        "pl": ("onion", None),
        "pl-perl": ("onion", None),
        "pl-prolog": ("prolog-owl", None),
        "pm": ("onion", "text-M"),
        "js": ("js-tile", None),
        "mjs": ("js-tile", "text-M"),
        "cjs": ("js-tile", "text-C"),
        "jsx": ("react-atom", None),
        "ts": ("ts-tile", None),
        "mts": ("ts-tile", "text-M"),
        "cts": ("ts-tile", "text-C"),
        "tsx": ("react-atom", None),
        "vue": ("vue-mark", None),
        "svelte": ("svelte-mark", None),
        "astro": ("astro-mark", None),
        "coffee": ("paper-cup", None),
        "ejs": ("ejs-mark", None),
        "hbs": ("mustache", None),
        "pug": ("pug-dog", None),
        "njk": ("njk-mark", None),
        "py": ("python-snakes", None),
        "pyw": ("python-snakes", "text-W"),
        "pyi": ("python-snakes", "text-I"),
        "pyx": ("python-snakes", "text-C"),
        "pyc": ("python-snakes", "binary"),
        "pyd": ("python-snakes", "text-D"),
        "ipynb": ("jupyter-mark", None),
        "java": ("java-cup", None),
        "kt": ("kotlin-mark", None),
        "kts": ("kotlin-mark", "text-S"),
        "scala": ("scala-mark", None),
        "groovy": ("groovy-mark", None),
        "gradle": ("elephant", None),
        "c": ("hex-c", None),
        "h": ("hex-c", "text-H"),
        "cpp": ("hex-cpp", None),
        "cc": ("hex-cpp", None),
        "cxx": ("hex-cpp", None),
        "hpp": ("hex-cpp", "text-H"),
        "hxx": ("hex-cpp", "text-H"),
        "hh": ("hex-cpp", "text-H"),
        "cs": ("hex-cs", None),
        "csx": ("hex-cs", "text-S"),
        "cu": ("gpu-chip", "text-C"),
        "cuh": ("gpu-chip", "text-H"),
        "mm": ("objc-mark", "plus"),
        "rs": ("rust-gear", None),
        "go": ("gopher", None),
        "zig": ("zig-mark", None),
        "d": ("d-mark", None),
        "nim": ("crown", None),
        "cr": ("crystal-mark", None),
        "asm": ("dip-chip", None),
        "s": ("dip-chip", None),
        "odin": ("eye", None),
        "ada": ("tile-ADA", None),
        "adb": ("tile-ADA", None),
        "ads": ("tile-ADA", "text-H"),
        "hs": ("haskell-mark", None),
        "lhs": ("haskell-mark", "text-L"),
        "ml": ("camel", None),
        "mli": ("camel", "text-H"),
        "fs": ("fsharp-mark", None),
        "fsx": ("fsharp-mark", "text-S"),
        "fsi": ("fsharp-mark", "text-H"),
        "ex": ("elixir-drop", None),
        "exs": ("elixir-drop", "text-S"),
        "erl": ("erlang-mark", None),
        "hrl": ("erlang-mark", "text-H"),
        "clj": ("clojure-mark", None),
        "cljs": ("clojure-mark", "text-S"),
        "cljc": ("clojure-mark", "text-C"),
        "edn": ("edn-mark", None),
        "elm": ("elm-tangram", None),
        "purs": ("purescript-mark", None),
        "gleam": ("gleam-star", None),
        "scm": ("lambda", None),
        "rkt": ("racket-mark", None),
        "lisp": ("parens", None),
        "el": ("emacs-mark", None),
        "lean": ("forall", None),
        "agda": ("pi-mark", None),
        "idr": ("turnstile", None),
        "rb": ("ruby-gem", None),
        "rake": ("rake-tool", None),
        "gemspec": ("ruby-gem", "template"),
        "php": ("php-mark", None),
        "lua": ("lua-mark", None),
        "r": ("r-mark", None),
        "rmd": ("r-mark", "text-M"),
        "jl": ("julia-dots", None),
        "tcl": ("quill", None),
        "awk": ("awk-mark", None),
        "ahk": ("tile-H", None),
        "applescript": ("script-scroll", None),
        "scpt": ("script-scroll", "binary"),
        "swift": ("swift-bird", None),
        "dart": ("dart-mark", None),
        "mojo": ("flame", None),
        "vb": ("tile-VB", None),
        "vbs": ("tile-VB", "text-S"),
        "bas": ("basic-crt", None),
        "cob": ("punch-card", None),
        "cbl": ("punch-card", None),
        "pas": ("pascal-triangle", None),
        "dpr": ("temple", None),
        "f": ("tile-F", None),
        "for": ("tile-F", None),
        "f90": ("tile-F", None),
        "f95": ("tile-F", None),
        "sas": ("tile-SAS", None),
        "sol": ("solidity-mark", None),
        "vy": ("vyper-mark", None),
        "move": ("move-arrow", None),
        "vhdl": ("and-gate", None),
        "vhd-vhdl": ("and-gate", None),
        "sv": ("xor-gate", None),
        "svh": ("xor-gate", "text-H"),
        "glsl": ("shader-triangle", None),
        "vert": ("vertex-mesh", None),
        "frag": ("fragment-pixels", None),
        "hlsl": ("shader-triangle", "text-D"),
        "wgsl": ("shader-triangle", "web"),
        "metal": ("ingot", None),
        "gdshader": ("shader-triangle", "text-G"),
        "ino": ("arduino-mark", None),
        "gd": ("godot-mark", None),
        "proto": ("schema", None),
        "pb-protobuf": ("schema", "binary"),
        "graphql": ("graphql-mark", None),
        "gql": ("graphql-mark", None),
        "prisma": ("prisma-mark", None),
        "tf": ("terraform-mark", None),
        "tfvars": ("terraform-mark", "text-V"),
        "hcl": ("hcl-mark", None),
        "nix": ("nix-snowflake", None),
        "cmake": ("cmake-mark", None),
        "dockerfile": ("docker-whale", None),
        "mk": ("hammer", None),
        "bzl": ("bazel-mark", None),
        "ninja": ("shuriken", None),
        "rego": ("shield-check", None),
        "cue": ("cue-mark", None),
        "dhall": ("dhall-mark", None),
        "jsonnet": ("jsonnet-mark", None),
        "wasm": ("wasm-mark", None),
        "wat": ("wasm-mark", "text-T"),
    }
)


# ------------------------------------------------------------------ block 4b: data, databases, web, shell


def mini_braces(y: float) -> str:
    left = f"M10 {y - 4:g}Q7.5 {y - 4:g} 7.5 {y - 2:g}Q7.5 {y:g} 6 {y:g}Q7.5 {y:g} 7.5 {y + 2:g}Q7.5 {y + 4:g} 10 {y + 4:g}"
    return left + map_path(left, lambda x: 40 - x, lambda v: v)


def s_json(d: Draw) -> None:
    d.path(BRACES, stroke="main", width=2.4)
    d.circle(20, 16, 2, fill="mid")
    d.circle(20, 24, 2, fill="mid")


def s_json_lines(d: Draw) -> None:
    for i, y in enumerate((8.5, 20, 31.5)):
        d.path(mini_braces(y), stroke="main", width=2)
        d.path(f"M13.5 {y:g}h13", stroke="mid" if i % 2 else "main", width=2.4)


def s_har(d: Draw) -> None:
    d.path("M5 4.5v31", stroke="mid", width=1.8)
    for i, (x, w, role) in enumerate(((8, 10, "main"), (12, 14, "mid"), (15, 8, "main"), (19, 16, "mid"), (24, 11, "main"))):
        d.rect(x, 5.5 + i * 6, w, 4, 1.5, fill=role)


def s_folded_map(d: Draw) -> None:
    d.path("M4.5 9l9.5-4 12 4 9.5-4v26l-9.5 4-12-4-9.5 4z", fill="tint", stroke="main")
    d.path("M14 5v26M26 9v26", stroke="main", width=1.8)
    d.path("M8 27c4-2 5-8 9-8s5 6 9 4 4.5-7 6-9", stroke="mid", width=2)


def s_yaml(d: Draw) -> None:
    for x, y, w in ((6, 8.5, 22), (11, 16.5, 17), (11, 24.5, 13), (6, 32.5, 18)):
        d.path(f"M{x:g} {y:g}h3.6", stroke="main", width=2.8)
        d.path(f"M{x + 7:g} {y:g}h{w:g}", stroke="mid", width=2.6)


def s_toml(d: Draw) -> None:
    d.path("M11 6H6v28h5M29 6h5v28h-5", stroke="main", width=3)
    text(d, "T", 20, 20, 15, "mid", 3.2)


def table_frame(d: Draw) -> None:
    d.rect(4.5, 6.5, 31, 27, 3, fill="tint", stroke="main")
    d.path("M4.5 15.5h31M4.5 24.5h31", stroke="main", width=1.6)


def s_csv(d: Draw) -> None:
    table_frame(d)
    for y in (11, 20, 29):
        for x in (14.5, 25.5):
            d.circle(x, y - 0.6, 1.3, fill="main")
            d.path(f"M{x + 1:g} {y:g}l-1.3 2.4", stroke="main", width=1.3)
        for x0 in (7.5, 18.5, 29.5):
            d.path(f"M{x0:g} {y:g}h3.4", stroke="mid", width=1.8)


def s_tsv(d: Draw) -> None:
    table_frame(d)
    for y in (11, 20, 29):
        for x in (12, 23):
            d.path(f"M{x:g} {y:g}h4.6M{x + 2.6:g} {y - 2:g}l2 2-2 2M{x + 5.6:g} {y - 2.2:g}v4.4", stroke="main",
                   width=1.3)
        d.path(f"M7 {y:g}h3M30 {y:g}h3", stroke="mid", width=1.8)


def s_paper_plane(d: Draw) -> None:
    d.path("M4 31l4.5-2M8.5 35l3.5-1.6", stroke="mid", width=2)
    d.path("M4.5 18.5L35.5 5 28 34.5l-8.5-8-5 5.5v-8z", fill="main", stroke="main", width=1.6)
    d.path("M35.5 5L14.5 23.5", stroke="tint", width=1.8)


def s_packed_braces(d: Draw) -> None:
    d.rect(4.5, 4.5, 31, 31, 4, fill="main")
    d.path("M17 11c-2.5 0-3 1-3 3v2.5c0 1.5-.8 2.5-2 3 1.2.5 2 1.5 2 3V25c0 2 .5 3 3 3"
           "M23 11c2.5 0 3 1 3 3v2.5c0 1.5.8 2.5 2 3-1.2.5-2 1.5-2 3V25c0 2-.5 3-3 3", stroke="tint", width=2.2)
    d.circle(20, 19.5, 1.9, fill="tint")


def s_byte_cells(d: Draw) -> None:
    for r, y in enumerate((9, 21.5)):
        for c, x in enumerate((4.5, 12.5, 20.5, 28.5)):
            d.rect(x, y, 7, 9.5, 1.5, fill="main" if (r + c) % 2 == 0 else "mid")


def s_rpc_boxes(d: Draw) -> None:
    d.path("M16.5 11h8.5a4 4 0 0 1 4 4v3.5M26 15.5l3 3 3-3", stroke="main", width=2)
    d.path("M23.5 29H15a4 4 0 0 1-4-4v-3.5M14 24.5l-3-3-3 3", stroke="mid", width=2)
    d.rect(4.5, 5, 12, 12, 2.5, fill="tint", stroke="main")
    d.rect(23.5, 23, 12, 12, 2.5, fill="main")


def s_captain_hat(d: Draw) -> None:
    d.path("M7.5 20c0-6.6 5.6-11.5 12.5-11.5S32.5 13.4 32.5 20z", fill="tint", stroke="main")
    d.rect(6.5, 19, 27, 5.5, 1.6, fill="main")
    d.path("M9 24.5h22c-1.2 4.4-5.4 7.5-11 7.5S10.2 28.9 9 24.5z", fill="mid", stroke="main", width=1.6)
    d.circle(20, 14.5, 2.6, fill="main")


def s_flat_buffer(d: Draw) -> None:
    d.path("M10 15.5c1.5-6 11-6 12.5 0M21 13l1.5 2.5 2.5-1.6M22 15.5c1.5-5 9-5 10.5 0M31.4 13.2l1.1 2.3 2.4-1.4",
           stroke="mid", width=1.8)
    d.rect(4, 17.5, 32, 10, 2, fill="tint", stroke="main")
    d.path("M10 17.5v10M22 17.5v10M28 17.5v10", stroke="main", width=1.8)
    d.rect(4, 17.5, 6, 10, 2, fill="main")


def s_ini(d: Draw) -> None:
    d.path("M8 5H5.5v9H8M32 5h2.5v9H32", stroke="main", width=2.2)
    d.path("M11.5 9.5h17", stroke="main", width=2.6)
    for y in (21.5, 30.5):
        d.path(f"M5.5 {y:g}h9M24.5 {y:g}h10", stroke="main", width=2.4)
        d.path(f"M17.5 {y - 1.6:g}h4M17.5 {y + 1.6:g}h4", stroke="mid", width=1.6)


def s_sliders(d: Draw) -> None:
    d.path("M5 10h30M5 20h30M5 30h30", stroke="mid", width=2.4)
    for x, y in ((13, 10), (27, 20), (18, 30)):
        d.circle(x, y, 3.8, fill="main", stroke="tint", width=1.6)


def s_properties(d: Draw) -> None:
    text(d, "#", 8, 8, 7, "mid", 1.6)
    d.path("M14 8h16", stroke="mid", width=2.2)
    for y in (17, 25, 33):
        d.path(f"M5.5 {y:g}h9M24.5 {y:g}h10", stroke="main", width=2.4)
        d.path(f"M17.5 {y - 1.6:g}h4M17.5 {y + 1.6:g}h4", stroke="mid", width=1.6)


def s_env(d: Draw) -> None:
    d.rect(4.5, 7.5, 31, 25, 3.5, fill="tint", stroke="main")
    text(d, "$", 13, 20, 14, "main", 2.8)
    d.path("M21.5 14.5h9M21.5 20h9M21.5 25.5h6", stroke="mid", width=2)


def disclosure(x: float, y: float, open_: bool) -> str:
    return f"M{x - 2.4:g} {y - 1.4:g}h4.8l-2.4 3z" if open_ else f"M{x - 1.4:g} {y - 2.4:g}v4.8l3-2.4z"


def s_plist(d: Draw) -> None:
    d.path(disclosure(7, 8.5, True) + disclosure(13, 16.5, True) + disclosure(13, 32.5, False), fill="main")
    d.circle(19, 24.5, 1.6, fill="main")
    for x, y, w, role in ((11, 8.5, 22, "main"), (17, 16.5, 17, "main"), (23, 24.5, 12, "mid"), (17, 32.5, 15, "main")):
        d.path(f"M{x:g} {y:g}h{w:g}", stroke=role, width=2.4)


def s_padlock(d: Draw) -> None:
    d.path("M13 17.5v-4a7 7 0 0 1 14 0v4", stroke="main", width=3)
    d.rect(8, 17, 24, 18.5, 3.5, fill="main")
    d.circle(20, 24.5, 2.4, fill="tint")
    d.path("M20 25v4.5", stroke="tint", width=2)


def s_log(d: Draw) -> None:
    d.path("M9 5v30", stroke="mid", width=2)
    for y, w in ((9, 22), (20, 18), (31, 20)):
        d.circle(9, y, 2.8, fill="main")
        d.path(f"M15 {y:g}h{w:g}", stroke="main", width=2.4)


def s_git(d: Draw) -> None:
    d.path("M20 4L36 20 20 36 4 20z", fill="main", stroke="main", width=3)
    d.path("M14 11.5l5 5v10M19 16.5l6.5 6.5", stroke="tint", width=2.2)
    d.circle(19, 16.5, 2.2, fill="tint")
    d.circle(19, 27, 2.4, fill="tint")
    d.circle(25.5, 23, 2.4, fill="tint")


def cube_faces(d: Draw, cx: float, cy: float, s: float) -> None:
    top = f"M{cx:g} {cy - s:g}L{cx + s:g} {cy - s / 2:g}L{cx:g} {cy:g}L{cx - s:g} {cy - s / 2:g}z"
    left = f"M{cx - s:g} {cy - s / 2:g}L{cx:g} {cy:g}L{cx:g} {cy + s:g}L{cx - s:g} {cy + s / 2:g}z"
    right = f"M{cx:g} {cy:g}L{cx + s:g} {cy - s / 2:g}L{cx + s:g} {cy + s / 2:g}L{cx:g} {cy + s:g}z"
    d.path(top, fill="mid", stroke="main", width=1.2)
    d.path(left, fill="tint", stroke="main", width=1.2)
    d.path(right, fill="main", stroke="main", width=1.2)


def s_cubes(d: Draw) -> None:
    cube_faces(d, 20, 12.5, 7.5)
    cube_faces(d, 12, 26.5, 7.5)
    cube_faces(d, 28, 26.5, 7.5)


def s_info(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.circle(20, 12.5, 2.3, fill="tint")
    d.path("M20 18.5v10", stroke="tint", width=3.4)


def s_npm(d: Draw) -> None:
    d.rect(4, 11, 32, 18, 2, fill="main")
    d.path("M8 25.5V15h6.5v10.5M18 29V15h6v7h-6M27.5 25.5V15h5v10.5M30 15v10.5", stroke="tint", width=2.2)


def s_diff(d: Draw) -> None:
    rows = ((8.5, "+", "main"), (16.5, "-", "mid"), (24.5, "+", "main"), (32.5, "-", "mid"))
    for y, sign, role in rows:
        d.path(f"M5 {y:g}h6" + (f"M8 {y - 3:g}v6" if sign == "+" else ""), stroke=role, width=2.4)
        d.path(f"M15 {y:g}h{20 if y < 30 else 14:g}", stroke=role, width=2.4)


def s_bandage(d: Draw) -> None:
    d.path(rotated([(-6, -15), (6, -15), (6, 15), (-6, 15)], 45, 20, 20), fill="main", stroke="main", width=4)
    d.path(rotated([(-6, -5.5), (6, -5.5), (6, 5.5), (-6, 5.5)], 45, 20, 20), fill="mid")
    for dx, dy in ((-1.6, -1.6), (1.6, 1.6), (-1.6, 1.6), (1.6, -1.6)):
        d.circle(20 + dx, 20 + dy, 0.9, fill="tint")


def s_sqlite(d: Draw) -> None:
    tile(d, 6)
    d.path("M29.5 8.5C22 9 15.5 14.5 14 23l-.4 3 2.6-.5C24 24 28.8 17.4 29.5 8.5z", fill="tint")
    d.path("M27.5 10.5L10 31", stroke="tint", width=2)


def s_access(d: Draw) -> None:
    back_sheet(d)
    d.path("M22 12.5h13M22 20h13M22 27.5h13", stroke="mid", width=1.8)
    d.circle(28.5, 8.6, 1.4, fill="main")
    office_tile(d, "A")


def s_server_rack(d: Draw) -> None:
    d.rect(7, 4.5, 26, 31, 3, fill="tint", stroke="main")
    for y, role in ((8, "main"), (16.5, "main"), (25, "mid")):
        d.rect(10, y, 20, 6.5, 1.2, fill=role)
        d.circle(13.2, y + 3.25, 1.2, fill="tint")
        d.path(f"M19 {y + 3.25:g}h8", stroke="tint", width=1.4)


def s_dbase(d: Draw) -> None:
    table_frame(d)
    d.path("M4.5 9.5a3 3 0 0 1 3-3h25a3 3 0 0 1 3 3v6h-31z", fill="main", stroke="main")
    d.path("M14 15.5v18M24 15.5v18", stroke="main", width=1.6)
    d.path("M6.2 18.4l2.8 1.6-2.8 1.6z", fill="main")


def s_oracle(d: Draw) -> None:
    d.rect(4.5, 11, 31, 18, 9, stroke="main", width=4.4)


def s_dolphin(d: Draw) -> None:
    d.path("M5 29c2.5-9.5 11-16.5 21-16.5 2.2 0 4.2.4 6 1.2l3.5-2.7-1 4.3c1 1.4 1.5 3 1.5 4.7-2-1-4.2-1.4-6.2-1"
           "-2 5.8-8 9.8-15 9.8l-2.4 5-2-5.4C7.6 28.8 6.2 29.2 5 29z", fill="main")
    d.path("M17 12.5l-1.5-5 5.5 4.6", fill="main", stroke="main", width=1.4)
    d.circle(28.5, 15.6, 1.2, fill="tint")


def s_stones(d: Draw) -> None:
    d.ellipse(20, 30, 14.5, 5.5, fill="main")
    d.ellipse(19, 21.5, 10.5, 4.4, fill="mid")
    d.ellipse(21, 13.6, 7, 3.6, fill="main")
    d.ellipse(20, 7.4, 4, 2.4, fill="mid")


def s_duck(d: Draw) -> None:
    d.path("M5.5 26.5c0-4 3-7 8-7h8c6 0 11 3 12.5 8 .5 2-1 4-3 4H10.5c-3 0-5-2-5-5z", fill="main")
    d.circle(19, 14.5, 7.5, fill="main")
    d.path("M25.5 13.5l8.5 2.5-8.5 2.5z", fill="mid")
    d.circle(21, 12.6, 1.5, fill="tint")
    d.path("M13 26c3 2.2 8.5 2.2 11.5-.8", stroke="tint", width=1.6)


def s_firebird(d: Draw) -> None:
    d.path("M16.5 28.5c-2.4 2.4-2.6 5.2-.6 7 .2-2.2 1.6-3.4 4.1-5 2.5 1.6 3.9 2.8 4.1 5 2-1.8 1.8-4.6-.6-7z",
           fill="mid")
    d.path("M3.5 11c5.5-.6 10.6 1.8 14.5 6.6L20 15.5l2 2.1C25.9 12.8 31 10.4 36.5 11c-3.2 5-8.6 9.4-14.2 10.6L20 30"
           "l-2.3-8.4C12.1 20.4 6.7 16 3.5 11z", fill="main")
    d.circle(20, 12.5, 2.8, fill="main")
    d.path("M7.5 13.4c3 .4 6 2 8.4 4.6M32.5 13.4c-3 .4-6 2-8.4 4.6", stroke="tint", width=1.4)


def arc_path(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.2f} {y0:.2f}A{r:g} {r:g} 0 {large} 1 {x1:.2f} {y1:.2f}"


def s_realm(d: Draw) -> None:
    d.path(arc_path(20, 20, 12.5, -80, 30), stroke="main", width=5)
    d.path(arc_path(20, 20, 12.5, 40, 150), stroke="mid", width=5)
    d.path(arc_path(20, 20, 12.5, 160, 270), stroke="main", width=5)


def s_redis(d: Draw) -> None:
    for y in (21, 14, 7):
        d.path(f"M6 {y + 5:g}v3.5l14 5.5 14-5.5V{y + 5:g}l-14 5.5z", fill="main")
        d.path(f"M20 {y:g}l14 5-14 5.5L6 {y + 5:g}z", fill="mid", stroke="main", width=1.2)
    d.path(star_path(20, 12, 2.6, 1.1, 4), fill="tint")


def s_mongo_leaf(d: Draw) -> None:
    d.path("M20 4c5 5 8.5 11 8.5 17.5 0 6-3.6 10-8.5 12.2-4.9-2.2-8.5-6.2-8.5-12.2C11.5 15 15 9 20 4z", fill="main")
    d.path("M20 9v27", stroke="tint", width=1.8)


def s_parquet(d: Draw) -> None:
    cells = ((5.5, 5.5, True), (20.5, 5.5, False), (5.5, 20.5, False), (20.5, 20.5, True))
    for x, y, horizontal in cells:
        for i in range(3):
            role = "main" if (i + (0 if horizontal else 1)) % 2 == 0 else "mid"
            if horizontal:
                d.rect(x, y + i * 4.8 + 0.2, 14, 4.2, 0.8, fill=role)
            else:
                d.rect(x + i * 4.8 + 0.2, y, 4.2, 14, 0.8, fill=role)


def s_columnar(d: Draw) -> None:
    for c, x in enumerate((5, 15.5, 26)):
        for i in range(4):
            role = "main" if (i + c) % 2 == 0 else "mid"
            d.rect(x, 5 + i * 7.6, 9, 6.6, 1.2, fill=role)


def s_arrow_chevrons(d: Draw) -> None:
    d.path("M4.5 10l7.5 10-7.5 10M24.5 10l7.5 10-7.5 10", stroke="main", width=3.6)
    d.path("M14.5 10l7.5 10-7.5 10", stroke="mid", width=3.6)


def s_hierarchy(d: Draw) -> None:
    d.path("M20 13v6M8.5 19h23M8.5 19v7M31.5 19v7M20 19v7", stroke="main", width=1.8)
    d.rect(14, 5, 12, 8, 2, fill="main")
    for x in (3.5, 14, 24.5):
        d.rect(x, 26, 12, 8, 2, fill="mid")


def s_data_cube(d: Draw) -> None:
    d.path("M20 4.5L33.5 12 20 19.5 6.5 12z", fill="mid", stroke="main", width=1.6)
    d.path("M6.5 12L20 19.5v16L6.5 28z", fill="tint", stroke="main", width=1.6)
    d.path("M33.5 12v16L20 35.5v-16z", fill="main", stroke="main", width=1.6)
    d.path("M11 14.5v16M15.5 17v16M13.25 8.25l13.5 7.5M26.75 8.25l-13.5 7.5", stroke="main", width=1)
    d.path("M24.5 17v16M29 14.5v16", stroke="tint", width=1)


def s_chunk_grid(d: Draw) -> None:
    roles = ["main", "mid", "tint", "mid", "main", "mid", "tint", "mid", "main"]
    for i, role in enumerate(roles):
        x, y = 5 + (i % 3) * 10.3, 5 + (i // 3) * 10.3
        d.rect(x, y, 9.2, 9.2, 1.6, fill=role, stroke="main" if role == "tint" else None, width=1.6)


def s_histogram_bell(d: Draw) -> None:
    for x, h in ((6, 5), (11, 11), (16, 19), (21, 21), (26, 12), (31, 5)):
        d.rect(x - 2, 34 - h, 4.4, h, 0.8, fill="mid")
    d.path("M4 33c5 0 7-22 15-22s10 22 17 22", stroke="main", width=2.4)


def s_scatter(d: Draw) -> None:
    d.path("M6 5v29h29", stroke="main", width=2)
    for x, y in ((11, 28), (14, 24), (17, 26), (19, 20), (23, 19), (25, 14), (29, 15), (31, 10)):
        d.circle(x, y, 1.9, fill="mid")
    d.path("M9 31L33 8", stroke="main", width=2.4)


def s_numpy(d: Draw) -> None:
    d.path("M20 4.5L33.5 12 20 19.5 6.5 12z", fill="mid")
    d.path("M6.5 12L20 19.5v16L6.5 28z", fill="main")
    d.path("M33.5 12v16L20 35.5v-16z", fill="main")
    d.path("M6.5 20L20 27.5 33.5 20M20 19.5v16", stroke="tint", width=1.6)


def s_pickle_jar(d: Draw) -> None:
    d.rect(9, 9.5, 22, 26, 5, fill="tint", stroke="main")
    d.rect(10.5, 4.5, 19, 5, 1.6, fill="main")
    pts = [(4 * math.cos(t), 10.5 * math.sin(t)) for t in (math.pi * k / 10 for k in range(20))]
    d.path(rotated(pts, 22, 20, 23), fill="main")
    for x, y in ((18.4, 18.5), (21.4, 23), (19.4, 28)):
        d.circle(x, y, 0.9, fill="tint")


def graph(d: Draw, nodes: list[tuple[float, float]], edges: list[tuple[int, int]], hub: int | None = None) -> None:
    d.path("".join(f"M{nodes[a][0]:g} {nodes[a][1]:g}L{nodes[b][0]:g} {nodes[b][1]:g}" for a, b in edges),
           stroke="mid", width=2)
    for i, (x, y) in enumerate(nodes):
        d.circle(x, y, 4.4 if i == hub else 3.4, fill="main")


def s_graph_tri(d: Draw) -> None:
    graph(d, [(9, 9), (31, 12), (20, 31), (7, 27)], [(0, 1), (1, 2), (2, 0), (0, 3), (3, 2)])


def s_graph_star(d: Draw) -> None:
    nodes = [(20, 20)] + [(20 + 14 * math.cos(math.radians(-90 + 72 * k)), 20 + 14 * math.sin(math.radians(-90 + 72 * k)))
                          for k in range(5)]
    nodes = [(round(x, 2), round(y, 2)) for x, y in nodes]
    graph(d, nodes, [(0, k) for k in range(1, 6)], hub=0)


def s_graph_tree(d: Draw) -> None:
    graph(d, [(20, 7), (11, 19), (29, 19), (6, 32), (16, 32), (29, 32)], [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)])


def s_turtle(d: Draw) -> None:
    d.path("M7 25.5l-3.2 2.2M11 25v5M27.5 25v5", stroke="mid", width=3.2)
    d.circle(33.5, 22, 3.4, fill="mid")
    d.path("M6.5 25.5a13.5 12 0 0 1 27 0z", fill="main")
    d.path("M13.5 25.5l2.2-7h8.6l2.2 7M15.7 18.5l4.3-4.8 4.3 4.8", stroke="tint", width=1.4)


def s_rdf(d: Draw) -> None:
    d.path("M14 20h10", stroke="main", width=2.2)
    d.path("M21.5 16.5L25 20l-3.5 3.5", stroke="main", width=2.2)
    d.rect(14.5, 9, 9, 4.5, 1.4, fill="mid")
    d.circle(9, 20, 5.5, fill="main")
    d.circle(31, 20, 5.5, fill="mid", stroke="main", width=1.8)


def s_triples(d: Draw) -> None:
    for y in (10, 20, 30):
        for x, role in ((7, "main"), (16, "mid"), (25, "main")):
            d.circle(x, y, 3.2, fill=role)
        d.circle(33, y + 1.6, 1.5, fill="main")


def s_quads(d: Draw) -> None:
    for y in (10, 20, 30):
        for x, role in ((6.5, "main"), (14.5, "mid"), (22.5, "main"), (30.5, "mid")):
            d.circle(x, y, 2.9, fill=role)


def s_trig(d: Draw) -> None:
    d.rect(4.5, 7, 31, 27, 4, fill="tint", stroke="main")
    d.rect(8, 4, 11, 6, 1.6, fill="main")
    d.path("M17.5 21.5h5M20.5 19l2.5 2.5-2.5 2.5", stroke="main", width=1.8)
    d.circle(12.5, 21.5, 4.2, fill="main")
    d.circle(27.5, 21.5, 4.2, fill="mid")


def s_safe(d: Draw) -> None:
    d.rect(5, 5.5, 30, 27, 3, fill="main")
    d.rect(9, 9.5, 22, 19, 2, fill="tint")
    d.circle(20, 19, 5.4, fill="main")
    d.circle(20, 19, 1.8, fill="tint")
    d.path("M20 13.6v2M20 22.4v2M14.6 19h2M23.4 19h2", stroke="tint", width=1.2)
    d.path("M9 32.5v3M31 32.5v3", stroke="main", width=3)


def s_memo(d: Draw) -> None:
    d.path("M6 6h28v20l-8 8H6z", fill="tint", stroke="main")
    d.path("M34 26h-8v8", fill="mid", stroke="main")
    d.path("M11 13h18M11 19h18M11 25h10", stroke="mid", width=2)


def s_fox(d: Draw) -> None:
    d.path("M5.5 6l7.5 6.5h14L34.5 6l-2 13.5c-1 7-6 13-12.5 15.5C13.5 32.5 8.5 26.5 7.5 19.5z", fill="main",
           stroke="main", width=1.4)
    d.path("M10.5 22.5c2 5 5.2 8.6 9.5 10.4 4.3-1.8 7.5-5.4 9.5-10.4-3 1-6.3 1.6-9.5 1.6s-6.5-.6-9.5-1.6z", fill="tint")
    d.path("M8.5 9.5l3 3H9zM31.5 9.5l-3 3H31z", fill="mid")
    d.circle(14.8, 19.5, 1.7, fill="tint")
    d.circle(25.2, 19.5, 1.7, fill="tint")
    d.circle(20, 31, 1.7, fill="main")


def s_thumbs(d: Draw) -> None:
    for x, y in ((4.5, 4.5), (21, 4.5), (4.5, 21), (21, 21)):
        scene(d, x, y, 14.5, 14.5, 2)


def s_btree(d: Draw) -> None:
    d.path("M16 12L9 25M20 12v13M24 12l7 13", stroke="main", width=1.8)
    d.rect(12, 5, 16, 7, 1.6, fill="main")
    d.path("M17.3 5v7M22.7 5v7", stroke="tint", width=1.2)
    for x in (3.5, 14.5, 25.5):
        d.rect(x, 25, 11, 7, 1.6, fill="mid")


def s_ram(d: Draw) -> None:
    d.path("".join(f"M{x:g} 25v4.5" for x in (7, 10, 13, 16, 22, 25, 28, 31, 34)), stroke="main", width=1.4)
    d.rect(4, 11.5, 32, 14, 2, fill="main")
    for x in (7, 14, 21, 28):
        d.rect(x, 14.5, 5, 8, 0.8, fill="tint")


HTML_SHIELD = "M6 4.5h28l-2.5 28L20 36l-11.5-3.5z"


def shield_mark(digit: str):
    def draw(d: Draw) -> None:
        d.path(HTML_SHIELD, fill="main", stroke="main", width=1.4)
        d.path("M20 7v26.5l9.3-2.8 2.2-23.7z", fill="mid")
        text(d, digit, 20, 19.5, 15, "tint", 3.2)

    return draw


def s_sass(d: Draw) -> None:
    d.circle(20, 20, 15.5, fill="main")
    d.path("M26 12.5c-3-2-9-1.4-10 1.6s3.6 4.4 6.2 5.8 3 4-.8 6-7.2.2-8.4-1.6", stroke="tint", width=2.6)


def s_stylus(d: Draw) -> None:
    d.path("M5 33c3-3 5-1 7-3s0-4 2-6 4 0 6-2", stroke="mid", width=2)
    d.path(rotated([(-2.6, -15), (2.6, -15), (2.6, 7), (-2.6, 7)], 45, 25, 15), fill="main")
    d.path(rotated([(-2.6, 7), (2.6, 7), (0, 12.5)], 45, 25, 15), fill="mid")


def s_postcss(d: Draw) -> None:
    d.circle(20, 21, 14.5, stroke="main", width=2.4)
    d.path("M20 6.5L32.6 28.3H7.4z", stroke="main", width=2.2)
    d.circle(20, 21.5, 6, stroke="mid", width=2.2)


def s_xml(d: Draw) -> None:
    d.path("M13 11l-8 9 8 9M27 11l8 9-8 9", stroke="main", width=3.2)
    d.path("M23 8l-6 24", stroke="mid", width=3)


def s_rss(d: Draw) -> None:
    tile(d, 7)
    d.circle(12.5, 27.5, 2.8, fill="tint")
    d.path("M10.5 19a10.5 10.5 0 0 1 10.5 10.5M10.5 11.5a18 18 0 0 1 18 18", stroke="tint", width=3.2)


def s_bash(d: Draw) -> None:
    tile(d, 4)
    text(d, "$", 14.5, 18.5, 12, "tint", 2.8)
    d.path("M21.5 25h8", stroke="tint", width=2.8)


def s_zsh(d: Draw) -> None:
    d.rect(4.5, 7, 31, 26, 4, fill="main")
    text(d, "%", 14, 20, 9, "tint", 2.4)
    d.path("M21 25h8", stroke="mid", width=2.6)


def s_fish_outline(d: Draw) -> None:
    d.path("M5 12l6.5 8L5 28M11.5 20c4-6 9-9 14-9 5 0 9 4 10.5 9-1.5 5-5.5 9-10.5 9-5 0-10-3-14-9z", stroke="main",
           width=2.6)
    d.circle(29, 18.5, 1.7, fill="main")
    d.path("M21 15.5c1.5 3 1.5 6 0 9", stroke="mid", width=2)


def s_powershell(d: Draw) -> None:
    d.path("M10.5 7.5H36l-6.5 25H4z", fill="main", stroke="main", width=2.4)
    d.path("M13 14l7 6-7 6", stroke="tint", width=2.8)
    d.path("M20.5 27h7", stroke="tint", width=2.8)


def s_cmd(d: Draw) -> None:
    d.rect(4.5, 6, 31, 28, 3, fill="tint", stroke="main")
    d.path("M4.5 9a3 3 0 0 1 3-3h25a3 3 0 0 1 3 3v3h-31z", fill="main", stroke="main")
    d.path("M9.5 18l4.5 3.5-4.5 3.5", stroke="main", width=2.4)
    d.path("M17 27h7", stroke="mid", width=2.4)


for _value in ("LESS", "NU"):
    SYMBOLS[f"tile-{_value}"] = letter_tile(_value)

SYMBOLS.update(
    {
        "json-braces": s_json,
        "json-lines": s_json_lines,
        "har-waterfall": s_har,
        "folded-map": s_folded_map,
        "yaml-list": s_yaml,
        "toml-mark": s_toml,
        "csv-table": s_csv,
        "tsv-table": s_tsv,
        "paper-plane": s_paper_plane,
        "packed-braces": s_packed_braces,
        "byte-cells": s_byte_cells,
        "rpc-boxes": s_rpc_boxes,
        "captain-hat": s_captain_hat,
        "flat-buffer": s_flat_buffer,
        "ini-sections": s_ini,
        "sliders": s_sliders,
        "properties-kv": s_properties,
        "env-dollar": s_env,
        "plist-tree": s_plist,
        "padlock": s_padlock,
        "log-timeline": s_log,
        "git-mark": s_git,
        "cubes": s_cubes,
        "info-circle": s_info,
        "npm-tile": s_npm,
        "diff-lines": s_diff,
        "bandage": s_bandage,
        "sqlite-mark": s_sqlite,
        "access": s_access,
        "server-rack": s_server_rack,
        "dbase-table": s_dbase,
        "oracle-ring": s_oracle,
        "dolphin": s_dolphin,
        "stones": s_stones,
        "duck": s_duck,
        "firebird": s_firebird,
        "realm-ring": s_realm,
        "redis-stack": s_redis,
        "mongo-leaf": s_mongo_leaf,
        "parquet-floor": s_parquet,
        "columnar": s_columnar,
        "arrow-chevrons": s_arrow_chevrons,
        "hierarchy": s_hierarchy,
        "data-cube": s_data_cube,
        "chunk-grid": s_chunk_grid,
        "histogram-bell": s_histogram_bell,
        "scatter-line": s_scatter,
        "numpy-cube": s_numpy,
        "pickle-jar": s_pickle_jar,
        "graph-tri": s_graph_tri,
        "graph-star": s_graph_star,
        "graph-tree": s_graph_tree,
        "turtle": s_turtle,
        "rdf-triple": s_rdf,
        "triples": s_triples,
        "quads": s_quads,
        "trig-frame": s_trig,
        "safe": s_safe,
        "memo-note": s_memo,
        "fox": s_fox,
        "thumb-grid": s_thumbs,
        "btree": s_btree,
        "ram-stick": s_ram,
        "html-shield": shield_mark("5"),
        "css-shield": shield_mark("3"),
        "sass-mark": s_sass,
        "stylus-pen": s_stylus,
        "postcss-mark": s_postcss,
        "xml-tag": s_xml,
        "rss-mark": s_rss,
        "bash-tile": s_bash,
        "zsh-terminal": s_zsh,
        "fish-outline": s_fish_outline,
        "ps-tile": s_powershell,
        "cmd-window": s_cmd,
    }
)

ICONS.update(
    {
        # data
        "json": ("json-braces", None),
        "jsonc": ("json-braces", "comment"),
        "json5": ("json-braces", "text-5"),
        "jsonld": ("json-braces", "link"),
        "bson": ("json-braces", "binary"),
        "jsonl": ("json-lines", None),
        "ndjson": ("json-lines", None),
        "har": ("har-waterfall", None),
        "map": ("folded-map", None),
        "yaml": ("yaml-list", None),
        "yml": ("yaml-list", None),
        "toml": ("toml-mark", None),
        "csv": ("csv-table", None),
        "tsv": ("tsv-table", None),
        "avro": ("paper-plane", None),
        "msgpack": ("packed-braces", None),
        "cbor": ("byte-cells", None),
        "thrift": ("rpc-boxes", None),
        "capnp": ("captain-hat", None),
        "fbs": ("flat-buffer", None),
        "ini": ("ini-sections", None),
        "cfg": ("sliders", None),
        "conf": ("config", None),
        "env": ("env-dollar", None),
        "properties": ("properties-kv", None),
        "plist": ("plist-tree", None),
        "lock": ("padlock", None),
        "log": ("log-timeline", None),
        "gitignore": ("git-mark", "ban"),
        "gitattributes": ("git-mark", "text-A"),
        "gitmodules": ("git-mark", "text-M"),
        "editorconfig": ("text", "gear"),
        "reg": ("cubes", None),
        "inf": ("info-circle", None),
        "dockerignore": ("docker-whale", "ban"),
        "npmrc": ("npm-tile", "gear"),
        "diff": ("diff-lines", None),
        "patch": ("bandage", None),
        "tfstate": ("terraform-mark", "database"),
        # db
        "db": ("database", None),
        "sql": ("database", "search"),
        "dump": ("database", "download"),
        "dmp": ("database", "download"),
        "bak": ("database", "sync"),
        "dbm": ("database", "key"),
        "gdb": ("database", "web"),
        "sqlite": ("sqlite-mark", None),
        "sqlite3": ("sqlite-mark", None),
        "db-sqlite": ("sqlite-mark", None),
        "db3": ("sqlite-mark", None),
        "s3db": ("sqlite-mark", None),
        "mdb": ("access", None),
        "accdb": ("access", None),
        "laccdb": ("access", "lock"),
        "ldb": ("access", "lock"),
        "mdf": ("server-rack", None),
        "ndf": ("server-rack", "plus"),
        "ldf": ("server-rack", "text-L"),
        "dbf": ("dbase-table", None),
        "db-paradox": ("dbase-table", "text-P"),
        "dbf-oracle": ("oracle-ring", None),
        "frm": ("dolphin", "template"),
        "ibd": ("dolphin", "database"),
        "myd": ("dolphin", "text-D"),
        "myi": ("dolphin", "text-I"),
        "sst": ("stones", None),
        "duckdb": ("duck", None),
        "fdb": ("firebird", None),
        "realm": ("realm-ring", None),
        "rdb": ("redis-stack", None),
        "aof": ("redis-stack", "plus"),
        "wt": ("mongo-leaf", None),
        "parquet": ("parquet-floor", None),
        "orc": ("columnar", None),
        "arrow": ("arrow-chevrons", None),
        "feather": ("quill", None),
        "h5": ("hierarchy", None),
        "hdf5": ("hierarchy", None),
        "nc": ("data-cube", None),
        "zarr": ("chunk-grid", None),
        "mat": ("membrane", "database"),
        "rds": ("r-data", "database"),
        "rdata": ("r-data", "database"),
        "rda": ("r-data", "database"),
        "sav": ("histogram-bell", None),
        "dta": ("scatter-line", None),
        "sas7bdat": ("tile-SAS", "database"),
        "xpt": ("tile-SAS", "arrow"),
        "npy": ("numpy-cube", None),
        "npz": ("numpy-cube", "spring"),
        "pkl": ("pickle-jar", None),
        "pickle": ("pickle-jar", None),
        "joblib": ("pickle-jar", "text-J"),
        "graphml": ("graph-tri", None),
        "gexf": ("graph-star", None),
        "gml": ("graph-tree", None),
        "ttl": ("turtle", None),
        "rdf": ("rdf-triple", None),
        "owl": ("prolog-owl", None),
        "nt": ("triples", None),
        "nq": ("quads", None),
        "trig": ("trig-frame", None),
        "kdbx": ("safe", None),
        "kdb": ("safe", "text-1"),
        "dbt": ("memo-note", None),
        "fpt": ("fox", None),
        "cdx": ("fox", "text-I"),
        "db-thumbs": ("thumb-grid", None),
        "db-bdb": ("btree", None),
        "mdb-lmdb": ("ram-stick", None),
        # web
        "html": ("html-shield", None),
        "htm": ("html-shield", None),
        "xhtml": ("html-shield", "text-X"),
        "mhtml": ("html-shield", "text-M"),
        "css": ("css-shield", None),
        "scss": ("sass-mark", "braces"),
        "sass": ("sass-mark", None),
        "less": ("tile-LESS", None),
        "styl": ("stylus-pen", None),
        "pcss": ("postcss-mark", None),
        "xml": ("xml-tag", None),
        "xsl": ("xml-tag", "arrow"),
        "xslt": ("xml-tag", "arrow"),
        "xsd": ("schema", "text-X"),
        "dtd": ("xml-tag", "text-D"),
        "wsdl": ("xml-tag", "web"),
        "rss": ("rss-mark", None),
        "atom": ("rss-mark", "text-A"),
        # shell
        "sh": ("terminal", None),
        "bash": ("bash-tile", None),
        "zsh": ("zsh-terminal", None),
        "fish": ("fish-outline", None),
        "csh": ("terminal", "text-C"),
        "ksh": ("terminal", "text-K"),
        "ps1": ("ps-tile", None),
        "psm1": ("ps-tile", "text-M"),
        "bat": ("cmd-window", "gear"),
        "cmd": ("cmd-window", None),
        "nu": ("tile-NU", None),
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
