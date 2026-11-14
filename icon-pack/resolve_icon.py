#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Filecon contributors
"""
Wählt das beste Icon für eine Datei: Dateiname -> Magic-Bytes/Inhalt -> Endung -> Familien-Fallback -> empty.
Benutzung:  python3 resolve_icon.py pfad/zur/datei.db [manifest.json]
In Code:    from resolve_icon import resolve; resolve("foo.ts")  -> "ts" | "ts-stream" | ...
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def _head(path, n=1024):
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except OSError:
        return b""

def _sniff(ext, name, h):
    low = h.lower()
    if ext == "db":
        if h.startswith(b"SQLite format 3\x00"): return "db-sqlite"
        if name.lower() == "thumbs.db" or h.startswith(b"\xd0\xcf\x11\xe0"): return "db-thumbs"
        if len(h) >= 16 and h[12:16] in (b"\x62\x31\x05\x00", b"\x00\x05\x31\x62", b"\x61\x15\x06\x00", b"\x00\x06\x15\x61"): return "db-bdb"
        return "db"
    if ext == "mdb" and len(h) >= 20 and h[16:20] == b"\xde\xc0\xef\xbe": return "mdb-lmdb"
    if ext == "ts" and len(h) > 376 and h[0] == h[188] == h[376] == 0x47: return "ts-stream"
    if ext == "mts" and len(h) > 196 and h[4] == h[196] == 0x47: return "mts-video"
    if ext == "key":
        if b"PRIVATE KEY" in h or b"BEGIN OPENSSH PRIVATE" in h: return "key-private"
        if h.startswith(b"PK"): return "key-keynote"
        return "key"
    if ext == "pub":
        if low.startswith((b"ssh-", b"-----begin public", b"-----begin rsa public", b"---- begin ssh2 public")): return "pub-key"
        return "pub"
    if ext == "m":
        if b"#import" in h or b"@interface" in h or b"@implementation" in h: return "m-objc"
        if b"function " in low or h.lstrip().startswith(b"%") or b"end\n" in low: return "m-matlab"
        return "m"
    if ext == "pl":
        if b"use strict" in low or b"perl" in low[:80] or b"my $" in h: return "pl-perl"
        if b":-" in h: return "pl-prolog"
        return "pl"
    if ext == "v":
        if b"module " in h and b"endmodule" in h: return "v-verilog"
        if b"Require " in h or b"Lemma " in h or b"Definition " in h or b"Theorem " in h: return "v-coq"
        if b"fn " in h or b"pub fn" in h: return "v-vlang"
        return "v"
    if ext == "obj":
        txt = h[:200]
        if txt.startswith((b"# ", b"v ", b"mtllib", b"o ", b"g ")): return "obj"
        if h.startswith((b"\x7fELF", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa", b"\x64\x86", b"\x4c\x01")): return "obj-object"
        return "obj"
    if ext == "vhd":
        if h[:8] == b"conectix" or h[-512:-504] == b"conectix": return "vhd"
        if b"entity " in low or b"architecture " in low: return "vhd-vhdl"
        return "vhd"
    if ext == "img" and not (h.startswith((b"\x89PNG", b"\xff\xd8", b"GIF8")) or h[:4] == b"RIFF"): return "img-disk"
    return None

def resolve(path, manifest=None):
    if manifest is None:
        manifest = json.load(open(os.path.join(HERE, "manifest.json")))
    name = os.path.basename(path)
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else name.lower()
    if name.lower() in manifest and "." not in name:  # z. B. "Dockerfile"
        return name.lower()
    cand = _sniff(ext, name, _head(path)) if os.path.exists(path) else None
    if cand and cand in manifest: return cand
    if ext in manifest: return ext
    if name.lower() == "makefile": return "mk"
    return "empty"

if __name__ == "__main__":
    print(resolve(sys.argv[1], json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None))
