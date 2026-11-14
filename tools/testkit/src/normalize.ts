// Normalization used to compare rendered output with the pack SVGs.
// Ignored on purpose: <title>, size attributes (width/height), a11y attributes, class, comments
// (framework hydration markers) and self-closing vs. explicit end tags (DOM serialization).

const KEPT_ROOT_ATTRIBUTES = new Set(["xmlns", "viewBox", "fill"]);

export function normalizeSvg(svg: string): string {
  let s = svg
    .trim()
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<title>[\s\S]*?<\/title>/g, "");
  s = s.replace(/<([a-zA-Z][\w:-]*)((?:\s+[\w:-]+="[^"]*")*)\s*\/>/g, "<$1$2></$1>");
  const match = /^<svg\b([^>]*)>([\s\S]*)<\/svg>$/.exec(s);
  if (!match) throw new Error(`Not an <svg> element: ${svg.slice(0, 120)}`);
  const attributes = [...(match[1] ?? "").matchAll(/([\w:-]+)="([^"]*)"/g)]
    .filter((m) => KEPT_ROOT_ATTRIBUTES.has(m[1] as string))
    .map((m) => `${m[1]}="${m[2]}"`)
    .sort();
  return `<svg ${attributes.join(" ")}>${match[2]}</svg>`;
}

/** Attributes of the root `<svg>` element. */
export function rootAttributes(svg: string): Record<string, string> {
  const match = /<svg\b([^>]*)>/.exec(svg.replace(/<!--[\s\S]*?-->/g, ""));
  if (!match) throw new Error("No <svg> element");
  return Object.fromEntries([...(match[1] ?? "").matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]));
}

/**
 * Evaluates an auto-theme SVG the way a browser would for the given color scheme, independently from the
 * production implementation: parses the embedded `@media (prefers-color-scheme: dark)` rules, applies them
 * to the elements carrying the classes, then drops `<style>` and `class` attributes.
 */
export function evaluateAutoTheme(svg: string, scheme: "light" | "dark"): string {
  const styleMatch = /<style>([\s\S]*?)<\/style>/.exec(svg);
  if (!styleMatch) throw new Error("auto theme: no embedded <style>");
  const css = styleMatch[1] ?? "";
  const media = /^@media \(prefers-color-scheme: dark\)\{([\s\S]*)\}$/.exec(css);
  if (!media) throw new Error(`auto theme: unexpected stylesheet ${css}`);
  const rules = new Map<string, [string, string][]>();
  for (const rule of (media[1] ?? "").matchAll(/\.([\w-]+)\{([^}]*)\}/g)) {
    const declarations = (rule[2] ?? "")
      .split(";")
      .filter(Boolean)
      .map((declaration) => declaration.split(":").map((part) => part.trim()) as [string, string]);
    rules.set(rule[1] as string, declarations);
  }
  const withoutStyle = svg.replace(styleMatch[0], "");
  return withoutStyle.replace(
    /<([a-zA-Z][\w:-]*)([^<>]*?)\s+class="([^"]*)"([^<>]*?)(\/?)>/g,
    (_m, tag, before, classes, after, slash) => {
      let attrs = `${before}${after}`;
      if (scheme === "dark") {
        for (const cls of String(classes).split(/\s+/)) {
          for (const [property, value] of rules.get(cls) ?? []) {
            const pattern = new RegExp(`(\\s${property}=)"[^"]*"`);
            attrs = pattern.test(attrs) ? attrs.replace(pattern, `$1"${value}"`) : `${attrs} ${property}="${value}"`;
          }
        }
      }
      return `<${tag}${attrs}${slash}>`;
    },
  );
}
