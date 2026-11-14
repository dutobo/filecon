import "@angular/compiler";
import { reflectComponentType } from "@angular/core";
import { type ComponentFixture, getTestBed, TestBed } from "@angular/core/testing";
import { BrowserTestingModule, platformBrowserTesting } from "@angular/platform-browser/testing";
import { conformanceSuite, type RenderProps } from "@filecon/testkit";
import { describe, expect, it } from "vitest";
import { FIXED_STYLE, PACKAGE_NAME, STYLES } from "../src/generated/variant";

// Tests run against the built package (partial compilation output, linked at runtime by @angular/compiler).
getTestBed().initTestEnvironment(BrowserTestingModule, platformBrowserTesting());
const lib = (await import(/* @vite-ignore */ PACKAGE_NAME)) as typeof import("../src/index");

let fixture: ComponentFixture<unknown> | undefined;

function render(inputs: Record<string, unknown>): string {
  fixture ??= TestBed.createComponent(lib.FileconIconComponent);
  const defaults: Record<string, unknown> = { name: undefined, file: undefined, icon: undefined, title: undefined };
  for (const [key, value] of Object.entries({ ...defaults, ...inputs })) {
    if (value !== undefined || key in defaults) fixture.componentRef.setInput(key, value);
  }
  fixture.componentRef.setInput("theme", inputs.theme ?? "light");
  fixture.componentRef.setInput("size", inputs.size ?? 40);
  if (FIXED_STYLE === null) fixture.componentRef.setInput("iconStyle", inputs.iconStyle ?? "default");
  fixture.detectChanges();
  return (fixture.nativeElement as HTMLElement).innerHTML;
}

const toInputs = ({ style, className: _className, ...rest }: RenderProps): Record<string, unknown> => ({
  ...rest,
  ...(FIXED_STYLE ? {} : { iconStyle: style }),
});

conformanceSuite({
  packageName: PACKAGE_NAME,
  styles: STYLES,
  render: (props) => render(toInputs(props)),
  renderSingle: (exportName, props) =>
    render({ ...toInputs(props), icon: (lib as Record<string, unknown>)[exportName] }),
  singleExports: lib as unknown as Record<string, unknown>,
  iconComponentName: lib.iconComponentName,
  classOnSvg: false,
});

describe("angular specifics", () => {
  it("is a standalone component with the filecon-icon selector", () => {
    const mirror = reflectComponentType(lib.FileconIconComponent);
    expect(mirror?.selector).toBe("filecon-icon");
    expect(mirror?.isStandalone).toBe(true);
  });

  it("accepts single icon definitions", () => {
    expect(lib.PdfIcon).toMatchObject({ name: "pdf" });
    expect(render({ icon: lib.PdfIcon })).toBe(render({ name: "pdf" }));
  });
});
