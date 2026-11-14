import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  AUTHOR,
  CONTRIBUTORS,
  HOMEPAGE,
  INITIAL_VERSION,
  NODE_ENGINE,
  PACKAGES_DIR,
  REPOSITORY,
  VERSIONS,
} from "./config";
import type { PackageJsonParts } from "./template-api";

export const SOURCE_CONDITION = "@filecon/source";

/** Exports map for tsup output (`dist/<entry>.js|.cjs|.d.ts|.d.cts`) plus a dev-only source condition. */
export function tsupExports(entries: readonly string[], sourceExt = "ts"): Record<string, unknown> {
  const map: Record<string, unknown> = {};
  for (const entry of entries) {
    const key = entry === "index" ? "." : `./${entry}`;
    map[key] = {
      [SOURCE_CONDITION]: `./src/${entry}.${sourceExt}`,
      import: { types: `./dist/${entry}.d.ts`, default: `./dist/${entry}.js` },
      require: { types: `./dist/${entry}.d.cts`, default: `./dist/${entry}.cjs` },
    };
  }
  map["./package.json"] = "./package.json";
  return map;
}

/** Removes the dev-only source condition (used for `publishConfig.exports`). */
export function stripSourceCondition(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stripSourceCondition);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, inner] of Object.entries(value)) {
      if (key !== SOURCE_CONDITION) out[key] = stripSourceCondition(inner);
    }
    return out;
  }
  return value;
}

function existingVersion(dirName: string): string {
  const file = join(PACKAGES_DIR, dirName, "package.json");
  if (!existsSync(file)) return INITIAL_VERSION;
  const current = JSON.parse(readFileSync(file, "utf8")) as { version?: string };
  return current.version ?? INITIAL_VERSION;
}

const sorted = (deps: Record<string, string> | undefined): Record<string, string> | undefined =>
  deps && Object.keys(deps).length > 0
    ? Object.fromEntries(Object.entries(deps).sort(([a], [b]) => a.localeCompare(b)))
    : undefined;

export function composePackageJson(name: string, dirName: string, parts: PackageJsonParts): string {
  const exportsMap = parts.exports ?? tsupExports(parts.entries ?? ["index"]);
  const main = (exportsMap["."] as { require?: { default?: string } } | undefined)?.require?.default;
  const module = (exportsMap["."] as { import?: { default?: string } } | undefined)?.import?.default;
  const types = (exportsMap["."] as { import?: { types?: string } } | undefined)?.import?.types;
  const devDependencies = {
    typescript: VERSIONS.typescript,
    ...parts.devDependencies,
  };
  const pkg: Record<string, unknown> = {
    name,
    version: existingVersion(dirName),
    description: parts.description,
    keywords: ["filecon", "file-icons", "icons", "svg", "file-type", ...(parts.keywords ?? [])],
    homepage: HOMEPAGE,
    bugs: { url: `${REPOSITORY}/issues` },
    repository: { type: "git", url: `git+${REPOSITORY}.git`, directory: `packages/${dirName}` },
    license: "Apache-2.0",
    author: AUTHOR,
    contributors: CONTRIBUTORS,
    type: "module",
    sideEffects: false,
    ...(main ? { main } : {}),
    ...(module ? { module } : {}),
    ...(types ? { types } : {}),
    exports: exportsMap,
    ...parts.extra,
    files: ["dist", "NOTICE"],
    engines: { node: NODE_ENGINE },
    scripts: parts.scripts,
    dependencies: sorted(parts.dependencies),
    peerDependencies: sorted(parts.peerDependencies),
    peerDependenciesMeta: parts.peerDependenciesMeta,
    devDependencies: sorted(devDependencies),
    publishConfig: {
      access: "public",
      provenance: true,
      exports: stripSourceCondition(exportsMap),
    },
  };
  return `${JSON.stringify(pkg, (_key, value) => (value === undefined ? undefined : value), 2)}\n`;
}
