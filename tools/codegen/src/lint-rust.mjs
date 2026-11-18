// `pnpm lint:rust`: rustfmt check + clippy (warnings are errors) for every crate under crates/.
import { execSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

const crates = join(import.meta.dirname, "..", "..", "..", "crates");
for (const name of readdirSync(crates).sort()) {
  const manifest = join(crates, name, "Cargo.toml");
  if (!existsSync(manifest)) continue;
  console.log(`--- ${name}`);
  execSync(`cargo fmt --manifest-path "${manifest}" --check`, { stdio: "inherit" });
  execSync(`cargo clippy --manifest-path "${manifest}" --all-targets --all-features -- -D warnings`, {
    stdio: "inherit",
  });
}
