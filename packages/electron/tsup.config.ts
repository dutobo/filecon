import { defineConfig } from "tsup";

export default defineConfig({
  entry: { index: "src/index.ts", main: "src/main.ts", preload: "src/preload.ts", renderer: "src/renderer.ts" },
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  target: "node20",
  external: [/^@filecon\//, "electron"],
});
