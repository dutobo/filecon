# Filecon – Icon-Pack (Quelle der Wahrheit für alle Pakete)

703 Datei-Icons, je 3 Stile. 40×40 px, skalierbar, Label-Text ist als Pfad eingebettet (keine Schrift nötig).

## Ordner
| Pfad | Inhalt |
|---|---|
| `default/dark/`, `default/light/` | Umriss, farbiges Label bzw. farbige Glyphe |
| `gray/dark/`, `gray/light/` | gefüllte graue Seite, graue Schrift/Glyphe |
| `solid/` | gefüllte Farbseite, weiße Schrift/Glyphe (Dark = Light, daher nur ein Ordner) |
| `manifest.json` | alle 703 Icons: `type`, `category`, `label`, `color`, `family`, bei Varianten `of`/`meaning`, bei mehrdeutigen Endungen `ambiguous` |
| `resolve_icon.py` | wählt das Icon für eine Datei (Name → Magic-Bytes → Endung → Familie → `empty`) |
| `tests/resolve-cases.json` | 20 Testfälle für den Resolver (Spezifikation für Ports nach JS/Rust) |
| `generate_file_icons.py` | erzeugt alle SVGs neu (`python3 generate_file_icons.py ausgabe/`, braucht `fonttools` + Inter Bold) |
| `preview.html` | Galerie mit Suche, Stil- und Theme-Umschalter |

Jedes Icon existiert in allen 5 Ordnern unter demselben Namen: `<name>.svg`.

## Icon-Arten (`manifest[name].type`)
- `ext` (647): ein Icon je Endung, z. B. `pdf`, `rs`, `parquet`.
- `generic` (27): Familien-Icons ohne Label, z. B. `database`, `archive`, `3d`, `cad`, `map-pin`, `neural`,
  `package`, `disc`, `mail`, `book`, `presentation`, `network`, `game`, `secret-key`, `binary`, `config`, `empty`.
  Fallback über `manifest[ext].family`; ganz am Ende `empty`.
- `generic-ext` (6): mehrdeutige Endungen ohne dominante Bedeutung: `db`, `key`, `v`, `m`, `pl`, `pb`.
- `variant` (23): spezifische Varianten mit Suffix, z. B. `ts-stream`, `db-sqlite`, `db-thumbs`, `m-objc`,
  `m-matlab`, `v-verilog`, `pl-perl`, `key-private`, `obj-object`, `mdb-lmdb`, `img-disk`, `vhd-vhdl`.
  Die Varianten einer Endung stehen in `manifest[plain].ambiguous`.

Dominante Bedeutung = Plain-Name (z. B. `ts` = TypeScript, `obj` = 3D-Modell, `mdb` = Access).

## Auflösung
`resolve_icon.py` (Referenzimplementierung): Dateiname (z. B. `Thumbs.db`, `Dockerfile`) → Magic-Bytes/Inhalt
(erste 1 KB, z. B. `SQLite format 3` → `db-sqlite`) → Endung → `family` → `empty`.
Ohne Dateiinhalt arbeitet der Resolver nur mit Namen und Endung.

## Hinweise
- Die SVGs wurden mit gerundeten Zahlen erzeugt (ca. 4 MB gesamt); weitere Optimierung nur verlustfrei.
- Farben: `default`-Stil nutzt die Marken-/Kategoriefarben aus `manifest.json`; Umrissfarben dark `#3F3F46`, light `#D5D7DA`.
- Keine Logos enthalten.

Lizenz: Apache License 2.0 (`LICENSE`, `NOTICE`). Bei Weitergabe beide Dateien mitgeben und Änderungen kenntlich machen.
