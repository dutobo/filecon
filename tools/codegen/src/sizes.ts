// Size report (docs/sizes.md): tarball size, gzip size of the shipped ESM code, and real-world bundle costs
// (minified + gzip) for importing one icon vs. the full `FileIcon`. Run after `pnpm build`.
import { execSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, relative } from "node:path";
import { gzipSync } from "node:zlib";
import { build } from "esbuild";
import { PACKAGES_DIR, ROOT, STYLES } from "./config";
import { listFiles, writeIfChanged } from "./fsutil";

const FRAMEWORK_EXTERNALS = [
  "react",
  "react-dom",
  "react-native",
  "react-native-svg",
  "preact",
  "vue",
  "solid-js",
  "solid-js/web",
  "electron",
  "@angular/*",
  "node:*",
];

const gzip = (data: Buffer | string): number => gzipSync(data, { level: 9 }).length;
const kb = (bytes: number): string =>
  bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(2)} MB` : `${(bytes / 1024).toFixed(1)} kB`;

interface Row {
  name: string;
  tarball: number;
  distGzip: number;
  singleIcon?: number;
  allIcons?: number;
}

/** Entry code for the bundle measurements, or `undefined` for packages compiled by the consumer (Svelte, Astro). */
function bundleEntries(dir: string, name: string): { single: string; all: string } | undefined {
  const fw = dir.replace(new RegExp(`-(${STYLES.join("|")})$`), "");
  if (["svelte", "astro", "shared", "electron", "iconify", "css", "tauri"].includes(fw)) return undefined;
  if (fw === "angular") {
    return {
      single: `import { PdfIcon, FileconIconComponent } from "${name}"; console.log(PdfIcon, FileconIconComponent);`,
      all: `import { FileconIconComponent } from "${name}"; console.log(FileconIconComponent);`,
    };
  }
  if (fw === "elements") {
    return {
      single: `import { PdfIcon } from "${name}/icons"; console.log(PdfIcon);`,
      all: `import { FileconIconElement } from "${name}"; console.log(FileconIconElement);`,
    };
  }
  if (fw === "js") {
    return {
      single: `import { PdfIcon } from "${name}/icons"; console.log(PdfIcon());`,
      all: `import { getIcon } from "${name}"; console.log(getIcon("pdf"));`,
    };
  }
  return {
    single: `import { PdfIcon } from "${name}/icons"; console.log(PdfIcon);`,
    all: `import { FileIcon } from "${name}"; console.log(FileIcon);`,
  };
}

async function bundleSize(cwd: string, code: string): Promise<number> {
  const result = await build({
    stdin: { contents: code, resolveDir: cwd, loader: "js" },
    bundle: true,
    minify: true,
    format: "esm",
    platform: "neutral",
    mainFields: ["module", "main"],
    conditions: ["import", "default"],
    external: FRAMEWORK_EXTERNALS,
    write: false,
    logLevel: "silent",
  });
  return gzip(Buffer.concat(result.outputFiles.map((file) => Buffer.from(file.contents))));
}

function packedSize(dir: string, destination: string): number {
  const before = new Set(readdirSync(destination));
  execSync(`pnpm pack --pack-destination "${destination}"`, { cwd: join(PACKAGES_DIR, dir), stdio: "pipe" });
  const tarball = readdirSync(destination).find((file) => !before.has(file) && file.endsWith(".tgz"));
  return tarball ? statSync(join(destination, tarball)).size : 0;
}

function distGzip(dir: string): number {
  const dist = join(PACKAGES_DIR, dir, "dist");
  const files = listFiles(dist).filter((file) => {
    const path = relative(dist, file).split("\\").join("/");
    if (path.startsWith("svg/") || path.endsWith(".map") || /\.d\.(ts|cts|mts)$/.test(path)) return false;
    if (/\.cjs$/.test(path)) return false; // count the ESM build only
    return /\.(js|mjs|svelte|astro|json)$/.test(path);
  });
  return files.reduce((sum, file) => sum + gzip(readFileSync(file)), 0);
}

/** Upper bound for importing one single icon (catches regressions in tree-shaking). */
const SINGLE_ICON_LIMIT = 16 * 1024;

/** `pnpm sizes --check`: only the bundle measurements, fails if a single icon pulls in the whole icon set. */
async function check(): Promise<void> {
  const failures: string[] = [];
  for (const dir of readdirSync(PACKAGES_DIR).sort()) {
    const pkg = JSON.parse(readFileSync(join(PACKAGES_DIR, dir, "package.json"), "utf8")) as {
      name: string;
      private?: boolean;
    };
    const entries = pkg.private ? undefined : bundleEntries(dir, pkg.name);
    // Angular: the component itself supports `name`/`file`, so it always contains the package's icon map.
    if (!entries || dir.startsWith("angular")) continue;
    const size = await bundleSize(join(PACKAGES_DIR, dir), entries.single);
    console.log(`${pkg.name.padEnd(32)} 1 icon ${kb(size).padStart(9)}`);
    if (size > SINGLE_ICON_LIMIT) failures.push(`${pkg.name}: importing one icon costs ${kb(size)}`);
  }
  if (failures.length > 0) {
    console.error(["", "Tree-shaking regression:", ...failures].join("\n"));
    process.exit(1);
  }
}

async function main(): Promise<void> {
  const destination = mkdtempSync(join(tmpdir(), "filecon-sizes-"));
  const rows: Row[] = [];
  try {
    for (const dir of readdirSync(PACKAGES_DIR).sort()) {
      const pkg = JSON.parse(readFileSync(join(PACKAGES_DIR, dir, "package.json"), "utf8")) as {
        name: string;
        private?: boolean;
      };
      if (pkg.private) continue;
      const row: Row = { name: pkg.name, tarball: packedSize(dir, destination), distGzip: distGzip(dir) };
      const entries = bundleEntries(dir, pkg.name);
      if (entries) {
        const cwd = join(PACKAGES_DIR, dir);
        row.singleIcon = await bundleSize(cwd, entries.single);
        row.allIcons = await bundleSize(cwd, entries.all);
      }
      rows.push(row);
      console.log(
        `${pkg.name.padEnd(32)} tarball ${kb(row.tarball).padStart(9)}  dist ${kb(row.distGzip).padStart(9)}`,
      );
    }
  } finally {
    rmSync(destination, { recursive: true, force: true });
  }

  const crate = join(ROOT, "crates", "filecon", "target", "package");
  const crateFile = (() => {
    try {
      return readdirSync(crate).find((file) => file.endsWith(".crate"));
    } catch {
      return undefined;
    }
  })();

  const lines = [
    "# Package sizes",
    "",
    "Generated by `pnpm sizes` after `pnpm build` (gzip level 9). Columns:",
    "",
    "- **Tarball**: size of the `pnpm pack` tarball (what npm downloads).",
    "- **dist (gzip)**: sum of the gzipped ESM files in `dist/` (CJS builds, maps, `.d.ts` and the SVG copies of",
    "  `@filecon/shared` excluded). Includes the icon data where the package owns it (`@filecon/js*`).",
    '- **1 icon**: minified + gzipped bundle of `import { PdfIcon } from "<pkg>/icons"` including all `@filecon/*`',
    "  dependencies (framework runtime excluded). Shows tree-shaking.",
    "- **All icons**: same for the dynamic `FileIcon` / `getIcon` (contains the data of every icon of the package's",
    "  styles).",
    "",
    "Svelte and Astro ship components that the consumer compiles, so no bundle size is measured for them; the",
    "Angular numbers are for the partially compiled FESM bundle before the Angular linker.",
    "",
    "| Package | Tarball | dist (gzip) | 1 icon | All icons |",
    "|---|---:|---:|---:|---:|",
    ...rows.map(
      (row) =>
        `| \`${row.name}\` | ${kb(row.tarball)} | ${kb(row.distGzip)} | ${row.singleIcon === undefined ? "–" : kb(row.singleIcon)} | ${row.allIcons === undefined ? "–" : kb(row.allIcons)} |`,
    ),
    "",
  ];
  if (crateFile) {
    lines.push(
      "## Rust crate",
      "",
      `| Crate | .crate (compressed) |`,
      "|---|---:|",
      `| \`filecon\` | ${kb(statSync(join(crate, crateFile)).size)} |`,
      "",
    );
  }
  writeIfChanged(join(ROOT, "docs", "sizes.md"), lines.join("\n"));
  console.log("docs/sizes.md written");
}

(process.argv.includes("--check") ? check() : main()).catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
