# Contributing to STENCILBOX

STENCILBOX is a small local-first instrument, not a service. Preserve its single-file runtime, offline operation, clear failure states, accessible controls, and editable JSON projects.

## Make a change

Work in `src/`, not in the generated root `index.html`. Run `python3 build.py` after source changes and commit both the source and regenerated HTML. Do not add a CDN, telemetry, account requirement, or runtime package installation.

See [development commands](docs/DEVELOPMENT.md). At minimum run the build check, repository check, and geometry suite. Changes affecting UI, storage, import/export, or geometry also need the applicable browser and independent STL tests. Fresh results go into ignored `artifacts/`, not the checked-in release evidence under `tests/`.

A bug report should include app version, browser/OS, launch method, steps, seed/settings, and a sanitized JSON file when useful. Remove personal notes first. For STL problems include slicer version, unit interpretation, and expected versus observed dimensions. Screenshots alone cannot reproduce geometry.

## Geometry compatibility

A seed and recipe must reproduce the same contours. Do not silently change an existing generator version. Changes to generation, precision, contour topology, or serialization require an explicit compatibility decision, regression tests, and changelog entry. `VERSION`, `package.json`, UI labels, engine version, and documentation should agree when the app version changes.

Keep failed exports blocked. Mesh validation is not a strength or printability guarantee. Preserve measured findings, confidence levels, assumptions, and honest test limitations.

## Scope and licensing

Keep contributions focused and describe user-visible effects in the pull request. Preserve `LICENSE`, `THIRD_PARTY_NOTICES.md`, and vendor notices. Do not commit `.env` files, credentials, private JSON projects, or generated test caches. Test changes are welcome; unsupported universal printer or browser compatibility claims are not.
