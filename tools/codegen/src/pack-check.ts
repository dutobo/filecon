// Acceptance criterion 4: every publishable package can be packed with `pnpm pack`, and the tarball
// contains LICENSE, NOTICE, README.md and dist/ – but no sources or tests. Never publishes anything.
import { execSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { gunzipSync } from "node:zlib";
import { PACKAGES_DIR } from "./config";

interface TarEntry {
  path: string;
  content: Buffer;
}

/** Minimal ustar reader (enough for npm tarballs). */
export function readTarball(file: string): TarEntry[] {
  const data = gunzipSync(readFileSync(file));
  const entries: TarEntry[] = [];
  let offset = 0;
  while (offset + 512 <= data.length) {
    const header = data.subarray(offset, offset + 512);
    if (header.every((byte) => byte === 0)) break;
    const field = (start: number, length: number) =>
      header
        .subarray(start, start + length)
        .toString("utf8")
        .replace(/\0.*$/s, "");
    const name = field(0, 100);
    const prefix = field(345, 155);
    const size = Number.parseInt(field(124, 12).trim() || "0", 8);
    const type = field(156, 1);
    const path = prefix ? `${prefix}/${name}` : name;
    const content = data.subarray(offset + 512, offset + 512 + size);
    if (type === "0" || type === "") entries.push({ path: path.replace(/^package\//, ""), content });
    offset += 512 + Math.ceil(size / 512) * 512;
  }
  return entries;
}

const SOURCE_FILE = /(^|\/)(src|test|tests|__tests__)\//;
const TS_SOURCE = /\.(ts|tsx|mts|cts)$/;
const DECLARATION = /\.d\.(ts|mts|cts)$/;
const CONFIG_FILE = /(^|\/)(tsconfig[^/]*\.json|[^/]*\.config\.(ts|js|mjs|cjs)|vitest[^/]*|biome\.json)$/;

export function checkTarball(entries: TarEntry[]): string[] {
  const problems: string[] = [];
  const paths = entries.map((entry) => entry.path);
  for (const required of ["LICENSE", "NOTICE", "README.md", "package.json"]) {
    if (!paths.includes(required)) problems.push(`missing ${required}`);
  }
  if (!paths.some((path) => path.startsWith("dist/"))) problems.push("missing dist/");
  for (const path of paths) {
    if (SOURCE_FILE.test(path)) problems.push(`source/test file: ${path}`);
    else if (TS_SOURCE.test(path) && !DECLARATION.test(path)) problems.push(`TypeScript source: ${path}`);
    else if (CONFIG_FILE.test(path)) problems.push(`config file: ${path}`);
  }
  const manifest = entries.find((entry) => entry.path === "package.json")?.content.toString("utf8") ?? "";
  if (manifest.includes("workspace:")) problems.push("package.json still contains workspace: ranges");
  if (manifest.includes("@filecon/source")) problems.push("package.json still contains the dev-only source condition");
  return problems;
}

function publishablePackages(): string[] {
  return readdirSync(PACKAGES_DIR)
    .filter((dir) => {
      try {
        const pkg = JSON.parse(readFileSync(join(PACKAGES_DIR, dir, "package.json"), "utf8")) as { private?: boolean };
        return !pkg.private;
      } catch {
        return false;
      }
    })
    .sort();
}

function main(): void {
  const only = process.argv.slice(2);
  const destination = mkdtempSync(join(tmpdir(), "filecon-pack-"));
  const rows: string[] = [];
  let failed = 0;
  try {
    for (const dir of publishablePackages().filter((name) => only.length === 0 || only.includes(name))) {
      const before = new Set(readdirSync(destination));
      execSync(`pnpm pack --pack-destination "${destination}"`, { cwd: join(PACKAGES_DIR, dir), stdio: "pipe" });
      const tarball = readdirSync(destination).find((file) => !before.has(file) && file.endsWith(".tgz"));
      if (!tarball) throw new Error(`pnpm pack produced no tarball for ${dir}`);
      const entries = readTarball(join(destination, tarball));
      const problems = checkTarball(entries);
      if (problems.length > 0) failed++;
      rows.push(
        `${problems.length === 0 ? "ok  " : "FAIL"} ${dir.padEnd(16)} ${String(entries.length).padStart(5)} files`,
      );
      for (const problem of problems.slice(0, 10)) rows.push(`       - ${problem}`);
    }
  } finally {
    rmSync(destination, { recursive: true, force: true });
  }
  console.log(rows.join("\n"));
  if (failed > 0) {
    console.error(`\n${failed} package(s) failed the tarball check.`);
    process.exit(1);
  }
}

if (process.argv[1]?.endsWith("pack-check.ts")) main();
