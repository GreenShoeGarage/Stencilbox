# Changelog

## STENCILBOX rename — 2026-09-17

Renamed TRACEFORM to **STENCILBOX** throughout the app, repository package, documentation, export labels, and example designs. New JSON exports use `stencilbox-project`; imports also accept legacy `traceform-project` files with generator 1.0.0. Same-origin legacy autosave, preferences, shelf, and baseline entries are copied only when the new entry is absent; originals are retained. Existing STENCILBOX entries take precedence. Regenerated README screenshots and reran validation. Generator version remains 1.0.0 because generated geometry is unchanged.

## Repository packaging — 2026-09-17

No application or generator change; still 1.0.0. Added GitHub CI and optional Pages workflows, development setup, issue and pull-request templates, repository hygiene, source/build checks, and reproducible ZIP packaging. Test harnesses now write fresh output to ignored artifacts instead of modifying release examples or recorded evidence. Preserved application source, bundled HTML, licenses, example designs, and README screenshots.

## 1.0.0 — 2026-09-17

Initial release: eight deterministic geometric stencil families; editable pattern and opening transforms; four plate outlines; guarded connected-body geometry; binary STL, reproducible JSON and SVG export; top/3D/drawing views; software 3D fallback; local persistence and shelf; undo/redo; inspection findings and reports; accessible themes and mobile layout; regression tests and sample studies.
