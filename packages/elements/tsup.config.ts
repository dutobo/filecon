import { defineConfig } from "tsup";

export default defineConfig({
  entry: { index: "src/index.ts", icons: "src/icons.ts", define: "src/define.ts" },
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  target: "es2020",
  external: [/^@filecon\//],
});
