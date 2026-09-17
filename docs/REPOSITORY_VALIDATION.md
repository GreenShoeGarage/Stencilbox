# STENCILBOX repository verification

Date: September 17, 2026. Application/generator version: **1.0.0**. Renamed from TRACEFORM at the user's direction.

## Scope of change

App and repository branding, export labels, shipped example titles, package filenames, screenshots, and documentation now use STENCILBOX. New project exports use `stencilbox-project`; imports also accept legacy `traceform-project` files. Browser data is copied from the old keys only when the corresponding new key is absent; the original data is retained.

**The geometry algorithm is unchanged.** Source comparison against the supplied original repository found only branding and format-compatibility edits on engine lines 1, 85, 97, 98, and 100. The stylesheet, 3D renderer, triangulator, and vendor license are byte-identical. All eight included sample STL triangle payloads are byte-identical after the 80-byte descriptive header. Legacy JSON test fixtures are exact copies of the original examples.

Current `index.html` SHA-256:

```text
880f8830c45a21e1ec37ec134d571ac3fa2b94362310ce3e29c879ae958af472
```

## Checks rerun for this package

| Check | Result |
| --- | --- |
| Deterministic geometry regression | 224 cases passed |
| Invalid-input rejection | 6 checks passed |
| Standard browser DOM integration | 44 checks passed |
| Legacy/current JSON compatibility | All 8 original examples restored with identical geometry |
| Rebrand, browser-storage copying, and precedence | 29 checks passed |
| Independent included STL verification | All 8 passed |
| Independent freshly generated STL verification | All 8 passed |
| Browser errors / app network requests in standard integration | 0 / 0 |
| Desktop, 3D, drawing, and mobile screenshots | Recaptured with new brand |
| Source/build match and repository structure/local links | Checked by `build.py --check` and `tools/check_repo.py` |

Current machine-readable results are in [validation/](validation/). The original pre-rename results under `tests/*-results.json` remain unchanged as historical evidence. Normal test runs write to ignored `artifacts/`; they do not overwrite either record.

## What the compatibility checks cover

Original saved contours regenerate exactly, new JSON exports use the new format name, user project titles and notes survive, and snapshot tampering and mismatched generator versions are still rejected. The browser suite tests project, preferences, shelf, and baseline copying; preservation of all four original keys; precedence of existing new entries (including empty shelf and cleared baseline); successful clean-install saving; and continued access to legacy geometry with an explicit JSON-backup warning when new writes fail.

## Environment and limits

Local browser: Chromium **144.0.7559.96**. Geometry ran under Node.js 22.16.0. Python was 3.13.5. The main and rename browser suites load the packaged HTML with `set_content` and use an in-memory storage adapter. This tests application behavior but does not certify native file-origin storage permissions. Software 3D is forced in the main integration suite. Export payloads are intercepted; native Save dialogs and slicer/printer behavior are not tested. Screenshots from the no-storage smoke test may show `Export JSON to save`; this is the actual storage-failure state in that harness.

Different origins cannot read each other's local browser data. Export/import JSON when moving to a different domain, browser, profile, or file location. See [RENAMING.md](RENAMING.md).

No GitHub repository or Pages site was created, renamed, or pushed. Workflows are included but have not run remotely. No physical printing, drawing-feel, or strength testing was performed.
