# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Filecon contributors
"""Prüft resolve_icon.py gegen resolve-cases.json (dient auch als Spezifikation für Ports in andere Sprachen)."""
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from resolve_icon import resolve
manifest = json.load(open(os.path.join(ROOT, "manifest.json")))
cases = json.load(open(os.path.join(HERE, "resolve-cases.json")))
tmp = tempfile.mkdtemp(); bad = []
for c in cases:
    p = os.path.join(tmp, c["file"]); open(p, "wb").write(bytes.fromhex(c["content_hex"]))
    got = resolve(p, manifest)
    if got != c["expected"]: bad.append((c["file"], c["expected"], got))
print("OK" if not bad else bad, f"- {len(cases)} Fälle")
sys.exit(1 if bad else 0)
