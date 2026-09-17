# STENCILBOX 1.0.0 architecture

## Single-file artifact

`build.py` embeds the stylesheet, Earcut module, geometry engine, viewer, and app into `index.html`. The result has no runtime fetches. A restrictive Content Security Policy permits only embedded code/styles and data/blob images, and disallows `connect-src`. System fonts are used; no font files are bundled.

## Geometry pipeline

1. Normalize whitelisted settings and initialize a deterministic, seed-based pseudorandom generator.
2. Generate candidate opening polygons. Voronoi uses repeated convex half-plane clipping; triangular cells use geometric insets; other families place polygonal motifs.
3. Soften polygon corners where applicable, scale/rotate openings around their centers, apply the global affine transformation, then apply ID-based individual edits.
4. Round generated contours to five decimal places. Preserve counterclockwise contour orientation after mirrors.
5. Accept openings only inside the convex board's inward-offset half-planes and at the requested polygon-to-polygon distance from previous openings. Report omissions or bounded packing limits.
6. Convert coordinates to the same Float32 precision that binary STL uses, then triangulate the plate and holes with Earcut. Correct applicable collinear T-junctions.
7. Extrude top/bottom surfaces and side walls. Validate edge incidence and direction, connectedness, signed volume, triangle area, and Euler characteristic.
8. Use the validated vertex/face arrays for 3D display and binary STL serialization.

The plate outlines are convex, and the generator's cutouts are simple, disjoint, non-nested polygons. This restricted geometry avoids the disconnected-island problem without a general polygon-boolean dependency. It is not a boolean editor for arbitrary artwork.

## State and persistence

The authoritative editable state is the settings object plus ID-keyed opening edits. Project JSON also stores generated contours for a reproducibility check. The importer validates the format, schema, generator release and units before regenerating. The browser autosave stores the smaller recipe/edits form, without a redundant geometry snapshot. JSON exports contain the geometry and inspection snapshot.

Undo/redo stores bounded recipe snapshots. The local shelf stores up to 18 copies. Baseline metrics compare usable opening count, percentage open area, and geometric material volume. There is no collaborative backend, account model, telemetry, or sync.

## Renderer

The primary viewer is a small orthographic WebGL renderer. The fallback performs actual triangle projection and per-pixel depth testing in Canvas ImageData. Neither changes the export mesh or exaggerates its thickness. The stencil and drawing views use inline SVG, with mathematical Y-up geometry transformed into SVG display coordinates.

## Safety boundaries

Geometry validation does not simulate thermal distortion, adhesion, flexibility, strength, printer motion, slicer toolpaths, or pencil contact. Print assumptions affect warnings only. A unitless STL must be interpreted correctly by the slicer. The report is an inspection record, not an engineering certification.
