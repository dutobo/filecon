/**
 * Name of the single-icon export for an icon: PascalCase + `Icon` (`pdf` -> `PdfIcon`, `ts-stream` -> `TsStreamIcon`).
 * Names that start with a digit get an `Icon` prefix instead (`7z` -> `Icon7z`).
 */
export function iconComponentName(name: string): string {
  const pascal = name
    .split(/[^A-Za-z0-9]+/)
    .filter((part) => part.length > 0)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
  return /^[0-9]/.test(pascal) ? `Icon${pascal}` : `${pascal}Icon`;
}
