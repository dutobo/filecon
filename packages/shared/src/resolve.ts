// Port of icon-pack/resolve_icon.py (reference implementation).
// Order: file name -> magic bytes / content (first 1 KB) -> extension -> "mk" for Makefile -> "empty".
import { type IconName, iconNames } from "./generated/names";

const NAME_SET: ReadonlySet<string> = new Set<string>(iconNames);
const HEAD_LIMIT = 1024;

/** `true` if `name` is one of the icon names. */
export function isIconName(name: string): name is IconName {
  return NAME_SET.has(name);
}

/** Normalizes an icon name or extension (`"PDF"`, `".pdf"`) and falls back to `"empty"`. */
export function toIconName(nameOrExtension: string): IconName {
  const normalized = nameOrExtension.trim().toLowerCase().replace(/^\.+/, "");
  return isIconName(normalized) ? normalized : "empty";
}

const bytes = (text: string): Uint8Array => Uint8Array.from(text, (char) => char.charCodeAt(0));

function startsWith(h: Uint8Array, prefix: Uint8Array): boolean {
  if (h.length < prefix.length) return false;
  for (let i = 0; i < prefix.length; i++) if (h[i] !== prefix[i]) return false;
  return true;
}

const startsWithAny = (h: Uint8Array, prefixes: readonly Uint8Array[]): boolean =>
  prefixes.some((prefix) => startsWith(h, prefix));

function equalsAt(h: Uint8Array, start: number, expected: Uint8Array): boolean {
  if (start < 0 || h.length < start + expected.length) return false;
  for (let i = 0; i < expected.length; i++) if (h[start + i] !== expected[i]) return false;
  return true;
}

function includes(h: Uint8Array, needle: Uint8Array): boolean {
  outer: for (let i = 0; i + needle.length <= h.length; i++) {
    for (let j = 0; j < needle.length; j++) if (h[i + j] !== needle[j]) continue outer;
    return true;
  }
  return false;
}

const includesAny = (h: Uint8Array, needles: readonly Uint8Array[]): boolean =>
  needles.some((needle) => includes(h, needle));

/** ASCII-only lowercase, like Python's `bytes.lower()`. */
const asciiLower = (h: Uint8Array): Uint8Array => h.map((b) => (b >= 0x41 && b <= 0x5a ? b + 0x20 : b));

const WHITESPACE = new Set([0x20, 0x09, 0x0a, 0x0d, 0x0b, 0x0c]);

/** Like Python's `bytes.lstrip()` (ASCII whitespace). */
function lstrip(h: Uint8Array): Uint8Array {
  let i = 0;
  while (i < h.length && WHITESPACE.has(h[i] as number)) i++;
  return h.subarray(i);
}

const SQLITE = bytes("SQLite format 3\x00");
const OLE2 = bytes("\xd0\xcf\x11\xe0");
const BDB_MAGICS = [
  bytes("\x62\x31\x05\x00"),
  bytes("\x00\x05\x31\x62"),
  bytes("\x61\x15\x06\x00"),
  bytes("\x00\x06\x15\x61"),
];
const LMDB = bytes("\xde\xc0\xef\xbe");
const PRIVATE_KEYS = [bytes("PRIVATE KEY"), bytes("BEGIN OPENSSH PRIVATE")];
const PK = bytes("PK");
const PUBLIC_KEYS = [
  bytes("ssh-"),
  bytes("-----begin public"),
  bytes("-----begin rsa public"),
  bytes("---- begin ssh2 public"),
];
const OBJC = [bytes("#import"), bytes("@interface"), bytes("@implementation")];
const PERCENT = bytes("%");
const FUNCTION = bytes("function ");
const END_LINE = bytes("end\n");
const USE_STRICT = bytes("use strict");
const PERL = bytes("perl");
const MY_SCALAR = bytes("my $");
const PROLOG = bytes(":-");
const MODULE = bytes("module ");
const ENDMODULE = bytes("endmodule");
const COQ = [bytes("Require "), bytes("Lemma "), bytes("Definition "), bytes("Theorem ")];
const VLANG = [bytes("fn "), bytes("pub fn")];
const OBJ_TEXT = [bytes("# "), bytes("v "), bytes("mtllib"), bytes("o "), bytes("g ")];
const OBJ_BINARY = [
  bytes("\x7fELF"),
  bytes("\xcf\xfa\xed\xfe"),
  bytes("\xfe\xed\xfa"),
  bytes("\x64\x86"),
  bytes("\x4c\x01"),
];
const CONECTIX = bytes("conectix");
const VHDL = [bytes("entity "), bytes("architecture ")];
const IMAGES = [bytes("\x89PNG"), bytes("\xff\xd8"), bytes("GIF8")];
const RIFF = bytes("RIFF");

function sniff(ext: string, name: string, h: Uint8Array): string | null {
  const low = asciiLower(h);
  switch (ext) {
    case "db":
      if (startsWith(h, SQLITE)) return "db-sqlite";
      if (name.toLowerCase() === "thumbs.db" || startsWith(h, OLE2)) return "db-thumbs";
      if (h.length >= 16 && BDB_MAGICS.some((magic) => equalsAt(h, 12, magic))) return "db-bdb";
      return "db";
    case "mdb":
      return h.length >= 20 && equalsAt(h, 16, LMDB) ? "mdb-lmdb" : null;
    case "ts":
      return h.length > 376 && h[0] === 0x47 && h[188] === 0x47 && h[376] === 0x47 ? "ts-stream" : null;
    case "mts":
      return h.length > 196 && h[4] === 0x47 && h[196] === 0x47 ? "mts-video" : null;
    case "key":
      if (includesAny(h, PRIVATE_KEYS)) return "key-private";
      if (startsWith(h, PK)) return "key-keynote";
      return "key";
    case "pub":
      return startsWithAny(low, PUBLIC_KEYS) ? "pub-key" : "pub";
    case "m":
      if (includesAny(h, OBJC)) return "m-objc";
      if (includes(low, FUNCTION) || startsWith(lstrip(h), PERCENT) || includes(low, END_LINE)) return "m-matlab";
      return "m";
    case "pl":
      if (includes(low, USE_STRICT) || includes(low.subarray(0, 80), PERL) || includes(h, MY_SCALAR)) return "pl-perl";
      if (includes(h, PROLOG)) return "pl-prolog";
      return "pl";
    case "v":
      if (includes(h, MODULE) && includes(h, ENDMODULE)) return "v-verilog";
      if (includesAny(h, COQ)) return "v-coq";
      if (includesAny(h, VLANG)) return "v-vlang";
      return "v";
    case "obj":
      if (startsWithAny(h.subarray(0, 200), OBJ_TEXT)) return "obj";
      if (startsWithAny(h, OBJ_BINARY)) return "obj-object";
      return "obj";
    case "vhd":
      if (equalsAt(h, 0, CONECTIX) || (h.length >= 512 && equalsAt(h, h.length - 512, CONECTIX))) return "vhd";
      if (includesAny(low, VHDL)) return "vhd-vhdl";
      return "vhd";
    case "img":
      return startsWithAny(h, IMAGES) || startsWith(h, RIFF) ? null : "img-disk";
    default:
      return null;
  }
}

/**
 * Picks the best icon for a file.
 *
 * @param fileName file name or path (`"report.final.pdf"`, `"src/Dockerfile"`)
 * @param head optional file content; only the first 1 KB is inspected (magic bytes).
 *   Without `head` only the name and the extension are used.
 */
export function resolveIcon(fileName: string, head?: Uint8Array): IconName {
  const name = fileName.split(/[\\/]/).pop() ?? "";
  const lowerName = name.toLowerCase();
  const dot = name.lastIndexOf(".");
  const ext = dot >= 0 ? name.slice(dot + 1).toLowerCase() : lowerName;
  if (dot < 0 && isIconName(lowerName)) return lowerName;
  const candidate = head === undefined ? null : sniff(ext, name, head.subarray(0, HEAD_LIMIT));
  if (candidate !== null && isIconName(candidate)) return candidate;
  if (isIconName(ext)) return ext;
  if (lowerName === "makefile") return "mk";
  return "empty";
}
