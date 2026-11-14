import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";

export const stats = { written: 0, unchanged: 0, removed: 0 };

/** Writes only when the content changed (keeps the codegen idempotent and incremental builds fast). */
export function writeIfChanged(file: string, content: string | Buffer): void {
  if (existsSync(file)) {
    const current = readFileSync(file);
    const next = typeof content === "string" ? Buffer.from(content) : content;
    if (current.equals(next)) {
      stats.unchanged++;
      return;
    }
  }
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, content);
  stats.written++;
}

export function listFiles(dir: string): string[] {
  if (!existsSync(dir)) return [];
  const out: string[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...listFiles(full));
    else out.push(full);
  }
  return out;
}

/** Writes `files` below `dir` and removes every other file in `dir` (for fully generated directories). */
export function syncDirectory(dir: string, files: Record<string, string | Buffer>): void {
  const wanted = new Set(Object.keys(files).map((file) => join(dir, file)));
  for (const existing of listFiles(dir)) {
    if (!wanted.has(existing)) {
      rmSync(existing);
      stats.removed++;
    }
  }
  for (const [file, content] of Object.entries(files)) writeIfChanged(join(dir, file), content);
}

export const toPosix = (path: string): string => path.split("\\").join("/");
export const rel = (from: string, to: string): string => toPosix(relative(from, to));
