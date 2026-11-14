import { defineConfig } from "tsup";

export default defineConfig({
  entry: { index: "src/index.ts", icons: "src/icons.ts", data: "src/data.ts" },
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  target: "es2020",
  // Icon data is only bundled into the `data` entry; `index` and `icons` import it via the package name.
  external: [/^@filecon\//],
});
