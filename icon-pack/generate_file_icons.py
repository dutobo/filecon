#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Filecon contributors
"""
Filecon – Generator für Datei-Icons im Stil von Untitled UI: drei Stile (default / gray / solid),
Seite mit Eselsohr, Endungs-Label, Linien-Glyphen für generische Typen.

Alle Formen werden hier selbst gezeichnet -> keine fremden Icon-Assets.
Label-Text wird als Pfad aus einer Schrift (Standard: Inter Bold, SIL OFL)
umgewandelt, die SVGs brauchen also keine Schrift beim Anzeigen.

Aufruf:  python3 generate_file_icons.py [ausgabeordner] [pfad/zur/Inter-Bold.otf]
"""
import json, sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = sys.argv[1] if len(sys.argv) > 1 else "file-icons"
FONT_CANDIDATES = [
    sys.argv[2] if len(sys.argv) > 2 else None,
    "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "/usr/share/fonts/truetype/inter/Inter-Bold.ttf",
    "Inter-Bold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_PATH = next(p for p in FONT_CANDIDATES if p and os.path.exists(p))
FONT = TTFont(FONT_PATH)
GLYPHS, CMAP, HMTX = FONT.getGlyphSet(), FONT.getBestCmap(), FONT["hmtx"]
UPM = FONT["head"].unitsPerEm
CAP = getattr(FONT["OS/2"], "sCapHeight", 0) or int(UPM * 0.72)

# ---------------------------------------------------------------- Stile
# default: Umriss + farbiges Label/Glyph | gray: gefüllte graue Seite | solid: gefüllte Farbseite
OUTLINE = {"dark": "#3F3F46", "light": "#D5D7DA"}
PAGE_FILL = {"dark": "none", "light": "#FFFFFF"}
GRAY = {  # Seite, Eselsohr, Glyph/Text
    "dark":  {"page": "#25282F", "fold": "#171A1F", "ink": "#A9ADB7"},
    "light": {"page": "#F5F5F5", "fold": "#E4E7EC", "ink": "#414651"},
}
SOLID_INK, SOLID_FOLD = "#FFFFFF", ('#FFFFFF', 0.32)

# ---------------------------------------------------------------- Farben
CAT_COLOR = {
    "lang": "#7F56D9", "shell": "#475467", "web": "#E04F16", "data": "#0E9384", "db": "#099250",
    "ml": "#7A5AF8", "text": "#667085", "docs": "#1570EF", "sheet": "#079455", "slides": "#E04F16",
    "book": "#B54708", "mail": "#1570EF", "img": "#7F56D9", "design": "#E62E05", "audio": "#DD2590",
    "video": "#444CE7", "archive": "#B54708", "disk": "#667085", "pkg": "#B54708", "exec": "#475467",
    "font": "#6172F3", "3d": "#0BA5EC", "cad": "#0086C9", "gis": "#12B76A", "cert": "#DC6803",
    "net": "#444CE7", "game": "#7F56D9", "misc": "#667085",
}
EXT_COLOR = {  # Marken-/Wiedererkennungsfarben (dunkel genug für weiße Schrift)
    "js": "#B7791F", "mjs": "#B7791F", "cjs": "#B7791F", "jsx": "#0891B2",
    "ts": "#3178C6", "tsx": "#3178C6", "mts": "#3178C6", "cts": "#3178C6", "py": "#3B7BBF", "pyw": "#3B7BBF",
    "java": "#D96C00", "jar": "#D96C00", "class": "#D96C00", "kt": "#7F52FF",
    "kts": "#7F52FF", "swift": "#F05138", "c": "#00599C", "h": "#00599C",
    "cpp": "#0A6CB8", "hpp": "#0A6CB8", "cc": "#0A6CB8", "cs": "#68217A",
    "go": "#0A9CC4", "rs": "#B7410E", "rb": "#CC342D", "php": "#6C71B5",
    "lua": "#3F40A3", "r": "#276DC3", "scala": "#DC322F", "dart": "#0175C2",
    "hs": "#5E5086", "ex": "#6E4A7E", "exs": "#6E4A7E", "erl": "#A90533",
    "clj": "#5881D8", "cljs": "#5881D8", "elm": "#1293D8", "fs": "#378BBA",
    "ml": "#E98407", "vb": "#68217A", "jl": "#9558B2", "nim": "#C99F00",
    "zig": "#E8830C", "d": "#B03931", "cr": "#4B5563",
    "groovy": "#4298B8", "gradle": "#0B7285", "sol": "#4B5563",
    "vue": "#2F9E6F", "svelte": "#E8431C", "astro": "#6D28D9",
    "wasm": "#654FF0", "wat": "#654FF0", "graphql": "#E10098", "gql": "#E10098",
    "tf": "#7B42BC", "hcl": "#7B42BC", "nix": "#5277C3", "dockerfile": "#1D63ED",
    "html": "#E34F26", "htm": "#E34F26", "css": "#1572B6", "scss": "#CC6699",
    "sass": "#CC6699", "less": "#2B5CA8", "styl": "#2F8F4E", "xml": "#E8830C",
    "xsl": "#E8830C", "json": "#475467", "jsonc": "#475467", "json5": "#475467",
    "yaml": "#B42318", "yml": "#B42318", "toml": "#9C4221", "csv": "#079455",
    "tsv": "#079455", "sql": "#0086C9", "sqlite": "#0F80CC", "sqlite3": "#0F80CC", "md": "#344054",
    "mdx": "#F59E0B", "pdf": "#D92D20", "doc": "#1570EF", "docx": "#1570EF",
    "xls": "#079455", "xlsx": "#079455", "ppt": "#E04F16", "pptx": "#E04F16",
    "ai": "#E62E05", "psd": "#1570EF", "indd": "#C11574", "fig": "#7A5AF8",
    "sketch": "#F79009", "xd": "#C11574", "aep": "#6938EF", "prproj": "#6938EF",
    "avi": "#1570EF", "img": "#7F56D9", "svg": "#F79009", "sh": "#2F9E44",
    "bash": "#2F9E44", "zsh": "#2F9E44", "fish": "#2F9E44", "ps1": "#2671BE",
    "bat": "#475467", "cmd": "#475467", "gitignore": "#E64A19", "ipynb": "#E8831C",
    "pt": "#EE4C2C", "pth": "#EE4C2C", "onnx": "#4B5563", "tflite": "#E8831C", "keras": "#C62828",
    "kdbx": "#2F9E44", "docm": "#1570EF", "xlsm": "#079455", "pptm": "#E04F16",
}
LABEL = {  # Label max. 5 Zeichen; unbekannte >5 werden automatisch auf 5 gekürzt
    "dockerfile": "DOCK", "gitignore": "GIT", "properties": "PROP", "torrent": "TORR",
    "sqlite": "SQLT", "sqlite3": "SQLT", "gradle": "GRDL", "prisma": "PRSM", "svelte": "SVLT",
    "parquet": "PRQT", "sketch": "SKTCH", "prproj": "PRPRJ", "numbers": "NUMB", "graphql": "GQL",
    "groovy": "GRVY", "gemspec": "GEMSP", "applescript": "ASCPT", "safetensors": "SAFE",
    "tfrecord": "TFREC", "mlmodel": "MLMDL", "editorconfig": "EDCFG", "gitattributes": "GITAT",
    "gitmodules": "GITMD", "dockerignore": "DIGN", "unitypackage": "UNITY", "keystore": "KEYST",
    "appimage": "APPIM", "fcpxml": "FCPXM", "logicx": "LOGIC", "afdesign": "AFDES", "afphoto": "AFPHO",
    "catpart": "CATP", "sldprt": "SLDPT", "sldasm": "SLDAS", "mbtiles": "MBTIL", "topojson": "TOPO",
    "geojson": "GEOJS", "aseprite": "ASEPR", "laccdb": "LACDB", "sas7bdat": "SAS7", "squashfs": "SQFS",
    "gdshader": "GDSH", "jsonnet": "JSNNT", "pcapng": "PCAPN", "uasset": "UASST", "pickle": "PKL",
    "joblib": "JBLIB", "feather": "FTHR", "duckdb": "DUCK", "tfstate": "TFSTA", "tfvars": "TFVAR",
    "markdown": "MD", "jsonld": "JSNLD", "msgpack": "MSGPK", "capnp": "CAPNP", "thrift": "THRFT",
    "npmrc": "NPMRC", "midi": "MIDI", "alac": "ALAC", "aup3": "AUP3", "logicx ": "LOGIC",
}

# ---------------------------------------------------------------- Endungen je Kategorie
EXTENSIONS = {
 "lang": "js mjs cjs jsx ts mts cts tsx vue svelte astro coffee ejs hbs pug njk py pyw ipynb pyi pyx pyc pyd "
         "java kt kts scala groovy gradle c h cpp hpp cc cxx hxx hh cs csx cu cuh mm rs go zig d nim cr asm s odin ada adb ads "
         "hs lhs ml mli fs fsx fsi ex exs erl hrl clj cljs cljc edn elm purs gleam scm rkt lisp el lean agda idr "
         "rb rake gemspec php pm lua r rmd jl tcl awk ahk applescript scpt swift dart mojo vb vbs bas cob cbl pas dpr "
         "f90 f f95 for sas sol vy move vhdl sv svh glsl vert frag hlsl wgsl metal gdshader ino gd proto graphql gql prisma "
         "tf tfvars hcl nix cmake dockerfile mk bzl ninja rego cue dhall jsonnet wasm wat",
 "shell": "sh bash zsh fish ps1 psm1 bat cmd csh ksh nu",
 "web": "html htm xhtml css scss sass less styl pcss xml xsl xslt xsd dtd wsdl rss atom mhtml",
 "data": "json jsonc jsonl json5 ndjson jsonld har map yaml yml toml csv tsv avro msgpack cbor bson thrift capnp fbs "
         "ini cfg conf env properties plist lock log gitignore editorconfig reg inf gitattributes gitmodules dockerignore "
         "npmrc diff patch tfstate",
 "db": "sql dump bak sqlite sqlite3 db3 s3db mdb accdb laccdb mdf ndf ldf dbf dmp frm ibd myd myi ldb sst dbm duckdb "
       "fdb gdb realm rdb aof wt parquet orc arrow feather h5 hdf5 nc zarr mat rds rdata rda sav dta sas7bdat xpt "
       "npy npz pkl pickle joblib graphml gexf gml ttl rdf owl nt nq trig kdbx kdb dbt fpt cdx",
 "ml": "pt pth ckpt safetensors onnx gguf tflite keras mlmodel tfrecord",
 "text": "txt text md markdown mdx rst adoc org rtf tex bib cls sty srt vtt ass ssa sub",
 "docs": "doc docx docm dot dotx odt ott wpd pdf pages xps oxps djvu vsd vsdx one pub mpp",
 "sheet": "xls xlsx xlsm xlsb xltx ods numbers",
 "slides": "ppt pptx pptm pps ppsx potx odp",
 "book": "epub mobi azw3 fb2 cbz cbr",
 "mail": "ics vcf eml msg mbox pst ost emlx",
 "img": "png jpg jpeg gif webp bmp ico icns cur tiff tif heic heif avif jxl jp2 tga pcx pbm pgm ppm dds ktx ktx2 exr hdr "
        "raw cr2 cr3 nef arw dng orf raf rw2 svg svgz img wmf emf",
 "design": "psd psb xcf kra ora clip ai eps cdr indd fig sketch xd afdesign afphoto aep prproj drp fcpxml veg",
 "audio": "mp3 wav flac aac ogg m4a wma aiff aif mid midi opus amr ape alac wv mka ac3 dts caf au m3u m3u8 pls sf2 sfz "
          "als flp logicx ptx cpr rpp aup3 band",
 "video": "mp4 mov avi mkv webm flv wmv mpeg mpg m4v 3gp m2ts ogv vob divx asf rm rmvb mpd",
 "archive": "zip rar 7z tar gz bz2 xz tgz tbz2 txz zst lz4 lzma cab arj lzh zipx z",
 "disk": "iso dmg vhd vhdx vmdk vdi qcow2 ova ovf wim squashfs cpio vmx vbox",
 "pkg": "deb rpm apk ipa msi pkg jar war ear whl egg gem nupkg aab xapk msix appx snap appimage xpi crx vsix unitypackage",
 "exec": "exe dll so dylib bin class o a lib ko elf out com sys scr ocx drv efi dex rom hex uf2 axf bit pdb mdmp core",
 "font": "ttf otf woff woff2 eot ttc otc fon pfb bdf pcf",
 "3d": "obj fbx stl gltf glb blend 3ds dae ply 3mf amf usd usda usdc usdz abc max ma mb c4d x3d wrl mtl",
 "cad": "dwg dxf step stp iges igs sldprt sldasm ipt f3d catpart fcstd scad rvt ifc 3dm gcode skp",
 "gis": "shp shx prj gpkg kml kmz gpx osm pbf mbtiles topojson geojson",
 "cert": "pem crt cer p12 pfx jks keystore der csr sig ppk gpg asc",
 "net": "ovpn wg pcap pcapng evtx etl",
 "game": "unity prefab uasset umap pak tscn tres vpk wad nbt tmx ldtk aseprite",
 "misc": "torrent lnk url desktop tmp swp pid dat",
}
FAMILY = {"lang": "code", "shell": "terminal", "web": "code", "data": "config", "db": "database", "ml": "neural",
          "text": "document", "docs": "document", "sheet": "spreadsheet", "slides": "presentation", "book": "book",
          "mail": "mail", "img": "image", "design": "image", "audio": "audio", "video": "video",
          "archive": "archive", "disk": "disc", "pkg": "package", "exec": "binary", "font": "font", "3d": "3d",
          "cad": "cad", "gis": "map-pin", "cert": "secret-key", "net": "network", "game": "game", "misc": "empty"}

# Mehrdeutige Endungen: plain-Name = häufigste Bedeutung (oder generisch), Varianten mit Suffix
# name: (Label | None, Kategorie, Glyphe | None, Beschreibung)
VARIANTS = {
 "ts-stream":   ("TS", "video", None, "MPEG Transport Stream"),
 "mts-video":   ("MTS", "video", None, "AVCHD-Video"),
 "v-verilog":   ("VLOG", "lang", None, "Verilog"),
 "v-vlang":     ("V", "lang", None, "V (Programmiersprache)"),
 "v-coq":       ("COQ", "lang", None, "Coq"),
 "m-objc":      ("OBJC", "lang", None, "Objective-C"),
 "m-matlab":    ("MAT", "lang", None, "MATLAB/Octave"),
 "pl-perl":     ("PERL", "lang", None, "Perl"),
 "pl-prolog":   ("PLOG", "lang", None, "Prolog"),
 "obj-object":  ("OBJ", "exec", None, "kompilierte Objektdatei"),
 "key-keynote": ("KEY", "slides", None, "Apple Keynote"),
 "key-private": (None, "cert", "key", "privater Schlüssel"),
 "pub-key":     (None, "cert", "key", "öffentlicher Schlüssel"),
 "db-sqlite":   ("SQLT", "db", None, "SQLite"),
 "db-thumbs":   ("THUMB", "db", None, "Windows Thumbs.db"),
 "db-bdb":      ("BDB", "db", None, "Berkeley DB"),
 "db-paradox":  ("PDOX", "db", None, "Paradox"),
 "mdb-lmdb":    ("LMDB", "db", None, "LMDB"),
 "dbf-oracle":  ("ORA", "db", None, "Oracle-Datendatei"),
 "pb-protobuf": ("PB", "lang", None, "Protocol Buffers (binär)"),
 "pb-tf":       ("TFPB", "ml", None, "TensorFlow-Graph"),
 "img-disk":    ("IMG", "disk", None, "Disk-Image"),
 "vhd-vhdl":    ("VHDL", "lang", None, "VHDL-Quelltext"),
}
# Generische plain-Icons ohne dominante Bedeutung: name -> (Label | None, Kategorie, Glyphe | None)
PLAIN_GENERIC = {
 "v": ("V", "lang", None), "m": ("M", "lang", None), "pl": ("PL", "lang", None), "pb": ("PB", "ml", None),
 "db": (None, "db", "database"), "key": (None, "cert", "key"),
}
AMBIGUOUS = {  # plain-Name -> Varianten
 "ts": ["ts-stream"], "mts": ["mts-video"], "v": ["v-verilog", "v-vlang", "v-coq"], "m": ["m-objc", "m-matlab"],
 "pl": ["pl-perl", "pl-prolog"], "obj": ["obj-object"], "key": ["key-keynote", "key-private"], "pub": ["pub-key"],
 "db": ["db-sqlite", "db-thumbs", "db-bdb", "db-paradox"], "mdb": ["mdb-lmdb"], "dbf": ["dbf-oracle"],
 "pb": ["pb-protobuf", "pb-tf"], "img": ["img-disk"], "vhd": ["vhd-vhdl"],
}

# ---------------------------------------------------------------- Glyphen
# Koordinaten um (0,0), ca. 10x10 Einheiten, werden mit Strichfarbe gezeichnet
GLYPHS_SVG = {
 "code": '<path d="M-2.5-3-5.5 0l3 3M2.5-3l3 3-3 3M1-4.5-1 4.5"/>',
 "document": '<path d="M-4-3.5h8M-4-1h8M-4 1.5h8M-4 4h4.5"/>',
 "audio": '<path d="M-1.5 3.4v-7.6l6-1.6v7.4"/><circle cx="-3" cy="3.4" r="1.5"/><circle cx="3" cy="1.8" r="1.5"/>',
 "image": '<path d="M-5.2 4.5 -1.2-1l2.6 3.4 1.6-1.9 3.2 3.5z"/><circle cx="3.2" cy="-3" r="1.2"/>',
 "video": '<rect x="-4.5" y="-4.5" width="9" height="9" rx="1.5"/><path d="M-1.5-4.5v9M1.5-4.5v9M-4.5-1.5h3M-4.5 1.5h3M1.5-1.5h3M1.5 1.5h3"/>',
 "video-play": '<circle r="4.6"/><path d="M-1.2-2.1 2.4 0l-3.6 2.1z"/>',
 "spreadsheet": '<rect x="-5" y="-3.8" width="10" height="7.6" rx="1.6"/><path d="M-5-0.8h10M-1.6-0.8v4.6"/>',
 "folder": '<path d="M-5-2.4a1.2 1.2 0 0 1 1.2-1.2h2.5L0-2h3.8A1.2 1.2 0 0 1 5-0.8v4A1.2 1.2 0 0 1 3.8 4.4h-7.6A1.2 1.2 0 0 1-5 3.2z"/>',
 "archive": '<path d="M0-5v2M0-1.6v2"/><rect x="-1.6" y="1" width="3.2" height="3.8" rx="1"/>',
 "database": '<ellipse cy="-3" rx="4.5" ry="1.8"/><path d="M-4.5-3v6M4.5-3v6M-4.5 0a4.5 1.8 0 0 0 9 0M-4.5 3a4.5 1.8 0 0 0 9 0"/>',
 "config": '<path d="M-5-3h2.6M0.4-3H5M-5 0h6.6M4.6 0H5M-5 3h1.4M-0.6 3H5"/><circle cx="-1.2" cy="-3" r="1.2"/><circle cx="3.1" cy="0" r="1.2"/><circle cx="-2.1" cy="3" r="1.2"/>',
 "terminal": '<path d="M-4.5-2.8 -1 0l-3.5 2.8M0.8 3.4H5"/>',
 "font": '<path d="M-5 4.2 -2.2-4 0.6 4.2M-4-1.1h3.6"/><circle cx="3.4" cy="2.2" r="1.9"/><path d="M5.3 0.3v3.9"/>',
 "key": '<circle cx="-2" cy="-1.6" r="2.6"/><path d="M-0.2 0.2 4.8 5.2M2.6 3 4.2 1.4"/>',
 "3d": '<path d="M0-5 4.5-2.5v5L0 5l-4.5-2.5v-5zM-4.5-2.5 0 0l4.5-2.5M0 0v5"/>',
 "binary": '<rect x="-3.4" y="-3.4" width="6.8" height="6.8" rx="1.2"/><path d="M-1.5-5.4v2M1.5-5.4v2M-1.5 3.4v2M1.5 3.4v2M-5.4-1.5h2M-5.4 1.5h2M3.4-1.5h2M3.4 1.5h2"/>',
 "mail": '<rect x="-5" y="-3.5" width="10" height="7" rx="1.5"/><path d="M-5-2 0 1.5 5-2"/>',
 "package": '<path d="M-4.5-1.5h9v6h-9zM-5.5-4.5h11v3h-11zM-1.5 1h3"/>',
 "disc": '<circle r="4.8"/><circle r="1.2"/>',
 "map-pin": '<path d="M0 5.2C-3 1.8-4.2 0-4.2-2a4.2 4.2 0 0 1 8.4 0c0 2-1.2 3.8-4.2 7.2z"/><circle cy="-2" r="1.3"/>',
 "cad": '<path d="M-4.5 4.5v-9l9 9z"/><path d="M-4.5 1h2M-4.5-1.5h1M-1.5 4.5v-2M1.5 4.5v-1"/>',
 "book": '<path d="M-5-3.5C-3.5-4.5-1.5-4.5 0-3.5 1.5-4.5 3.5-4.5 5-3.5v8c-1.5-1-3.5-1-5 0-1.5-1-3.5-1-5 0zM0-3.5v8"/>',
 "presentation": '<rect x="-5" y="-4" width="10" height="7" rx="1"/><path d="M0 3v2.5M-2.5 5.5h5M-2.5 0.5l1.5-1.5 1.2 1 1.8-2"/>',
 "network": '<circle cx="0" cy="-3.5" r="1.4"/><circle cx="-3.8" cy="3" r="1.4"/><circle cx="3.8" cy="3" r="1.4"/><path d="M-0.8-2.3-3 1.8M0.8-2.3 3 1.8M-2.4 3h4.8"/>',
 "neural": '<circle cx="-3.8" cy="-2.5" r="1.1"/><circle cx="-3.8" cy="2.5" r="1.1"/><circle cx="0" cy="0" r="1.1"/><circle cx="3.8" cy="-2.5" r="1.1"/><circle cx="3.8" cy="2.5" r="1.1"/><path d="M-2.8-2.1-1-0.7M-2.8 2.1-1 0.7M1-0.7 2.8-2.1M1 0.7 2.8 2.1"/>',
 "game": '<path d="M-3-3h6a3.5 3.5 0 0 1 3.4 4.2l-.6 2.6a1.6 1.6 0 0 1-2.8.5L2 2.5h-4L-3 4.3a1.6 1.6 0 0 1-2.8-.5l-.6-2.6A3.5 3.5 0 0 1-3-3z"/><path d="M-3-0.2v2M-4 0.8h2"/>',
}
GENERIC = {  # Name -> (Glyph, Farbe) – Familien-Icons ohne Label
 "audio": ("audio", "#DD2590"), "code": ("code", "#444CE7"), "document": ("document", "#1570EF"),
 "empty": (None, None), "folder": ("folder", "#7F56D9"), "image": ("image", "#7F56D9"),
 "spreadsheet": ("spreadsheet", "#079455"), "video": ("video", "#444CE7"),
 "video-play": ("video-play", "#444CE7"), "archive": ("archive", "#B54708"),
 "database": ("database", "#079455"), "config": ("config", "#0E9384"),
 "terminal": ("terminal", "#475467"), "font": ("font", "#6172F3"), "secret-key": ("key", "#DC6803"),
 "3d": ("3d", "#0BA5EC"), "binary": ("binary", "#475467"), "mail": ("mail", "#1570EF"),
 "package": ("package", "#B54708"), "disc": ("disc", "#667085"), "map-pin": ("map-pin", "#12B76A"),
 "cad": ("cad", "#0086C9"), "book": ("book", "#B54708"), "presentation": ("presentation", "#E04F16"),
 "network": ("network", "#444CE7"), "neural": ("neural", "#7A5AF8"), "game": ("game", "#7F56D9"),
}

# ---------------------------------------------------------------- Geometrie (40x40)
VB = 40
X0, X1, Y0, Y1 = 4.75, 35.25, 0.75, 39.25   # Seite
R, FX, FY, FR = 3.25, 24.0, 12.0, 4.0        # Ecken-Radius, Eselsohr (x, y, Rundung)
SW = 1.5                                      # Strichstärke
LABEL_H, LABEL_R, LABEL_CY, LABEL_X, LABEL_PAD = 12.5, 2.5, 26.0, 0.75, 4.0
GLYPH_SCALE, GLYPH_CY = 1.3, 24.2
CX = (X0 + X1) / 2

def page_path():
    return (f"M{X0+R} {Y0}H{FX}L{X1} {FY}V{Y1-R}A{R} {R} 0 0 1 {X1-R} {Y1}H{X0+R}"
            f"A{R} {R} 0 0 1 {X0} {Y1-R}V{Y0+R}A{R} {R} 0 0 1 {X0+R} {Y0}Z")

def fold_stroke():
    return f"M{FX} {Y0-0.25}V{FY-FR}a{FR} {FR} 0 0 0 {FR} {FR}h{X1-FX-FR+0.25}"

def fold_fill():
    return f"M{FX} {Y0}V{FY-FR}a{FR} {FR} 0 0 0 {FR} {FR}H{X1}Z"

def page_svg(style, theme):
    if style == "default":
        return (f'<path d="{page_path()}" fill="{PAGE_FILL[theme]}" stroke="{OUTLINE[theme]}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="{fold_stroke()}" stroke="{OUTLINE[theme]}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round"/>')
    if style == "gray":
        g = GRAY[theme]
        return f'<path d="{page_path()}" fill="{g["page"]}"/><path d="{fold_fill()}" fill="{g["fold"]}"/>'
    return None  # solid braucht die Farbe -> in make()

def _num(v):
    t = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t

def text_path(txt, fs):
    scale = fs / UPM
    x, parts = 0.0, []
    for ch in txt:
        gn = CMAP[ord(ch)]
        pen = SVGPathPen(GLYPHS, ntos=_num)
        GLYPHS[gn].draw(TransformPen(pen, (scale, 0, 0, -scale, x * scale, 0)))
        parts.append(pen.getCommands())
        x += HMTX[gn][0]
    return " ".join(parts), x * scale

def fs_for(n, boxed):
    if boxed:
        return 8.2 if n <= 3 else 7.4 if n == 4 else 6.6
    return 7.4 if n <= 3 else 6.8 if n == 4 else 5.8

def svg_wrap(body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{VB}" height="{VB}" viewBox="0 0 {VB} {VB}" fill="none">'
            f'<title>{title}</title>{body}</svg>\n')

def ink_for(style, theme, color):
    return color if style == "default" else GRAY[theme]["ink"] if style == "gray" else SOLID_INK

def make(name, glyph, text, color, style, theme):
    """glyph: Schlüssel aus GLYPHS_SVG oder None; text: Label-Text oder None"""
    if style == "solid":
        fc, fo = SOLID_FOLD
        body = (f'<path d="{page_path()}" fill="{color}"/>'
                f'<path d="{fold_fill()}" fill="{fc}" fill-opacity="{fo}"/>')
    else:
        body = page_svg(style, theme)
    ink = ink_for(style, theme, color)
    if glyph:
        body += (f'<g transform="translate({CX} {GLYPH_CY}) scale({GLYPH_SCALE})" stroke="{ink}" '
                 f'stroke-width="{1.5/GLYPH_SCALE:.3f}" stroke-linecap="round" stroke-linejoin="round" fill="none">'
                 f'{GLYPHS_SVG[glyph]}</g>')
    if text:
        text = text[:5]
        boxed = style == "default"
        fs = fs_for(len(text), boxed)
        d, tw = text_path(text, fs)
        cap = CAP / UPM * fs
        if boxed:
            w = round(tw + 2 * LABEL_PAD, 2)
            body += (f'<rect x="{LABEL_X}" y="{LABEL_CY-LABEL_H/2}" width="{w}" height="{LABEL_H}" rx="{LABEL_R}" fill="{color}"/>'
                     f'<path transform="translate({LABEL_X+(w-tw)/2:.2f} {LABEL_CY+cap/2:.2f})" d="{d}" fill="#fff"/>')
        else:
            body += f'<path transform="translate({CX-tw/2:.2f} {27.0+cap/2:.2f})" d="{d}" fill="{ink}"/>'
    return svg_wrap(body, name)

# ---------------------------------------------------------------- Lauf
JOBS = [("default", "dark"), ("default", "light"), ("gray", "dark"), ("gray", "light"), ("solid", "dark")]

def write(style, theme, name, svg):
    folder = os.path.join(OUT, style, theme) if style != "solid" else os.path.join(OUT, "solid")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, f"{name}.svg"), "w").write(svg)

def emit(name, glyph, label, color):
    for style, theme in JOBS:
        write(style, theme, name, make(name, glyph, label, color, style, theme))

def main():
    manifest, seen = {}, set()
    for name, (glyph, color) in GENERIC.items():
        color = color or "#7F56D9"
        emit(name, glyph, None, color)
        manifest[name] = {"type": "generic", "color": color}
    for name, (label, cat, glyph) in PLAIN_GENERIC.items():
        color = CAT_COLOR[cat]
        emit(name, glyph, label, color)
        manifest[name] = {"type": "generic-ext", "category": cat, "label": label, "color": color,
                          "family": FAMILY[cat], "ambiguous": AMBIGUOUS[name]}
        seen.add(name)
    for cat, exts in EXTENSIONS.items():
        for ext in exts.split():
            if ext in seen or ext in GENERIC:
                continue
            seen.add(ext)
            color = EXT_COLOR.get(ext, CAT_COLOR[cat])
            label = LABEL.get(ext, ext.upper())[:5]
            emit(ext, None, label, color)
            manifest[ext] = {"type": "ext", "category": cat, "label": label, "color": color, "family": FAMILY[cat]}
            if ext in AMBIGUOUS:
                manifest[ext]["ambiguous"] = AMBIGUOUS[ext]
    for name, (label, cat, glyph, desc) in VARIANTS.items():
        base = name.split("-")[0]
        color = EXT_COLOR.get(label.lower() if label else "", CAT_COLOR[cat]) if name == "db-sqlite" else CAT_COLOR[cat]
        if name == "db-sqlite":
            color = EXT_COLOR["sqlite"]
        emit(name, glyph, label, color)
        manifest[name] = {"type": "variant", "of": base, "category": cat, "label": label, "color": color,
                          "family": FAMILY[cat], "meaning": desc}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{len(manifest)} Icons x 5 Dateien -> {OUT}/")

if __name__ == "__main__":
    main()
