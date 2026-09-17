"""Independent binary-STL inspection with trimesh and planar checks with Shapely."""
from pathlib import Path
import json
import os
import numpy as np
import trimesh
from shapely.geometry import Polygon
root = Path(__file__).resolve().parents[1]
output=Path(os.environ.get('STENCILBOX_TEST_OUTPUT', root/'artifacts/test-results'))
output.mkdir(parents=True,exist_ok=True)
example_dir=Path(os.environ.get('STENCILBOX_EXAMPLES', root/'examples'))
files=sorted(example_dir.glob('*.stl'))
if len(files)!=8:
    raise RuntimeError(f'Expected eight sample STLs in {example_dir}; found {len(files)}')
results=[]
for file in files:
    m=trimesh.load_mesh(file,process=True)
    data=json.loads(file.with_suffix('.json').read_text())
    settings=data['settings']; geom=data['geometry']; outer=Polygon(geom['outer']); holes=[Polygon(h['points']) for h in geom['openings']]
    assert outer.is_valid, file
    for h in holes:
        assert h.is_valid and outer.contains(h),file
        assert h.distance(outer.boundary)>=settings['border']-0.00011,file
    for i,h in enumerate(holes):
        for j in range(i):
            assert h.disjoint(holes[j]),file
            assert h.distance(holes[j])>=settings['minWeb']-0.00011,file
    expected=(outer.area-sum(h.area for h in holes))*settings['thickness']
    assert m.is_watertight,file
    assert m.is_winding_consistent,file
    assert m.is_volume,file
    assert len(m.split(only_watertight=False))==1,file
    assert np.all(m.area_faces>1e-10),file
    assert np.allclose(m.extents,[settings['width'],settings['height'],settings['thickness']],atol=.001),file
    assert abs(m.volume-expected)/expected<1e-6,file
    results.append(dict(file=file.name,watertight=bool(m.is_watertight),consistent_winding=bool(m.is_winding_consistent),positive_volume=bool(m.is_volume),components=1,triangles=len(m.faces),dimensions_mm=m.extents.tolist(),volume_mm3=float(m.volume),holes=len(holes),planar_geometry_valid=True))
(output/'independent-stl-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
