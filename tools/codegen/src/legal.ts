// LICENSE and NOTICE for every published artifact: the pack's files plus the notice of the generated styles.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { PACK_DIR, ROOT } from "./config";

export const LEGAL_FILES = ["LICENSE", "NOTICE"] as const;

/** Content of LICENSE (the pack's) or NOTICE (the pack's + tools/stylegen/NOTICE). */
export function legalFile(file: (typeof LEGAL_FILES)[number]): Buffer {
  const base = readFileSync(join(PACK_DIR, file));
  if (file === "LICENSE") return base;
  return Buffer.concat([base, readFileSync(join(ROOT, "tools", "stylegen", "NOTICE"))]);
}
