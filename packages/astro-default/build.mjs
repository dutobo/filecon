// Astro components ship as source: compile the TypeScript helpers with tsc, copy the .astro files next to them.
import { execSync } from "node:child_process";
import { cpSync, rmSync, statSync } from "node:fs";

rmSync("dist", { recursive: true, force: true });
execSync("tsc -p tsconfig.build.json", { stdio: "inherit" });
cpSync("src", "dist", {
  recursive: true,
  filter: (source) => statSync(source).isDirectory() || source.endsWith(".astro"),
});
