// Copies the stylesheets the codegen wrote to src/generated/ into dist/ (run `pnpm codegen` first).
import { copyFileSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const root = join(import.meta.dirname, "..");
const source = join(root, "src", "generated");
const dist = join(root, "dist");

const files = readdirSync(source).filter((file) => file.endsWith(".css"));
if (files.length === 0) throw new Error("No stylesheets in src/generated – run `pnpm codegen` first.");

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });
for (const file of files) copyFileSync(join(source, file), join(dist, file));
console.log(`css: ${files.length} stylesheets -> dist/`);
