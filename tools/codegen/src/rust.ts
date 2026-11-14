// Rust crate assets (phase 3). Generates nothing while crates/filecon does not exist.
import { existsSync } from "node:fs";
import { join } from "node:path";
import { CRATE_DIR } from "./config";
import type { Pack } from "./pack";

export function generateCrate(_pack: Pack): void {
  if (!existsSync(join(CRATE_DIR, "Cargo.toml"))) return;
}
