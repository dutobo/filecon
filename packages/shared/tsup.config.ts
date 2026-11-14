import { cpSync } from "node:fs";
import { defineConfig } from "tsup";

const pack = new URL("../../icon-pack/", import.meta.url);

export default defineConfig({
  entry: { index: "src/index.ts" },
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  target: "es2020",
  async onSuccess() {
    // SVGs and manifest are shipped verbatim from the icon pack (read-only source of truth).
    for (const dir of ["default", "gray", "solid"]) {
      cpSync(new URL(dir, pack), new URL(`dist/svg/${dir}`, import.meta.url), { recursive: true });
    }
    cpSync(new URL("manifest.json", pack), new URL("dist/manifest.json", import.meta.url));
  },
});
