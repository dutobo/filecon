# Publishing

Status of every distribution channel and how to release it. Always run the full check first:

```sh
pnpm install && pnpm lint && pnpm typecheck && pnpm build && pnpm test
```

Tokens never go into the repository. Locally they live in the gitignored `.env` (one `key: value` per line, e.g.
`npmjs: …`, `crates: …`, `pypi: …`, `vsce: …`, `ovsx: …`) and are passed to the tools as environment variables.

| Channel | Package(s) | Status |
|---|---|---|
| npm | `@filecon/*` (105 packages) | published 0.3.1 |
| crates.io | `filecon`, `filecon-dioxus`, `tauri-plugin-filecon` | published 0.3.1 |
| VS Code Marketplace + Open VSX | `dutobo.filecon-icons` | prepared (`extensions/vscode`) |
| PyPI | `filecon` | prepared (`ports/python`) |
| Go, Swift PM, Packagist (Composer) | – | not started: need a public repository (see below) |
| NuGet, pub.dev (Flutter), RubyGems | – | not started: need the .NET SDK / Flutter / Ruby toolchains |
| Figma Community | – | manual: import the SVGs from `icon-pack/` into a Figma file and publish it |

## npm

Needs a **granular access token** with read/write access to the `@filecon` scope and "Bypass two-factor
authentication" (otherwise every publish asks for a 2FA approval).

```sh
dest="$(mktemp -d)"
pnpm -r --filter "./packages/**" exec pnpm pack --pack-destination "$dest"
printf '//registry.npmjs.org/:_authToken=%s\n' "$NPM_TOKEN" > "$dest/.npmrc"
for tgz in "$dest"/*.tgz; do   # publish @filecon/shared and @filecon/js* first
  npm publish "$tgz" --access public --provenance=false --userconfig "$dest/.npmrc"
done
rm "$dest/.npmrc"
```

`pnpm pack` resolves `workspace:` ranges and applies `publishConfig.exports`. Local publishes cannot create npm
provenance (`--provenance=false`); provenance needs GitHub Actions (`.github/workflows/release.yml`) **and a public
repository**. New packages take a few minutes to appear in the registry.

## crates.io

Order matters (dependents need the published `filecon` version):

```sh
pnpm codegen   # generated crate assets (icons, generated.rs, LICENSE/NOTICE) are gitignored
export CARGO_REGISTRY_TOKEN=…
cargo publish --manifest-path crates/filecon/Cargo.toml --allow-dirty
cargo publish --manifest-path crates/filecon-dioxus/Cargo.toml --allow-dirty
cargo publish --manifest-path crates/tauri-plugin-filecon/Cargo.toml --allow-dirty
```

`--allow-dirty` is required because the generated assets are listed in `include` but not committed.

## VS Code Marketplace and Open VSX

One-time setup:

1. Marketplace: create the publisher `dutobo` at <https://marketplace.visualstudio.com/manage> and an Azure DevOps
   personal access token with the scope **Marketplace → Manage** (organization: "All accessible organizations").
2. Open VSX: log in at <https://open-vsx.org> with GitHub, sign the publisher agreement, create an access token, then
   `pnpm dlx ovsx create-namespace dutobo -p "$OVSX_PAT"`.

Release:

```sh
pnpm codegen
cd extensions/vscode
pnpm dlx @vscode/vsce package --no-dependencies            # -> filecon-icons-<version>.vsix
pnpm dlx @vscode/vsce publish --no-dependencies -p "$VSCE_PAT" --packagePath filecon-icons-*.vsix
pnpm dlx ovsx publish filecon-icons-*.vsix -p "$OVSX_PAT"
```

## PyPI

One-time setup: a PyPI account with 2FA and an API token (after the first upload, restrict it to the `filecon`
project or switch to a Trusted Publisher).

```sh
pnpm codegen
cd ports/python
python -m pip install build twine pytest
python -m pytest
python -m build
python -m twine check dist/*
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" python -m twine upload dist/*
```

## Git-based registries (Go, Swift PM, Packagist)

These registries download straight from the Git repository, so they need:

- a **public** `dutobo/filecon` repository (Packagist and the Go proxy cannot read private repositories), and
- the icon assets **committed** in the module directory (or in a separate distribution repository / release branch),
  because the generated files are gitignored here.

Recommended: a small CI job that generates `go/`, `swift/` and `php/` distribution trees and pushes them to a
`dist` branch or separate repositories with version tags.

## After making the repository public

- npm: enable **Trusted Publishing** per package (npmjs.com → package → Settings → Trusted publisher → GitHub
  Actions, workflow `release.yml`); then releases need no token and get provenance automatically.
- crates.io and PyPI support Trusted Publishing from GitHub Actions as well.
