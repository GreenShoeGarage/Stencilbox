# STENCILBOX rename and compatibility

STENCILBOX is the new name of TRACEFORM. This is a branding and project-format compatibility update, not a change to the pattern generator. Application/generator version remains **1.0.0**.

## What changed

The application title and header, errors, print reports, STL header, SVG titles, JSON export identifier, examples, README, repository name, packaging filenames, test names, and workflow artifact names now use STENCILBOX. The repository folder is `stencilbox/`. Runtime remains the self-contained `index.html`.

## Existing JSON projects

STENCILBOX accepts both `stencilbox-project` and the legacy `traceform-project` format with schema 1, generator 1.0.0, and millimeter units. Geometry snapshots are still checked against regenerated geometry; damaged snapshots and incompatible generator versions are rejected. New exports use `stencilbox-project`. The old TRACEFORM application cannot read the newly named format without an update; retain your original JSON when exchanging with an unupdated copy.

Project titles and notes from imported or autosaved user designs are not renamed or rewritten. The shipped example project titles are updated because they are demonstration content.

## Browser storage

When a STENCILBOX key is absent, the app looks for its TRACEFORM counterpart in the **same browser storage origin**, copies the saved value, and leaves the original intact:

| Current key | Legacy key |
| --- | --- |
| `stencilbox.project.v1` | `traceform.project.v1` |
| `stencilbox.preferences.v1` | `traceform.preferences.v1` |
| `stencilbox.shelf.v1` | `traceform.shelf.v1` |
| `stencilbox.baseline.v1` | `traceform.baseline.v1` |

An existing STENCILBOX entry always takes precedence. Clearing all site data deletes browser copies of both apps. Moving to a different domain, browser, profile, or local file location can make previous storage inaccessible. Export your current project as JSON before moving files; open it through **Open JSON** in STENCILBOX. Shelf entries are local, so export individual designs that need to travel to another origin.

No server-side migration, external accounts, or network access is used. The legacy `window.Traceform` hook remains an alias for `window.Stencilbox`; the current readiness flag is `window.__stencilboxReady`.

## Hosting

Replace the current hosted `index.html` to keep the same route. To use the new route, place the file at `/stencilbox/index.html`. The app has no route-specific asset paths. A GitHub repository may be named `stencilbox`; this archive does not create or rename a remote repository or configure a redirect from an older URL.
