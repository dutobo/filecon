// Builds dist/ from the icon sets the codegen wrote to src/generated/ (run `pnpm codegen` first).
// Per set: <id>.json (raw Iconify JSON), <id>.js / <id>.cjs (thin wrappers that load the JSON).
import { copyFileSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const root = join(import.meta.dirname, "..");
const source = join(root, "src", "generated");
const dist = join(root, "dist");

const ids = readdirSync(source)
  .filter((file) => file.endsWith(".json"))
  .map((file) => file.slice(0, -".json".length))
  .sort();
if (ids.length === 0) throw new Error("No icon sets in src/generated – run `pnpm codegen` first.");

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

const types = `/** Iconify JSON icon set (subset of \`IconifyJSON\` from \`@iconify/types\`). */
export interface IconifyJSON {
  prefix: string;
  info?: Record<string, unknown>;
  icons: Record<string, { body: string; width?: number; height?: number }>;
  categories?: Record<string, string[]>;
  width?: number;
  height?: number;
}
`;
writeFileSync(join(dist, "types.d.ts"), types);
writeFileSync(join(dist, "types.d.cts"), types);
writeFileSync(
  join(dist, "set.d.ts"),
  'import type { IconifyJSON } from "./types.js";\n\ndeclare const set: IconifyJSON;\nexport default set;\n',
);
writeFileSync(
  join(dist, "set.d.cts"),
  'import type { IconifyJSON } from "./types.cjs";\n\ndeclare const set: IconifyJSON;\nexport = set;\n',
);

for (const id of ids) {
  copyFileSync(join(source, `${id}.json`), join(dist, `${id}.json`));
  writeFileSync(
    join(dist, `${id}.js`),
    `import set from "./${id}.json" with { type: "json" };\n\nexport default set;\n`,
  );
  writeFileSync(join(dist, `${id}.cjs`), `"use strict";\n\nmodule.exports = require("./${id}.json");\n`);
}

const list = JSON.stringify(ids);
const loaders = (load) => ids.map((id) => `  ${JSON.stringify(id)}: () => ${load(id)},`).join("\n");
writeFileSync(
  join(dist, "index.js"),
  `/** Prefixes of all Filecon icon sets. */
export const prefixes = ${list};

/** Lazy loaders per prefix, e.g. for UnoCSS \`presetIcons({ collections })\`. */
export const collections = {
${loaders((id) => `import("./${id}.js").then((module) => module.default)`)}
};
`,
);
writeFileSync(
  join(dist, "index.cjs"),
  `"use strict";

exports.prefixes = ${list};
exports.collections = {
${loaders((id) => `Promise.resolve(require("./${id}.json"))`)}
};
`,
);
const indexTypes = (from) => `import type { IconifyJSON } from "${from}";

export type { IconifyJSON };
/** Prefix of a Filecon icon set. */
export type FileconPrefix = ${ids.map((id) => JSON.stringify(id)).join(" | ")};
/** Prefixes of all Filecon icon sets. */
export declare const prefixes: readonly FileconPrefix[];
/** Lazy loaders per prefix, e.g. for UnoCSS \`presetIcons({ collections })\`. */
export declare const collections: Record<FileconPrefix, () => Promise<IconifyJSON>>;
`;
writeFileSync(join(dist, "index.d.ts"), indexTypes("./types.js"));
writeFileSync(join(dist, "index.d.cts"), indexTypes("./types.cjs"));
console.log(`iconify: ${ids.length} sets -> dist/`);
