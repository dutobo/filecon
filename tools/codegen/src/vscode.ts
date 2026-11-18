// VS Code file icon themes (extensions/vscode): SVG copies, three icon theme JSONs, legal files.
// All outputs are gitignored; package.json, README.md, CHANGELOG.md, .vscodeignore and images/ are hand-written.
//
// Mapping (mirrors packages/shared/src/resolve.ts without content sniffing):
// - `fileExtensions`: every `ext` and `generic-ext` icon under its own (lowercase) name.
// - `fileNames`: the resolver's exact-name rules – an extension-less file whose lowercase name is an `ext`/
//   `generic-ext` icon name (e.g. `Dockerfile` -> `dockerfile`), `Makefile` -> `mk` and `Thumbs.db` -> `db-thumbs`.
//   Generic names (`code`, `image`, …) are not mapped as file names: as a bare file name they say nothing about
//   the content.
// - `languageIds`: VS Code language ids -> icon, for files whose extension/name is not mapped but whose language
//   VS Code knows (e.g. `.bashrc` -> shellscript -> `sh`). `plaintext` is deliberately not mapped (it would replace
//   the `empty` fallback for every unknown file).
// - `file` (fallback): `empty`, the resolver's own fallback for unknown files.
// - `folder`/`folderExpanded`/`rootFolder`/`rootFolderExpanded`: the pack's generic `folder` icon.
// - `variant` icons other than `db-thumbs` need content sniffing and are not mapped.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { isThemedStyle, type Style } from "../../../packages/shared/src/types";
import { ROOT, STYLE_TITLES, STYLES } from "./config";
import { syncDirectory, writeIfChanged } from "./fsutil";
import { LEGAL_FILES, legalFile } from "./legal";
import type { Pack } from "./pack";
import { svgPath } from "./pack";

export const VSCODE_DIR = join(ROOT, "extensions", "vscode");

/** Theme id, label and JSON file per style; must match `contributes.iconThemes` in extensions/vscode/package.json. */
export const VSCODE_THEMES = STYLES.map((style) => ({
  id: style === "default" ? "filecon" : `filecon-${style}`,
  label: style === "default" ? "Filecon" : `Filecon ${STYLE_TITLES[style]}`,
  style,
  file: `filecon-${style}.json`,
}));

export const VSCODE_FALLBACK = "empty";

/** Exact file names of the resolver that are not covered by the extension-less name rule. */
const SPECIAL_FILE_NAMES: Readonly<Record<string, string>> = { makefile: "mk", "thumbs.db": "db-thumbs" };

/** VS Code language id -> icon name (curated; every icon must exist in the pack). */
const LANGUAGE_IDS: Readonly<Record<string, string>> = {
  ada: "ada",
  asciidoc: "adoc",
  astro: "astro",
  awk: "awk",
  bat: "bat",
  bazel: "bzl",
  bibtex: "bib",
  c: "c",
  clojure: "clj",
  cmake: "cmake",
  cobol: "cob",
  coffeescript: "coffee",
  cpp: "cpp",
  crystal: "cr",
  csharp: "cs",
  css: "css",
  csv: "csv",
  cue: "cue",
  d: "d",
  dart: "dart",
  diff: "diff",
  dockercompose: "yaml",
  dockerfile: "dockerfile",
  dotenv: "env",
  editorconfig: "editorconfig",
  elixir: "ex",
  elm: "elm",
  erlang: "erl",
  fish: "fish",
  fortran: "f90",
  fsharp: "fs",
  gdscript: "gd",
  gleam: "gleam",
  glsl: "glsl",
  go: "go",
  gradle: "gradle",
  graphql: "graphql",
  groovy: "groovy",
  handlebars: "hbs",
  haskell: "hs",
  hcl: "hcl",
  hlsl: "hlsl",
  html: "html",
  ignore: "gitignore",
  ini: "ini",
  jade: "pug",
  java: "java",
  javascript: "js",
  javascriptreact: "jsx",
  json: "json",
  jsonc: "json",
  jsonl: "jsonl",
  jsonnet: "jsonnet",
  julia: "jl",
  kotlin: "kt",
  latex: "tex",
  less: "less",
  lisp: "lisp",
  log: "log",
  lua: "lua",
  makefile: "mk",
  markdown: "md",
  matlab: "m",
  mdx: "mdx",
  mojo: "mojo",
  nim: "nim",
  ninja: "ninja",
  nix: "nix",
  nushell: "nu",
  "objective-c": "m",
  "objective-cpp": "mm",
  ocaml: "ml",
  odin: "odin",
  pascal: "pas",
  perl: "pl",
  php: "php",
  powershell: "ps1",
  prisma: "prisma",
  properties: "properties",
  proto: "proto",
  proto3: "proto",
  pug: "pug",
  purescript: "purs",
  python: "py",
  r: "r",
  racket: "rkt",
  restructuredtext: "rst",
  ruby: "rb",
  rust: "rs",
  sass: "sass",
  scala: "scala",
  scheme: "scm",
  scss: "scss",
  shellscript: "sh",
  solidity: "sol",
  sql: "sql",
  starlark: "bzl",
  svelte: "svelte",
  swift: "swift",
  systemverilog: "sv",
  tcl: "tcl",
  terraform: "tf",
  tex: "tex",
  toml: "toml",
  tsv: "tsv",
  typescript: "ts",
  typescriptreact: "tsx",
  vb: "vb",
  vhdl: "vhdl",
  vue: "vue",
  wgsl: "wgsl",
  xml: "xml",
  xsl: "xsl",
  yaml: "yaml",
  zig: "zig",
  zsh: "zsh",
};

export const VSCODE_FOLDER = "folder";

export interface VscodeMapping {
  file: string;
  folder: string;
  fileExtensions: Record<string, string>;
  fileNames: Record<string, string>;
  languageIds: Record<string, string>;
}

export function vscodeMapping(pack: Pack): VscodeMapping {
  const fileExtensions: Record<string, string> = {};
  const fileNames: Record<string, string> = {};
  for (const icon of pack.icons) {
    if (icon.meta.type !== "ext" && icon.meta.type !== "generic-ext") continue;
    if (icon.name !== icon.name.toLowerCase() || icon.name.includes(".")) {
      throw new Error(`vscode: unexpected extension icon name "${icon.name}"`);
    }
    fileExtensions[icon.name] = icon.name;
    fileNames[icon.name] = icon.name;
  }
  for (const [fileName, name] of Object.entries(SPECIAL_FILE_NAMES)) {
    if (fileNames[fileName]) throw new Error(`vscode: file name "${fileName}" is already mapped`);
    fileNames[fileName] = name;
  }
  const mapping: VscodeMapping = {
    file: VSCODE_FALLBACK,
    folder: VSCODE_FOLDER,
    fileExtensions,
    fileNames: sortKeys(fileNames),
    languageIds: sortKeys({ ...LANGUAGE_IDS }),
  };
  for (const name of usedIcons(mapping)) {
    if (!pack.manifest[name]) throw new Error(`vscode: mapped icon "${name}" is not in the pack`);
  }
  return mapping;
}

function sortKeys(record: Record<string, string>): Record<string, string> {
  return Object.fromEntries(Object.entries(record).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));
}

const usedIcons = (mapping: VscodeMapping): string[] =>
  [
    ...new Set([
      mapping.file,
      mapping.folder,
      ...Object.values(mapping.fileExtensions),
      ...Object.values(mapping.fileNames),
      ...Object.values(mapping.languageIds),
    ]),
  ].sort();

/** Icon directory below `icons/` for a style and theme. */
const iconDir = (style: Style, theme: "light" | "dark"): string => (isThemedStyle(style) ? `${style}/${theme}` : style);

function associations(mapping: VscodeMapping, suffix: string) {
  const id = (name: string): string => `${name}${suffix}`;
  const remap = (record: Record<string, string>): Record<string, string> =>
    Object.fromEntries(Object.entries(record).map(([key, name]) => [key, id(name)]));
  return {
    file: id(mapping.file),
    folder: id(mapping.folder),
    folderExpanded: id(mapping.folder),
    rootFolder: id(mapping.folder),
    rootFolderExpanded: id(mapping.folder),
    fileExtensions: remap(mapping.fileExtensions),
    fileNames: remap(mapping.fileNames),
    languageIds: remap(mapping.languageIds),
  };
}

function themeJson(style: Style, mapping: VscodeMapping, icons: readonly string[]): string {
  const iconDefinitions: Record<string, { iconPath: string }> = {};
  const define = (theme: "light" | "dark", suffix: string): void => {
    for (const name of icons) {
      iconDefinitions[`${name}${suffix}`] = { iconPath: `../icons/${iconDir(style, theme)}/${name}.svg` };
    }
  };
  // Base definitions (dark SVGs) are used by dark and high-contrast dark color themes.
  define("dark", "");
  const theme: Record<string, unknown> = { iconDefinitions, ...associations(mapping, "") };
  if (isThemedStyle(style)) {
    // Light and high-contrast light color themes use the light SVGs; solid looks the same in both themes.
    define("light", "_light");
    const light = associations(mapping, "_light");
    theme.light = light;
    theme.highContrastLight = light;
  }
  return `${JSON.stringify(theme, null, 2)}\n`;
}

export function generateVscode(pack: Pack): void {
  const packageJsonFile = join(VSCODE_DIR, "package.json");
  if (!existsSync(packageJsonFile)) return;
  const manifest = JSON.parse(readFileSync(packageJsonFile, "utf8")) as {
    contributes?: { iconThemes?: { id: string; label: string; path: string }[] };
  };
  const declared = JSON.stringify(manifest.contributes?.iconThemes ?? []);
  const expected = JSON.stringify(
    VSCODE_THEMES.map(({ id, label, file }) => ({ id, label, path: `./themes/${file}` })),
  );
  if (declared !== expected) {
    throw new Error(`vscode: contributes.iconThemes in ${packageJsonFile} must be ${expected}`);
  }
  const mapping = vscodeMapping(pack);
  const icons = usedIcons(mapping);

  const svgs: Record<string, Buffer> = {};
  for (const { style } of VSCODE_THEMES) {
    for (const theme of isThemedStyle(style) ? (["light", "dark"] as const) : (["light"] as const)) {
      for (const name of icons)
        svgs[`${iconDir(style, theme)}/${name}.svg`] = readFileSync(svgPath(style, theme, name));
    }
  }
  syncDirectory(join(VSCODE_DIR, "icons"), svgs);

  const themes: Record<string, string> = {};
  for (const { style, file } of VSCODE_THEMES) themes[file] = themeJson(style, mapping, icons);
  syncDirectory(join(VSCODE_DIR, "themes"), themes);

  for (const file of LEGAL_FILES) writeIfChanged(join(VSCODE_DIR, file), legalFile(file));
}
