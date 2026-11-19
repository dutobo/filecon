# SPDX-License-Identifier: Apache-2.0
"""Filecon – file-type icons for 703 formats in nine styles, plus a file-type resolver.

>>> import filecon
>>> filecon.resolve("report.final.pdf")
'pdf'
>>> filecon.svg("pdf").startswith("<svg")
True
>>> filecon.resolve("app.db", b"SQLite format 3\\x00")
'db-sqlite'

The SVGs are the unmodified files of the Filecon icon pack and its generated styles (40x40, ``viewBox="0 0 40 40"``, including a
``<title>`` with the icon name), shipped as package data.
"""

from __future__ import annotations

import functools
from importlib.resources import files
from typing import Literal
from urllib.parse import quote

from ._names import NAMES
from ._resolve import HEAD_LIMIT, resolve

__version__ = "0.3.1"

__all__ = [
    "HEAD_LIMIT",
    "STYLES",
    "THEMES",
    "Style",
    "Theme",
    "data_uri",
    "is_icon_name",
    "names",
    "resolve",
    "svg",
    "to_icon_name",
]

Style = Literal["default", "gray", "solid", "papered", "papered-flat", "papered-craft", "scratch", "chalk", "iconic"]
"""``default``: outline with a colored label, ``gray``: filled gray page, ``solid``: filled colored page,
``papered``: realistic paper sheet, ``papered-flat``: flat paper, ``papered-craft``: cut paper,
``scratch``: pencil sketch on a note, ``chalk``: whiteboard marker (light) or blackboard chalk (dark),
``iconic``: a standalone, self-drawn symbol per file type instead of a page shape."""

Theme = Literal["light", "dark"]
"""Color theme; ``solid`` looks the same in both themes."""

STYLES: tuple[Style, ...] = (
    "default",
    "gray",
    "solid",
    "papered",
    "papered-flat",
    "papered-craft",
    "scratch",
    "chalk",
    "iconic",
)
THEMES: tuple[Theme, ...] = ("light", "dark")

_NAME_SET = frozenset(NAMES)


def names() -> tuple[str, ...]:
    """All icon names, sorted."""
    return NAMES


def is_icon_name(name: str) -> bool:
    """``True`` if ``name`` is one of the icon names (exact, case-sensitive)."""
    return name in _NAME_SET


def to_icon_name(name_or_extension: str) -> str:
    """Normalizes an icon name or extension (``"PDF"``, ``".pdf"``) and falls back to ``"empty"``."""
    normalized = name_or_extension.strip().lower().lstrip(".")
    return normalized if normalized in _NAME_SET else "empty"


def svg(name: str, style: Style = "default", theme: Theme = "light") -> str:
    """The SVG document of an icon.

    :param name: icon name or extension (``"pdf"``, ``".PDF"``); unknown names give the ``empty`` icon.
    :param style: one of :data:`STYLES`, e.g. ``"default"``, ``"solid"`` or ``"scratch"``.
    :param theme: ``"light"`` or ``"dark"`` (ignored for ``"solid"``).
    :raises ValueError: for an unknown style or theme.
    """
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}, not {style!r}")
    if theme not in THEMES:
        raise ValueError(f"theme must be one of {THEMES}, not {theme!r}")
    return _read(to_icon_name(name), style, "light" if style == "solid" else theme)


@functools.lru_cache(maxsize=256)
def _read(name: str, style: str, theme: str) -> str:
    folder = files(__name__) / "icons" / style
    if style != "solid":
        folder = folder / theme
    return (folder / f"{name}.svg").read_bytes().decode("utf-8")


def data_uri(svg: str) -> str:
    """A ``data:`` URI for an SVG string (for ``<img src>`` or CSS ``url()``), percent-encoded like
    JavaScript's ``encodeURIComponent``."""
    return "data:image/svg+xml," + quote(svg, safe="!~*'()")
