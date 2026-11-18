#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Filecon style generator: additional icon styles drawn on top of the icon pack (icon-pack/ stays untouched).

Styles: papered (realistic sheet), papered-flat, papered-craft (cut paper), scratch (pencil sketch on a note),
chalk (chalk on a blackboard / marker on a whiteboard). Every style has a light and a dark theme.

Inputs (read only): icon-pack/manifest.json (label, color) and icon-pack/default/light/*.svg (label lettering in
Inter Bold and the line glyphs of the generic icons). Handwriting: tools/stylegen/fonts/PatrickHand-Regular.ttf (OFL).

Rules for every style, so that all Filecon packages can render them:
- no ids, <defs>, gradients, filters, masks or clip paths (inline SVGs share one id namespace, and theme="auto"
  switches attributes via CSS classes),
- light and dark markup are structurally identical; only attribute values (colors, opacity) differ,
- deterministic output (pseudo-random wobble seeded by icon + style).

Usage: python stylegen.py [--out DIR] [--names pdf,zip,...] [--styles papered,scratch,...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PACK = os.path.join(ROOT, "icon-pack")
STYLES = ("papered", "papered-flat", "papered-craft", "scratch", "chalk")
THEMES = ("light", "dark")

# ------------------------------------------------------------------ helpers


def num(v: float) -> str:
    t = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t


def num1(v: float) -> str:
    """One decimal: enough for hand-drawn strokes and handwriting on a 40x40 grid, and much smaller output."""
    t = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t


def hex_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    """Mixes color a towards b by t (0 = a, 1 = b)."""
    ra, ga, ba = hex_rgb(a)
    rb, gb, bb = hex_rgb(b)
    return "#{:02X}{:02X}{:02X}".format(
        round(ra + (rb - ra) * t), round(ga + (gb - ga) * t), round(ba + (bb - ba) * t)
    )


def rng(*parts: str) -> random.Random:
    seed = hashlib.sha256("\u0000".join(parts).encode()).hexdigest()
    return random.Random(int(seed[:16], 16))


def smooth_closed(points: list[tuple[float, float]]) -> str:
    """Closed Catmull-Rom spline through the points as cubic Béziers. Catmull-Rom control points are mirrored
    around each point, so every segment after the first is written with the shorter `S` command."""
    n = len(points)
    d = f"M{num1(points[0][0])} {num1(points[0][1])}"
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if i == 0:
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            d += f"C{num1(c1[0])} {num1(c1[1])} {num1(c2[0])} {num1(c2[1])} {num1(p2[0])} {num1(p2[1])}"
        else:
            d += f"S{num1(c2[0])} {num1(c2[1])} {num1(p2[0])} {num1(p2[1])}"
    return d + "Z"


def smooth_open(points: list[tuple[float, float]]) -> str:
    d = f"M{num1(points[0][0])} {num1(points[0][1])}"
    n = len(points)
    for i in range(n - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < n else points[i + 1]
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if i == 0:
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            d += f"C{num1(c1[0])} {num1(c1[1])} {num1(c2[0])} {num1(c2[1])} {num1(p2[0])} {num1(p2[1])}"
        else:
            d += f"S{num1(c2[0])} {num1(c2[1])} {num1(p2[0])} {num1(p2[1])}"
    return d


def resample(poly: list[tuple[float, float]], step: float, closed: bool) -> list[tuple[float, float]]:
    pts = poly + ([poly[0]] if closed else [])
    out: list[tuple[float, float]] = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        k = max(1, round(length / step))
        for j in range(k):
            out.append((x1 + (x2 - x1) * j / k, y1 + (y2 - y1) * j / k))
    if not closed:
        out.append(pts[-1])
    return out


def wobble(points, r: random.Random, amount: float):
    return [(x + r.uniform(-amount, amount), y + r.uniform(-amount, amount)) for x, y in points]


# ------------------------------------------------------------------ page geometry


class Page:
    """Page with a dog-ear (top right), like the pack, but with its own bounds."""

    def __init__(self, x0: float, y0: float, x1: float, y1: float, r: float = 3.0, fold: float = 11.0):
        self.x0, self.y0, self.x1, self.y1, self.r, self.fold = x0, y0, x1, y1, r, fold
        self.fx = x1 - fold  # start of the dog-ear on the top edge
        self.fy = y0 + fold  # end of the dog-ear on the right edge

    def path(self, dx: float = 0, dy: float = 0) -> str:
        x0, y0, x1, y1, r = self.x0 + dx, self.y0 + dy, self.x1 + dx, self.y1 + dy, self.r
        fx, fy = self.fx + dx, self.fy + dy
        return (
            f"M{num(x0 + r)} {num(y0)}H{num(fx)}L{num(x1)} {num(fy)}V{num(y1 - r)}"
            f"A{num(r)} {num(r)} 0 0 1 {num(x1 - r)} {num(y1)}H{num(x0 + r)}"
            f"A{num(r)} {num(r)} 0 0 1 {num(x0)} {num(y1 - r)}V{num(y0 + r)}"
            f"A{num(r)} {num(r)} 0 0 1 {num(x0 + r)} {num(y0)}Z"
        )

    def fold_path(self, dx: float = 0, dy: float = 0) -> str:
        """The folded-over triangle (lies on the page)."""
        fx, fy, x1, y0 = self.fx + dx, self.fy + dy, self.x1 + dx, self.y0 + dy
        return f"M{num(fx)} {num(y0)}L{num(x1)} {num(fy)}H{num(fx + 2)}A2 2 0 0 1 {num(fx)} {num(fy - 2)}Z"

    def outline_points(self) -> list[tuple[float, float]]:
        x0, y0, x1, y1, r = self.x0, self.y0, self.x1, self.y1, self.r
        corner = lambda cx, cy, a0: [  # noqa: E731
            (cx + r * math.cos(math.radians(a0 + 30 * i)), cy + r * math.sin(math.radians(a0 + 30 * i))) for i in range(4)
        ]
        return (
            [(x0 + r, y0), (self.fx, y0), (x1, self.fy)]
            + corner(x1 - r, y1 - r, 0)
            + corner(x0 + r, y1 - r, 90)
            + corner(x0 + r, y0 + r, 180)[:-1]
        )

    def fold_points(self) -> list[tuple[float, float]]:
        return [(self.fx, self.y0), (self.fx, self.fy - 2), (self.fx + 2, self.fy), (self.x1, self.fy)]


# ------------------------------------------------------------------ pack input


def load_manifest() -> dict:
    with open(os.path.join(PACK, "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


PACK_RE = {
    "glyph": re.compile(r'<g transform="translate\(([\d.]+) ([\d.]+)\) scale\(([\d.]+)\)"[^>]*>(.*?)</g>'),
    "rect": re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)"'),
    "text": re.compile(r'<path transform="translate\(([\d.-]+) ([\d.-]+)\)" d="([^"]+)" fill="[^"]+"/>'),
}


def pack_parts(name: str) -> dict:
    """Glyph, label box and Inter lettering of an icon, taken from the pack's default/light SVG."""
    with open(os.path.join(PACK, "default", "light", f"{name}.svg"), encoding="utf-8") as f:
        svg = f.read()
    parts: dict = {"glyph": None, "rect": None, "text": None}
    if m := PACK_RE["glyph"].search(svg):
        parts["glyph"] = {"x": float(m[1]), "y": float(m[2]), "scale": float(m[3]), "body": m[4]}
    if m := PACK_RE["rect"].search(svg):
        parts["rect"] = tuple(float(v) for v in m.groups())
    if m := PACK_RE["text"].search(svg):
        parts["text"] = {"x": float(m[1]), "y": float(m[2]), "d": m[3]}
    return parts


class Handwriting:
    def __init__(self, path: str):
        font = TTFont(path)
        self.glyphs, self.cmap, self.hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
        self.upm = font["head"].unitsPerEm
        self.cap = getattr(font["OS/2"], "sCapHeight", 0) or int(self.upm * 0.7)

    def path(self, text: str, size: float) -> tuple[str, float, float]:
        """Path data (baseline at y=0, starting at x=0), advance width and cap height."""
        scale = size / self.upm
        x, parts = 0.0, []
        for ch in text:
            gn = self.cmap.get(ord(ch)) or self.cmap[ord("?")]
            pen = SVGPathPen(self.glyphs, ntos=num1)
            self.glyphs[gn].draw(TransformPen(pen, (scale, 0, 0, -scale, x * scale, 0)))
            parts.append(pen.getCommands())
            x += self.hmtx[gn][0]
        return " ".join(parts), x * scale, self.cap * scale


HAND = Handwriting(os.path.join(HERE, "fonts", "PatrickHand-Regular.ttf"))


# ------------------------------------------------------------------ shared drawing parts


def glyph_svg(g: dict, stroke: str, extra: str = "", width: float = 1.5) -> str:
    return (
        f'<g transform="translate({num(g["x"])} {num(g["y"])}) scale({num(g["scale"])})" stroke="{stroke}" '
        f'stroke-width="{width / g["scale"]:.3f}" stroke-linecap="round" stroke-linejoin="round" fill="none"{extra}>'
        f'{g["body"]}</g>'
    )


def inter_label(parts: dict, fill: str, text_fill: str = "#fff", shadow: str | None = None) -> str:
    x, y, w, h, rx = parts["rect"]
    out = ""
    if shadow:
        out += f'<rect x="{num(x + 0.5)}" y="{num(y + 0.7)}" width="{num(w)}" height="{num(h)}" rx="{num(rx)}" fill="{shadow}" fill-opacity="0.22"/>'
    out += f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="{num(rx)}" fill="{fill}"/>'
    t = parts["text"]
    return out + f'<path transform="translate({num(t["x"])} {num(t["y"])})" d="{t["d"]}" fill="{text_fill}"/>'


def hand_label(text: str, cx: float, baseline: float, fill: str, max_width: float = 24.0) -> tuple[str, float]:
    size = 11.5 if len(text) <= 2 else 10.5 if len(text) == 3 else 9.2 if len(text) == 4 else 8.0
    d, width, cap = HAND.path(text, size)
    if width > max_width:
        size *= max_width / width
        d, width, cap = HAND.path(text, size)
    return f'<path transform="translate({num(cx - width / 2)} {num(baseline)})" d="{d}" fill="{fill}"/>', width


def sketch_lines(points, r: random.Random, stroke: str, width: float, closed: bool, passes: int = 2,
                 amount: float = 0.18, opacity2: float = 0.4, extra: str = "", step: float = 4.2) -> str:
    """Hand-drawn stroke: gentle wobble, a slightly offset second pass and (for closed shapes) an open start/end
    with a small overshoot, like a pencil line that does not quite meet itself."""
    out = ""
    for i in range(passes):
        pts = resample(points, step, closed)
        if closed:
            shift = r.randrange(len(pts))
            pts = pts[shift:] + pts[:shift]
            (ax, ay), (bx, by) = pts[0], pts[1]
            length = math.hypot(bx - ax, by - ay) or 1
            overshoot = r.uniform(0.6, 1.4)
            pts = pts + [pts[0], (ax + (bx - ax) / length * overshoot, ay + (by - ay) / length * overshoot)]
        pts = wobble(pts, r, amount * (1 + 0.5 * i))
        if i > 0:
            dx, dy = r.uniform(-0.35, 0.35), r.uniform(-0.35, 0.35)
            pts = [(x + dx, y + dy) for x, y in pts]
        d = smooth_open(pts)
        op = "" if i == 0 else f' stroke-opacity="{opacity2}"'
        out += (f'<path d="{d}" stroke="{stroke}" stroke-width="{num(width if i == 0 else width * 0.6)}"'
                f' stroke-linecap="round" stroke-linejoin="round"{op}{extra}/>')
    return out


def hatch_rect(x: float, y: float, w: float, h: float, gap: float, r: random.Random) -> str:
    """Diagonal hatching (45°) inside a rectangle as one path, slightly irregular."""
    d = ""
    t = -h
    while t < w:
        x_start, y_start = x + t, y + h
        x_end, y_end = x + t + h, y
        if x_start < x:
            y_start -= x - x_start
            x_start = x
        if x_end > x + w:
            y_end += x_end - (x + w)
            x_end = x + w
        if x_end > x_start:
            j = r.uniform(-0.25, 0.25)
            d += f"M{num1(x_start)} {num1(y_start + j)}L{num1(x_end)} {num1(y_end - j)}"
        t += gap
    return d


SVG_HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40" fill="none">'


def wrap(name: str, body: str) -> str:
    return f"{SVG_HEAD}<title>{name}</title>{body}</svg>\n"


# ------------------------------------------------------------------ styles


def style_papered(name: str, meta: dict, parts: dict, theme: str) -> str:
    """Realistic sheet: soft layered shadow, warm white paper, shaded dog-ear, lifted corner, slight grain."""
    page = Page(5.0, 1.0, 34.2, 37.4, r=2.4)
    dark = theme == "dark"
    paper = "#D9D3C5" if dark else "#FDFBF6"
    edge = "#B9B2A3" if dark else "#E2DBCC"
    fold = "#C7C0B1" if dark else "#EFE9DC"
    shadow = "#000000"
    r = rng(name, "papered")
    body = (
        f'<path d="{page.path(1.1, 1.6)}" fill="{shadow}" fill-opacity="{"0.35" if dark else "0.07"}"/>'
        f'<path d="{page.path(0.5, 0.7)}" fill="{shadow}" fill-opacity="{"0.3" if dark else "0.08"}"/>'
        f'<path d="{page.path()}" fill="{paper}" stroke="{edge}" stroke-width="0.6" stroke-linejoin="round"/>'
    )
    # paper grain: a few faint fibres
    fibres = ""
    for _ in range(7):
        x, y = r.uniform(8, 30), r.uniform(15, 35)
        fibres += f"M{num(x)} {num(y)}l{num(r.uniform(1.2, 2.6))} {num(r.uniform(-0.4, 0.4))}"
    body += f'<path d="{fibres}" stroke="#8A7F68" stroke-opacity="{"0.25" if dark else "0.14"}" stroke-width="0.35" stroke-linecap="round"/>'
    # lifted bottom-right corner
    x1, y1 = page.x1, page.y1
    body += (f'<path d="M{num(x1 - 7)} {num(y1)}Q{num(x1 - 1.5)} {num(y1 - 0.8)} {num(x1)} {num(y1 - 6)}'
             f'V{num(y1 - 2.4)}A2.4 2.4 0 0 1 {num(x1 - 2.4)} {num(y1)}Z" fill="{shadow}" fill-opacity="{"0.16" if dark else "0.06"}"/>')
    # dog-ear: shadow on the page, then the folded flap
    body += (f'<path d="M{num(page.fx)} {num(page.y0)}L{num(page.x1)} {num(page.fy)}L{num(page.fx - 0.6)} {num(page.fy + 1.4)}Z" '
             f'fill="{shadow}" fill-opacity="{"0.3" if dark else "0.09"}"/>'
             f'<path d="{page.fold_path()}" fill="{fold}" stroke="{edge}" stroke-width="0.6" stroke-linejoin="round"/>')
    return wrap(name, body + content_inter(parts, meta, theme, shadow=shadow))


def style_papered_flat(name: str, meta: dict, parts: dict, theme: str) -> str:
    """Flat like the default style, but warm paper, fine grain and a subtle offset shadow."""
    page = Page(4.75, 0.75, 34.6, 38.6, r=3.25)
    dark = theme == "dark"
    paper = "#2B2823" if dark else "#FFFCF4"
    outline = "#4D473D" if dark else "#E6DDCB"
    fold = "#38342D" if dark else "#F3ECDD"
    r = rng(name, "papered-flat")
    body = (
        f'<path d="{page.path(0.6, 0.8)}" fill="#000000" fill-opacity="{"0.35" if dark else "0.06"}"/>'
        f'<path d="{page.path()}" fill="{paper}" stroke="{outline}" stroke-width="1.2" stroke-linejoin="round"/>'
        f'<path d="{page.fold_path()}" fill="{fold}" stroke="{outline}" stroke-width="1.2" stroke-linejoin="round"/>'
    )
    dots = "".join(
        f"M{num(r.uniform(8, 31))} {num(r.uniform(6, 36))}h0.01" for _ in range(6)
    )
    body += f'<path d="{dots}" stroke="{"#5A5348" if dark else "#DDD3BF"}" stroke-width="0.5" stroke-linecap="round"/>'
    return wrap(name, body + content_inter(parts, meta, theme))


def style_papered_craft(name: str, meta: dict, parts: dict, theme: str) -> str:
    """Cut paper: colored back sheet, tinted front sheet, layer shadows, label as a cut strip."""
    color = meta.get("color") or "#7F56D9"
    dark = theme == "dark"
    page = Page(6.6, 1.2, 35.0, 37.6, r=2.2)
    back = mix(color, "#000000", 0.35 if dark else 0.1)
    front = mix(color, "#18181B", 0.72) if dark else mix(color, "#FFFFFF", 0.84)
    fold = mix(color, "#18181B", 0.55) if dark else mix(color, "#FFFFFF", 0.66)
    body = (
        f'<path d="{page.path(-2.4, 1.6)}" fill="{back}"/>'
        f'<path d="{page.path(0.5, 0.8)}" fill="#000000" fill-opacity="{"0.45" if dark else "0.16"}"/>'
        f'<path d="{page.path()}" fill="{front}"/>'
        f'<path d="M{num(page.fx)} {num(page.y0)}L{num(page.x1)} {num(page.fy)}L{num(page.fx - 0.4)} {num(page.fy + 1.2)}Z" '
        f'fill="#000000" fill-opacity="{"0.4" if dark else "0.12"}"/>'
        f'<path d="{page.fold_path()}" fill="{fold}"/>'
    )
    if parts["rect"]:
        x, y, w, h, _ = parts["rect"]
        r = rng(name, "papered-craft")
        # cut strip: slightly irregular quadrilateral instead of a rounded rect
        quad = [(x + r.uniform(0, 0.5), y + r.uniform(-0.3, 0.3)), (x + w + r.uniform(-0.4, 0.4), y + r.uniform(-0.3, 0.3)),
                (x + w + r.uniform(-0.4, 0.4), y + h + r.uniform(-0.3, 0.3)), (x + r.uniform(0, 0.5), y + h + r.uniform(-0.3, 0.3))]
        poly = "M" + "L".join(f"{num(px)} {num(py)}" for px, py in quad) + "Z"
        shadow_poly = "M" + "L".join(f"{num(px + 0.5)} {num(py + 0.8)}" for px, py in quad) + "Z"
        t = parts["text"]
        body += (f'<path d="{shadow_poly}" fill="#000000" fill-opacity="{"0.5" if dark else "0.2"}"/>'
                 f'<path d="{poly}" fill="{color}"/>'
                 f'<path transform="translate({num(t["x"])} {num(t["y"])})" d="{t["d"]}" fill="#fff"/>')
    elif parts["glyph"]:
        ink = mix(color, "#FFFFFF", 0.35) if dark else mix(color, "#000000", 0.1)
        body += glyph_svg(parts["glyph"], ink, width=1.7)
    return wrap(name, body)


def content_inter(parts: dict, meta: dict, theme: str, shadow: str | None = None) -> str:
    """Label (pack lettering, Inter Bold) or glyph in the icon color – shared by papered and papered-flat."""
    color = meta.get("color") or "#7F56D9"
    if parts["rect"]:
        return inter_label(parts, color, shadow=shadow)
    if parts["glyph"]:
        ink = mix(color, "#FFFFFF", 0.25) if theme == "dark" and color in ("#475467", "#667085") else color
        return glyph_svg(parts["glyph"], ink)
    return ""


def style_scratch(name: str, meta: dict, parts: dict, theme: str) -> str:
    """Pencil sketch on a note sheet. The sheet stays light in the dark theme (only dimmed)."""
    dark = theme == "dark"
    page = Page(5.2, 1.4, 34.6, 38.0, r=2.6)
    paper = "#E9E4D6" if dark else "#FFFDF6"
    rule = "#7FA3D1"
    margin = "#E07A7A"
    graphite = "#46464E"
    r = rng(name, "scratch")
    body = f'<path d="{page.path()}" fill="{paper}"/>'
    # ruled note paper + margin line
    rules = "".join(f"M{num(page.x0 + 1.2)} {num(y)}H{num(page.x1 - 1.2)}" for y in (17.0, 22.5, 28.0, 33.5))
    body += (f'<path d="{rules}" stroke="{rule}" stroke-opacity="{"0.4" if dark else "0.35"}" stroke-width="0.45"/>'
             f'<path d="M{num(page.x0 + 4.2)} {num(page.y0 + 1)}V{num(page.y1 - 1)}" stroke="{margin}" '
             f'stroke-opacity="{"0.45" if dark else "0.4"}" stroke-width="0.45"/>')
    body += sketch_lines(page.outline_points(), r, graphite, 0.95, closed=True)
    body += sketch_lines(page.fold_points(), r, graphite, 0.85, closed=False, step=3.0)
    label = meta.get("label")
    if label:
        text, width = hand_label(label, 20.4, 30.2, graphite)
        bx, bw = 20.4 - width / 2 - 2.2, width + 4.4
        box = [(bx, 21.4), (bx + bw, 21.4), (bx + bw, 32.6), (bx, 32.6)]
        body += f'<path d="{hatch_rect(bx + 0.6, 22.0, bw - 1.2, 10.0, 1.6, r)}" stroke="{graphite}" stroke-opacity="0.18" stroke-width="0.4" stroke-linecap="round"/>'
        body += sketch_lines(box, r, graphite, 0.75, closed=True, amount=0.15, opacity2=0.35, step=3.5)
        body += text
    elif parts["glyph"]:
        g = parts["glyph"]
        body += glyph_svg(g, graphite, width=1.35)
        body += glyph_svg({**g, "x": g["x"] + 0.35, "y": g["y"] + 0.25}, graphite, ' stroke-opacity="0.35"', width=0.9)
    return wrap(name, body)


def style_chalk(name: str, meta: dict, parts: dict, theme: str) -> str:
    """Dark: chalk on a blackboard. Light: colored marker on a whiteboard."""
    dark = theme == "dark"
    color = meta.get("color") or "#7F56D9"
    page = Page(5.0, 1.2, 34.8, 38.2, r=2.8)
    board = "#27352D" if dark else "#FFFFFF"
    frame = "#3D4E44" if dark else "#D0D5DD"
    line = "#EDEEE8" if dark else "#344054"
    accent = mix(color, "#FFFFFF", 0.5) if dark else color
    r = rng(name, "chalk")
    dash = ' stroke-dasharray="5 0.9 2.5 0.6 7 1.1 3 0.7"'
    body = f'<path d="{page.path()}" fill="{board}" stroke="{frame}" stroke-width="0.8"/>'
    # smudges (chalk dust / dry marker residue)
    smudge = "".join(
        f"M{num(r.uniform(9, 28))} {num(r.uniform(6, 34))}h{num(r.uniform(2.5, 5))}" for _ in range(3)
    )
    body += f'<path d="{smudge}" stroke="{line}" stroke-opacity="{"0.06" if dark else "0.035"}" stroke-width="2.4" stroke-linecap="round"/>'
    body += sketch_lines(page.outline_points(), r, line, 1.25, closed=True, passes=2, amount=0.16, opacity2=0.3, extra=dash)
    body += sketch_lines(page.fold_points(), r, line, 1.1, closed=False, passes=1, amount=0.12, extra=dash, step=3.0)
    label = meta.get("label")
    if label:
        text, width = hand_label(label, 20.0, 29.6, accent)
        under = [(20.0 - width / 2 - 1, 32.4), (20.0, 32.0), (20.0 + width / 2 + 1, 32.5)]
        body += text + sketch_lines(under, r, accent, 1.0, closed=False, passes=1, amount=0.12, step=3.0)
    elif parts["glyph"]:
        body += glyph_svg(parts["glyph"], accent, dash, width=1.6)
    return wrap(name, body)


RENDER = {
    "papered": style_papered,
    "papered-flat": style_papered_flat,
    "papered-craft": style_papered_craft,
    "scratch": style_scratch,
    "chalk": style_chalk,
}

# ------------------------------------------------------------------ checks + main

ATTR_VALUE = re.compile(r'="[^"]*"')


def check_same_structure(light: str, dark: str, label: str) -> None:
    if ATTR_VALUE.sub('=""', light) != ATTR_VALUE.sub('=""', dark):
        raise SystemExit(f"{label}: light and dark markup differ structurally")
    if re.search(r"<(defs|linearGradient|radialGradient|filter|mask|clipPath)\b|\sid=", light):
        raise SystemExit(f"{label}: uses ids/defs (not allowed)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "icon-styles"))
    ap.add_argument("--names", default="")
    ap.add_argument("--styles", default=",".join(STYLES))
    args = ap.parse_args()
    manifest = load_manifest()
    names = [n for n in args.names.split(",") if n] or sorted(manifest)
    styles = [s for s in args.styles.split(",") if s]
    for name in names:
        if name not in manifest:
            raise SystemExit(f"unknown icon: {name}")
    count = 0
    for style in styles:
        render = RENDER[style]
        for name in names:
            parts = pack_parts(name)
            svgs = {theme: render(name, manifest[name], parts, theme) for theme in THEMES}
            check_same_structure(svgs["light"], svgs["dark"], f"{style}/{name}")
            for theme, svg in svgs.items():
                folder = os.path.join(args.out, style, theme)
                os.makedirs(folder, exist_ok=True)
                with open(os.path.join(folder, f"{name}.svg"), "w", encoding="utf-8", newline="") as f:
                    f.write(svg)
                count += 1
    print(f"stylegen: {len(styles)} styles x {len(names)} icons -> {count} files in {args.out}")


if __name__ == "__main__":
    sys.exit(main())
