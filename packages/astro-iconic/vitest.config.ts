import { getViteConfig } from "astro/config";

type ViteConfig = Parameters<typeof getViteConfig>[0];

// Astro's Vite config (compiles .astro files) plus the vitest options.
const config: ReturnType<typeof getViteConfig> = getViteConfig({
  test: { include: ["test/**/*.test.ts"], testTimeout: 180_000 },
} as ViteConfig);

export default config;
