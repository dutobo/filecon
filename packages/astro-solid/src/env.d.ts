/// <reference types="astro/client" />

// For the tsc build of the TypeScript helpers only; consumers (and `astro check`) get real types for `.astro`
// imports from Astro's language tooling.
declare module "*.astro" {
  const Component: (props: Record<string, unknown>) => unknown;
  export default Component;
}
