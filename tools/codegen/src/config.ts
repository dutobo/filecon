import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Style } from "../../../packages/shared/src/types";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
export const PACK_DIR = join(ROOT, "icon-pack");
export const PACKAGES_DIR = join(ROOT, "packages");
export const TEMPLATES_DIR = join(ROOT, "tools", "templates");
export const CRATE_DIR = join(ROOT, "crates", "filecon");

export const SCOPE = "@filecon";
export const INITIAL_VERSION = "0.1.0";
export const HOMEPAGE = "https://filecon.dev";
/** TODO(ISSUES.md): placeholder until the final repository location is known. */
export const REPOSITORY = "https://github.com/dutobo/filecon";
export const AUTHOR = { name: "dutobo", url: "https://github.com/dutobo" } as const;
export const CONTRIBUTORS = [{ name: "rafaelk-f", url: "https://github.com/rafaelk-f" }] as const;
export const NODE_ENGINE = ">=20";

export const STYLES: readonly Style[] = ["default", "gray", "solid"];
export type Variant = "all" | Style;
export const VARIANTS: readonly Variant[] = ["all", "default", "gray", "solid"];

/** Versions of third-party dependencies used by the generated packages (single place to bump). */
export const VERSIONS = {
  typescript: "~6.0.3",
  tsup: "^9.0.0",
  vitest: "^5.1.0",
  nodeTypes: "^24.19.2",
} as const;
