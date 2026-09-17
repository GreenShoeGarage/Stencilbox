# STENCILBOX v1.0.0 — validation record

Original pre-rename release review: September 17, 2026. The results below describe TRACEFORM v1.0.0 before renaming. The original `tests/*-results.json` files are retained unchanged as historical evidence. For the STENCILBOX rebrand validation, including legacy-file and browser-storage compatibility, see [REPOSITORY_VALIDATION.md](REPOSITORY_VALIDATION.md).

## Results

| Test layer | Result |
| --- | --- |
| Deterministic geometry regression | **224 / 224 cases passed** |
| Input rejection checks | **6 passed** |
| Browser integration | **44 checks passed**, Chromium 144.0.7559.96 |
| Independent sample-STL inspection | **8 / 8 passed** |
| Browser JavaScript errors | **0** |
| App network requests during DOM integration tests | **0** |

The artifacts below record results rather than asserting universal compatibility or physical strength.

## Geometry coverage

`tests/geometry.test.js` checks 28 cases in each of eight pattern families: a representative study, 24 seeded variations, a blank plate, an extreme no-room configuration, and a dense/collinear configuration. Variations exercise shapes, four plate outlines, thickness, border, minimum web, density, both kinds of scale, rotation, individual opening rotation, X/Y stretch, shear, translation, mirrors, and corner softening.

Every case tests closed paired mesh edges, consistent winding, nondegenerate triangles, one component, positive volume, expected volume and Euler characteristic, simple planar contours, requested border/web clearances, binary-STL structure, deterministic regeneration, and an exact JSON contour round-trip.

Malformed format names, incorrect units, incompatible generator releases, a corrupted geometry snapshot, a non-finite numeric input, and an unknown family are rejected.

During development, Float32 conversion exposed two collinear-triangle failures in strongly transformed facet patterns. The pipeline now converts coordinates before triangulation. Those cases are included in the final passing run. A display test also caught the SVG remaining visible behind the 3D canvas; a visibility assertion now covers that transition.

Recorded result: `tests/geometry-results.json`.

## Independent binary-STL checks

`tests/validate_stl.py` reopens the actual exported bytes using **Trimesh**, rather than reusing the app's mesh checker. It checks watertightness, consistent winding, positive volume, one body, nonzero face areas, expected dimensions, and expected volume. **Shapely** separately validates the saved planar polygons, containment, disjoint openings, border distance, and inter-opening clearance.

| File | Openings | Triangles | Dimensions, mm | Result |
| --- | ---: | ---: | --- | --- |
| grid-study.stl | 56 | 9,388 | 160.0 × 120.0 × 1.6 | Pass |
| honeycomb-study.stl | 40 | 5,164 | 160.0 × 120.0 × 1.6 | Pass |
| radial-study.stl | 81 | 5,692 | 150.0 × 150.0 × 1.6 | Pass |
| scatter-study.stl | 52 | 7,552 | 160.0 × 120.0 × 1.6 | Pass |
| triangles-study.stl | 60 | 4,044 | 160.0 × 120.0 × 1.6 | Pass |
| voronoi-study.stl | 52 | 5,992 | 160.0 × 120.0 × 1.6 | Pass |
| waves-study.stl | 55 | 11,424 | 170.0 × 100.0 × 1.6 | Pass |
| weave-study.stl | 56 | 11,628 | 140.0 × 140.0 × 1.6 | Pass |

Recorded result: `tests/independent-stl-results.json`. Exact binary floating-point extents are retained there; rounded dimensions are shown above.

## Browser coverage

The browser suite interacts with the actual packaged HTML and tests settings, geometry-changing transforms, all eight family buttons, undo/redo, individual editing and rejection of unsafe moves, hiding an opening, JSON export and file import, binary STL and SVG payloads, report generation, shelf capture, baseline comparison, 3D orbit and view visibility, theme switching, clear/undo behavior, and a 390 × 844 mobile layout.

Storage-adapter tests verify that autosave writes the correct project and displays the corresponding status. The separate smoke run also verifies the app remains operational when browser storage is unavailable. Screenshot files from that isolated, no-storage smoke run truthfully show its export-to-save status where visible.

Recorded result: `tests/browser-results.json`. Scripts: `tests/browser.test.py` and `tests/smoke.py`.

## Explicit limitations

- The managed browser blocks URL navigation: embedded HTML was tested with set_content, not direct file:// or hosted navigation.
- Autosave and shelf logic tested with a storage adapter; native file-origin browser persistence not tested.
- The software 3D fallback was exercised; WebGL was unavailable in this environment.
- Download payloads were inspected through a Blob interceptor; native Save dialog behavior was not tested.
- Print-report generation and invocation tested; physical printing and slicer import not performed.
- Safari and Firefox have not been run in this environment.
- The tests cover selected generated designs, not every possible setting combination.
- No independent slicer toolpath check, printer/material qualification, strength test, flexibility test, pencil-access simulation, or physical drawing trial has been performed.

The package is designed as a self-contained file and static page. Native launch, persistence, printing, and download behavior still depend on the destination browser and its policy. Keep JSON backups and inspect the model in the actual slicer before manufacturing.
