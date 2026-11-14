//! Port of `icon-pack/resolve_icon.py` (reference implementation).
//! Order: file name → magic bytes / content (first 1 KB) → extension → `mk` for Makefile → `empty`.

use crate::{generated::NAMES, index_of};

const HEAD_LIMIT: usize = 1024;

fn contains(haystack: &[u8], needle: &[u8]) -> bool {
    needle.is_empty()
        || haystack
            .windows(needle.len())
            .any(|window| window == needle)
}

fn contains_any(haystack: &[u8], needles: &[&[u8]]) -> bool {
    needles.iter().any(|needle| contains(haystack, needle))
}

fn starts_with_any(haystack: &[u8], prefixes: &[&[u8]]) -> bool {
    prefixes.iter().any(|prefix| haystack.starts_with(prefix))
}

fn equals_at(haystack: &[u8], start: usize, expected: &[u8]) -> bool {
    haystack.get(start..start + expected.len()) == Some(expected)
}

/// Like Python's `bytes.lstrip()`: strips ` \t\n\r\x0b\x0c`.
fn lstrip(h: &[u8]) -> &[u8] {
    let start = h
        .iter()
        .position(|b| !matches!(b, b' ' | b'\t' | b'\n' | b'\r' | 0x0b | 0x0c))
        .unwrap_or(h.len());
    &h[start..]
}

fn sniff(ext: &str, name: &str, h: &[u8]) -> Option<&'static str> {
    let low = h.to_ascii_lowercase();
    match ext {
        "db" => Some(if h.starts_with(b"SQLite format 3\x00") {
            "db-sqlite"
        } else if name.to_lowercase() == "thumbs.db" || h.starts_with(b"\xd0\xcf\x11\xe0") {
            "db-thumbs"
        } else if h.len() >= 16
            && [
                b"\x62\x31\x05\x00",
                b"\x00\x05\x31\x62",
                b"\x61\x15\x06\x00",
                b"\x00\x06\x15\x61",
            ]
            .iter()
            .any(|magic| equals_at(h, 12, *magic))
        {
            "db-bdb"
        } else {
            "db"
        }),
        "mdb" => (h.len() >= 20 && equals_at(h, 16, b"\xde\xc0\xef\xbe")).then_some("mdb-lmdb"),
        "ts" => (h.len() > 376 && h[0] == 0x47 && h[188] == 0x47 && h[376] == 0x47)
            .then_some("ts-stream"),
        "mts" => (h.len() > 196 && h[4] == 0x47 && h[196] == 0x47).then_some("mts-video"),
        "key" => Some(
            if contains_any(h, &[b"PRIVATE KEY", b"BEGIN OPENSSH PRIVATE"]) {
                "key-private"
            } else if h.starts_with(b"PK") {
                "key-keynote"
            } else {
                "key"
            },
        ),
        "pub" => Some(
            if starts_with_any(
                &low,
                &[
                    b"ssh-",
                    b"-----begin public",
                    b"-----begin rsa public",
                    b"---- begin ssh2 public",
                ],
            ) {
                "pub-key"
            } else {
                "pub"
            },
        ),
        "m" => Some(
            if contains_any(h, &[b"#import", b"@interface", b"@implementation"]) {
                "m-objc"
            } else if contains(&low, b"function ")
                || lstrip(h).starts_with(b"%")
                || contains(&low, b"end\n")
            {
                "m-matlab"
            } else {
                "m"
            },
        ),
        "pl" => Some(
            if contains(&low, b"use strict")
                || contains(&low[..low.len().min(80)], b"perl")
                || contains(h, b"my $")
            {
                "pl-perl"
            } else if contains(h, b":-") {
                "pl-prolog"
            } else {
                "pl"
            },
        ),
        "v" => Some(if contains(h, b"module ") && contains(h, b"endmodule") {
            "v-verilog"
        } else if contains_any(h, &[b"Require ", b"Lemma ", b"Definition ", b"Theorem "]) {
            "v-coq"
        } else if contains_any(h, &[b"fn ", b"pub fn"]) {
            "v-vlang"
        } else {
            "v"
        }),
        "obj" => Some(
            if starts_with_any(
                &h[..h.len().min(200)],
                &[b"# ", b"v ", b"mtllib", b"o ", b"g "],
            ) {
                "obj"
            } else if starts_with_any(
                h,
                &[
                    b"\x7fELF",
                    b"\xcf\xfa\xed\xfe",
                    b"\xfe\xed\xfa",
                    b"\x64\x86",
                    b"\x4c\x01",
                ],
            ) {
                "obj-object"
            } else {
                "obj"
            },
        ),
        "vhd" => Some(
            if h.starts_with(b"conectix")
                || (h.len() >= 512 && equals_at(h, h.len() - 512, b"conectix"))
            {
                "vhd"
            } else if contains_any(&low, &[b"entity ", b"architecture "]) {
                "vhd-vhdl"
            } else {
                "vhd"
            },
        ),
        "img" => (!starts_with_any(h, &[b"\x89PNG", b"\xff\xd8", b"GIF8", b"RIFF"]))
            .then_some("img-disk"),
        _ => None,
    }
}

/// Picks the best icon name for a file.
///
/// * `file_name` – file name or path (`/` and `\` are both accepted as separators).
/// * `head` – optional file content; only the first 1 KB is inspected. Without it only the name and the
///   extension are used.
///
/// Returns `"empty"` when nothing matches.
///
/// ```
/// assert_eq!(filecon::resolve("Dockerfile", None), "dockerfile");
/// assert_eq!(filecon::resolve("Makefile", None), "mk");
/// assert_eq!(filecon::resolve("clip.unknown", None), "empty");
/// ```
pub fn resolve(file_name: &str, head: Option<&[u8]>) -> &'static str {
    let name = file_name.rsplit(['/', '\\']).next().unwrap_or("");
    let lower_name = name.to_lowercase();
    let ext = match name.rfind('.') {
        Some(dot) => name[dot + 1..].to_lowercase(),
        None => lower_name.clone(),
    };
    if !name.contains('.') {
        if let Some(index) = index_of(&lower_name) {
            return NAMES[index];
        }
    }
    if let Some(head) = head {
        if let Some(candidate) = sniff(&ext, name, &head[..head.len().min(HEAD_LIMIT)]) {
            if let Some(index) = index_of(candidate) {
                return NAMES[index];
            }
        }
    }
    if let Some(index) = index_of(&ext) {
        return NAMES[index];
    }
    if lower_name == "makefile" {
        return "mk";
    }
    "empty"
}
