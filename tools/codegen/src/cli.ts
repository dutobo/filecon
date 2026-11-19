// Filecon codegen: icon pack + templates -> packages. Idempotent; run via `pnpm codegen` (also part of build/typecheck).
//
// Scaffolded (committed):  packages/<pkg>/{package.json, README.md, configs, src/*.ts, test/*}
// Generated (gitignored):  packages/<pkg>/src/generated/**, packages/<pkg>/{LICENSE,NOTICE}, crate assets
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";
import { pathToFileURL } from "node:url";
import { generateCss, generateIconify } from "./assets";
import { PACKAGES_DIR, ROOT, SCOPE, STYLES, TEMPLATES_DIR, VARIANTS, type Variant } from "./config";
import { variantModule } from "./data-module";
import { listFiles, stats, syncDirectory, toPosix, writeIfChanged } from "./fsutil";
import { LEGAL_FILES, legalFile } from "./legal";
import { renderTemplate } from "./mustache";
import { loadPack, type Pack } from "./pack";
import { composePackageJson } from "./package-json";
import { generatePython } from "./python";
import { generateCrate } from "./rust";
import { standalonePackages } from "./standalone";
import type { FrameworkTemplate, TemplateContext } from "./template-api";
import { GENERATED_HEADER } from "./template-api";
import { generateVscode } from "./vscode";

const STYLE_LABEL: Record<Variant, string> = {
  all: "all nine styles (default, gray, solid, papered, papered-flat, papered-craft, scratch, chalk, iconic)",
  default: "the default style (outline, colored label)",
  gray: "the gray style (filled gray page)",
  solid: "the solid style (filled colored page)",
  papered: "the papered style (realistic sheet of paper)",
  "papered-flat": "the papered-flat style (flat, warm paper)",
  "papered-craft": "the papered-craft style (cut paper layers)",
  scratch: "the scratch style (pencil sketch on a note sheet)",
  chalk: "the chalk style (chalk on a blackboard, marker on a whiteboard)",
  iconic: "the iconic style (a standalone symbol per file type instead of a page shape)",
};

/** Template order: `js` first because every other package takes its data from the js packages. */
async function loadTemplates(): Promise<FrameworkTemplate[]> {
  const ids = readdirSync(TEMPLATES_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && existsSync(join(TEMPLATES_DIR, entry.name, "template.ts")))
    .map((entry) => entry.name)
    .sort((a, b) => (a === "js" ? -1 : b === "js" ? 1 : a.localeCompare(b)));
  const templates: FrameworkTemplate[] = [];
  for (const id of ids) {
    const mod = (await import(pathToFileURL(join(TEMPLATES_DIR, id, "template.ts")).href)) as {
      default: FrameworkTemplate;
    };
    if (mod.default.id !== id) throw new Error(`Template id "${mod.default.id}" must match its folder "${id}"`);
    templates.push(mod.default);
  }
  return templates;
}

function contextFor(template: FrameworkTemplate, variant: Variant, pack: Pack): TemplateContext {
  const suffix = variant === "all" ? "" : `-${variant}`;
  const dirName = `${template.id}${suffix}`;
  const packageName = `${SCOPE}/${dirName}`;
  const dataPackage = `${SCOPE}/js${suffix}`;
  const fixedStyle = variant === "all" ? null : variant;
  const styles = fixedStyle ? [fixedStyle] : [...STYLES];
  const allPackage = `${SCOPE}/${template.id}`;
  return {
    framework: template.id,
    variant,
    packageName,
    dirName,
    styles,
    fixedStyle,
    dataPackage,
    dataImport: `${dataPackage}/data`,
    icons: pack.icons,
    pack,
    vars: {
      packageName,
      dirName,
      framework: template.id,
      title: template.title,
      variant,
      isAll: variant === "all",
      isSingle: variant !== "all",
      fixedStyle: fixedStyle ?? "",
      firstStyle: styles[0] as string,
      styleLabel: STYLE_LABEL[variant],
      allPackage,
      dataPackage,
      iconCount: String(pack.icons.length),
      siblings: VARIANTS.map((v) => `\`${allPackage}${v === "all" ? "" : `-${v}`}\``).join(", "),
    },
  };
}

/** Copies `files/` of a template into the package. `*.tpl` files are rendered and lose the suffix. */
function scaffold(templateDir: string, packageDir: string, ctx: TemplateContext): void {
  const filesDir = join(templateDir, "files");
  for (const source of listFiles(filesDir)) {
    const relPath = relative(filesDir, source);
    if (relPath.endsWith(".tpl")) {
      writeIfChanged(join(packageDir, relPath.slice(0, -4)), renderTemplate(readFileSync(source, "utf8"), ctx.vars));
    } else {
      writeIfChanged(join(packageDir, relPath), readFileSync(source));
    }
  }
}

function copyLegalFiles(packageDir: string): void {
  for (const file of LEGAL_FILES) writeIfChanged(join(packageDir, file), legalFile(file));
}

function generateShared(pack: Pack): void {
  const dir = join(PACKAGES_DIR, "shared", "src", "generated");
  const names = pack.icons.map((icon) => icon.name);
  const union = names.map((name) => `  | ${JSON.stringify(name)}`).join("\n");
  syncDirectory(dir, {
    "names.ts": `${GENERATED_HEADER}
/** One of the ${names.length} icon names of the Filecon icon pack. */
export type IconName =
${union};

/** All icon names, sorted. */
export const iconNames: readonly IconName[] = ${JSON.stringify(names, null, 2)};
`,
    "theme.ts": `${GENERATED_HEADER}import type { ThemeTable } from "../theme-core";

/** Theme classes derived from the light/dark pairs of the pack: class -> [attribute, light, dark]. */
export const THEME_TABLE: ThemeTable = ${JSON.stringify(pack.themeTable, null, 2)};
`,
  });
}

async function main(): Promise<void> {
  const started = Date.now();
  const pack = loadPack();
  generateShared(pack);
  copyLegalFiles(ROOT);

  for (const standalone of standalonePackages(pack)) {
    const packageDir = join(PACKAGES_DIR, standalone.dirName);
    writeIfChanged(
      join(packageDir, "package.json"),
      composePackageJson(`${SCOPE}/${standalone.dirName}`, standalone.dirName, standalone.parts),
    );
    copyLegalFiles(packageDir);
  }

  const templates = await loadTemplates();
  for (const template of templates) {
    for (const variant of VARIANTS) {
      const ctx = contextFor(template, variant, pack);
      const packageDir = join(PACKAGES_DIR, ctx.dirName);
      scaffold(join(TEMPLATES_DIR, template.id), packageDir, ctx);
      writeIfChanged(
        join(packageDir, "package.json"),
        composePackageJson(ctx.packageName, ctx.dirName, template.packageJson(ctx)),
      );
      const generated = template.generate(ctx);
      for (const path of Object.keys(generated)) {
        if (!toPosix(path).startsWith("src/generated/"))
          throw new Error(`${template.id}: generated file outside src/generated/: ${path}`);
      }
      const files: Record<string, string> = { "variant.ts": variantModule(ctx) };
      for (const [path, content] of Object.entries(generated))
        files[toPosix(path).slice("src/generated/".length)] = content;
      syncDirectory(join(packageDir, "src", "generated"), files);
      copyLegalFiles(packageDir);
    }
  }

  generateIconify(pack);
  generateCss(pack);
  generateCrate(pack);
  generateVscode(pack);
  generatePython(pack);
  console.log(
    `codegen: ${pack.icons.length} icons, ${templates.length} templates -> ${stats.written} written, ` +
      `${stats.unchanged} unchanged, ${stats.removed} removed (${Date.now() - started} ms)`,
  );
}

main().catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
