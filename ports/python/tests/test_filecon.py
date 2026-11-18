# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import unquote

import pytest

import filecon
from filecon import _reference_resolve

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "data" / "resolve-cases.json").read_text(encoding="utf-8"))
# The icon pack of the monorepo (source of truth); absent when testing from an sdist.
PACK_DIR = HERE.parents[2] / "icon-pack"
STYLES_DIR = HERE.parents[2] / "icon-styles"
needs_pack = pytest.mark.skipif(not (PACK_DIR / "manifest.json").is_file(), reason="icon-pack/ not available")

COMBINATIONS = [
    ("default", "light", "default/light"),
    ("default", "dark", "default/dark"),
    ("gray", "light", "gray/light"),
    ("gray", "dark", "gray/dark"),
    ("solid", "light", "solid"),
    ("solid", "dark", "solid"),
    ("papered", "light", "papered/light"),
    ("papered", "dark", "papered/dark"),
    ("papered-flat", "light", "papered-flat/light"),
    ("papered-flat", "dark", "papered-flat/dark"),
    ("papered-craft", "light", "papered-craft/light"),
    ("papered-craft", "dark", "papered-craft/dark"),
    ("scratch", "light", "scratch/light"),
    ("scratch", "dark", "scratch/dark"),
    ("chalk", "light", "chalk/light"),
    ("chalk", "dark", "chalk/dark"),
]


def test_names_sorted_and_unique() -> None:
    names = filecon.names()
    assert len(names) == 703
    assert list(names) == sorted(set(names))
    assert all(filecon.is_icon_name(name) for name in names)
    assert not filecon.is_icon_name("PDF")
    assert not filecon.is_icon_name("nope")


@needs_pack
def test_names_match_manifest() -> None:
    manifest = json.loads((PACK_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert filecon.names() == tuple(sorted(manifest))


@needs_pack
@pytest.mark.parametrize(("style", "theme", "folder"), COMBINATIONS)
def test_svgs_equal_pack_files(style: filecon.Style, theme: filecon.Theme, folder: str) -> None:
    for name in filecon.names():
        base = PACK_DIR if style in ("default", "gray", "solid") else STYLES_DIR
        expected = (base / folder / f"{name}.svg").read_bytes()
        assert filecon.svg(name, style, theme).encode("utf-8") == expected, f"{folder}/{name}"


@needs_pack
def test_reference_resolver_is_byte_identical() -> None:
    assert Path(_reference_resolve.__file__).read_bytes() == (PACK_DIR / "resolve_icon.py").read_bytes()


def test_svg_structure() -> None:
    for style, theme, _ in COMBINATIONS:
        for name in ("pdf", "empty", "ts-stream"):
            doc = filecon.svg(name, style, theme)
            assert re.match(r'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"', doc)
            assert f"<title>{name}</title>" in doc
            assert doc.rstrip().endswith("</svg>")


def test_light_and_dark_differ() -> None:
    assert filecon.svg("pdf", "default", "light") != filecon.svg("pdf", "default", "dark")
    assert filecon.svg("pdf", "solid", "light") == filecon.svg("pdf", "solid", "dark")


@pytest.mark.parametrize("value", ["pdf", "PDF", ".pdf", ".PDF", "  Pdf ", "..pdf"])
def test_extension_normalisation(value: str) -> None:
    assert filecon.to_icon_name(value) == "pdf"
    assert filecon.svg(value) == filecon.svg("pdf")


@pytest.mark.parametrize("value", ["", "zzz-unknown", "../pdf", "pdf.svg", "default/light/pdf"])
def test_unknown_gives_empty(value: str) -> None:
    assert filecon.to_icon_name(value) == "empty"
    for style, theme, _ in COMBINATIONS:
        assert filecon.svg(value, style, theme) == filecon.svg("empty", style, theme)


def test_defaults() -> None:
    assert filecon.svg("pdf") == filecon.svg("pdf", "default", "light")


@pytest.mark.parametrize(("style", "theme"), [("bold", "light"), ("default", "auto"), ("Default", "light")])
def test_invalid_style_or_theme(style: str, theme: str) -> None:
    with pytest.raises(ValueError):
        filecon.svg("pdf", style, theme)  # type: ignore[arg-type]


@pytest.mark.parametrize("case", CASES, ids=[case["file"] for case in CASES])
def test_resolve_cases(case: dict[str, str]) -> None:
    head = bytes.fromhex(case["content_hex"])
    assert filecon.resolve(case["file"], head) == case["expected"]
    assert filecon.resolve(case["file"], bytearray(head)) == case["expected"]
    assert filecon.resolve(case["file"], memoryview(head)) == case["expected"]


@pytest.mark.parametrize("case", CASES, ids=[case["file"] for case in CASES])
def test_reference_resolver_agrees(case: dict[str, str], tmp_path: Path) -> None:
    file = tmp_path / case["file"]
    file.write_bytes(bytes.fromhex(case["content_hex"]))
    manifest = dict.fromkeys(filecon.names())
    assert _reference_resolve.resolve(str(file), manifest) == case["expected"]


@pytest.mark.parametrize(
    ("file_name", "expected"),
    [
        ("report.final.pdf", "pdf"),
        ("REPORT.PDF", "pdf"),
        ("src/Dockerfile", "dockerfile"),
        ("C:\\work\\Makefile", "mk"),
        (".gitignore", "gitignore"),
        ("a.db", "db"),
        ("Thumbs.db", "db"),
        ("v.ts", "ts"),
        ("unknown.zzz", "empty"),
        ("README", "empty"),
        ("", "empty"),
    ],
)
def test_resolve_without_head(file_name: str, expected: str) -> None:
    assert filecon.resolve(file_name) == expected


def test_resolve_inspects_only_first_kb() -> None:
    sqlite = b"SQLite format 3\x00"
    assert filecon.resolve("a.db", sqlite + b"\x00" * 4096) == "db-sqlite"
    assert filecon.resolve("a.key", b"\x00" * filecon.HEAD_LIMIT + b"PRIVATE KEY") == "key"
    assert filecon.resolve("a.key", b"PRIVATE KEY") == "key-private"


def test_data_uri() -> None:
    doc = filecon.svg("pdf")
    uri = filecon.data_uri(doc)
    assert uri.startswith("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2F")
    assert unquote(uri[len("data:image/svg+xml,") :]) == doc
    # Same unreserved set as JavaScript's encodeURIComponent.
    assert filecon.data_uri("a-_.!~*'() ä#") == "data:image/svg+xml,a-_.!~*'()%20%C3%A4%23"


def test_package_data_is_complete() -> None:
    root = Path(filecon.__file__).parent / "icons"
    if not root.is_dir():  # e.g. zipped install; covered by the svg tests
        pytest.skip("icons not on the file system")
    for folder in sorted({folder for _, _, folder in COMBINATIONS}):
        files = sorted(entry[:-4] for entry in os.listdir(root / folder) if entry.endswith(".svg"))
        assert tuple(files) == filecon.names(), folder
