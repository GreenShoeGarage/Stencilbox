# Third-party notices

## Mapbox Earcut

`vendor/earcut.js` is the isolated CommonJS triangulation module extracted from the installed Plotly.js 3.3.1 distribution. Its browser/global wrapper was adapted for STENCILBOX. The module implements the classic Earcut API, including holes, deviation, and flattening. No assertion is made about the exact upstream Earcut package version embedded by Plotly.

Copyright (c) 2016, Mapbox. ISC license: see `vendor/EARCUT-LICENSE.txt`.

Upstream project and API reference:

```text
https://github.com/mapbox/earcut
```

The entire vendor license is retained in the portable HTML build as well as in the repository. The rest of Plotly is not included.

## Primary technical references

These references informed format handling and the limits stated in the UI; they are not runtime dependencies.

```text
Earcut API and robustness notes:
https://github.com/mapbox/earcut

STL geometry, binary/ASCII representations, and arbitrary units:
https://threejs.org/docs/pages/STLExporter.html

Modeling considerations for 3D printing:
https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
```

STENCILBOX uses its own STL writer and 3D renderer. It does not include Three.js or code from the Prusa article. The three-extrusion-line warning is STENCILBOX's disclosed conservative heuristic, not a certification or a manufacturer-prescribed universal minimum.
