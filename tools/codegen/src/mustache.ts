// Minimal placeholder syntax for template files:
//   {{name}}               -> value
//   {{#flag}}...{{/flag}}  -> kept if flag is truthy
//   {{^flag}}...{{/flag}}  -> kept if flag is falsy
export function renderTemplate(source: string, vars: Record<string, string | boolean>): string {
  const sections = /\{\{([#^])([\w.]+)\}\}([\s\S]*?)\{\{\/\2\}\}/g;
  let output = source;
  let previous: string;
  do {
    previous = output;
    output = output.replace(sections, (_m, kind: string, key: string, body: string) => {
      const truthy = Boolean(vars[key]);
      return (kind === "#" ? truthy : !truthy) ? body : "";
    });
  } while (output !== previous);
  return output.replace(/\{\{([\w.]+)\}\}/g, (match, key: string) => {
    const value = vars[key];
    if (value === undefined) throw new Error(`Unknown template variable ${match}`);
    return String(value);
  });
}
