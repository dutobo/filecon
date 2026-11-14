# Issues

Problems and open questions found while building the packages. The icon pack (`icon-pack/`) is the single source
of truth and is **never modified** here – pack issues are only recorded.

## Open TODOs

- [ ] **Repository URL is a placeholder.** All `package.json` files, the crate and the docs point to
  `https://github.com/dutobo/filecon`. Change `REPOSITORY` in `tools/codegen/src/config.ts` (and `crates/filecon/Cargo.toml`)
  once the final location is known, then run `pnpm codegen`.

## Icon pack

1. **Pack was delivered unpacked, not as `filecon-icon-pack.zip`.** The files were moved unchanged into `icon-pack/`
   (byte-identical, `.gitattributes` marks the folder `-text` so Git never touches line endings).
2. **README vs. resolver: family fallback.** `icon-pack/README.md` describes the chain
   "name → magic bytes → extension → `family` → `empty`", but `resolve_icon.py` never uses `family`
   (an extension that is in the manifest resolves to itself; unknown extensions go straight to `empty`).
   The TypeScript and Rust ports follow the reference implementation and its 20 test cases.
3. **Variants the resolver can never pick.** `db-paradox`, `pb-protobuf`, `pb-tf` and `dbf-oracle` are listed in
   `ambiguous` but `resolve_icon.py` has no sniffing rule for them (only reachable by name).
4. **Visually identical icons.** In every style these groups render the same SVG (only `<title>` differs):
   `secret-key` = `key` = `key-private` = `pub-key`, `v` = `v-vlang`, `vhdl` = `vhd-vhdl`, `graphql` = `gql`,
   `sqlite` = `sqlite3` = `db-sqlite`, `pkl` = `pickle`. Most are intended aliases; questionable are
   `key-private`/`pub-key` (the resolver distinguishes them, the icons do not) and `v` = `v-vlang`
   (the "ambiguous" `v` icon carries the V-language look, so the neutral fallback is not neutral).
5. **Non-generic icons without `label`.** `db`, `key` (type `generic-ext`) and `key-private`, `pub-key`
   (type `variant`) have no `label` in the manifest, unlike the other variants.
6. **Name-only `Thumbs.db`.** `resolve_icon.py` only recognizes `Thumbs.db` inside the content sniffing step, so
   `resolveIcon("Thumbs.db")` without content returns `db` (ported as-is).
7. **Empty content for `.img`.** With content given but empty (`head = []`), `x.img` resolves to `img-disk`
   because the "not PNG/JPEG/GIF/RIFF" rule matches (ported as-is; without `head` it is `img`).

## Tooling / environment

- **Node version.** Published packages declare `"node": ">=20"`. The development tooling (vitest 5, tsup 9,
  Angular 22, Astro 7) needs Node ≥ 22.18, so the workspace root requires that and CI runs Node 22 and 24.
- **File system.** pnpm workspaces need symlinks/junctions. The repository cannot live on exFAT/FAT drives
  (that is why it moved from `H:\filecon` to `C:\filecon`).
