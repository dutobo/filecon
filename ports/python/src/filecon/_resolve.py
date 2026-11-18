# SPDX-License-Identifier: Apache-2.0
"""File-type resolver: file name -> magic bytes / content (first 1 KB) -> extension -> "mk" for Makefile -> "empty".

Same order and results as the reference implementation ``icon-pack/resolve_icon.py``, but it works on a file
name plus optional content bytes instead of reading from disk. The content rules are the reference's own
``_sniff`` (byte-identical copy in ``_reference_resolve``).
"""

from __future__ import annotations

import re

from ._names import NAMES
from ._reference_resolve import _sniff

HEAD_LIMIT = 1024
"""Only the first 1 KB of the content is inspected."""

_NAME_SET = frozenset(NAMES)
_SEPARATORS = re.compile(r"[\\/]")


def resolve(file_name: str, head: bytes | None = None) -> str:
    """Picks the best icon name for a file.

    :param file_name: file name or path, e.g. ``"report.final.pdf"`` or ``"src/Dockerfile"`` (both ``/`` and
        ``\\`` separate directories).
    :param head: optional file content (any bytes-like object); only the first 1 KB is inspected (magic bytes).
        Without ``head`` only the name and the extension are used.
    :return: one of :func:`filecon.names`; ``"empty"`` if nothing matches.
    """
    name = _SEPARATORS.split(file_name)[-1]
    lower_name = name.lower()
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else lower_name
    if "." not in name and lower_name in _NAME_SET:  # e.g. "Dockerfile"
        return lower_name
    candidate = _sniff(ext, name, bytes(head[:HEAD_LIMIT])) if head is not None else None
    if candidate and candidate in _NAME_SET:
        return candidate
    if ext in _NAME_SET:
        return ext
    if lower_name == "makefile":
        return "mk"
    return "empty"
