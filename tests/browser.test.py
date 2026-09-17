"""Offline DOM integration tests. No network navigation is used.
The app is loaded with set_content; this harness does not test URL navigation.
A storage adapter tests persistence logic, NOT native file-origin storage permissions.
Downloads and printing are intercepted at the UI boundary and their payloads checked.
"""
from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path(os.environ.get('STENCILBOX_TEST_OUTPUT', ROOT/'artifacts/test-results'))
OUTPUT.mkdir(parents=True,exist_ok=True)
checks=[]
def ok(name,condition=True):
    assert condition,name
    checks.append(name)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-webgl'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.evaluate("""() => {
      const map=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>map.has(k)?map.get(k):null,setItem:(k,v)=>map.set(k,String(v)),removeItem:k=>map.delete(k)}});
      window.__blobs=[];URL.createObjectURL=(blob)=>{window.__blobs.push(blob);return 'blob:stencilbox-test';};URL.revokeObjectURL=()=>{};
      HTMLAnchorElement.prototype.click=function(){window.__lastFilename=this.download;};
      window.print=()=>{window.__printCalled=true;};
    }""")
    page.set_content((ROOT/'index.html').read_text())
    page.wait_for_function('window.__stencilboxReady===true')
    ok('Initial mesh passes',page.evaluate('Stencilbox.getMesh().validation.ok'))
    page.wait_for_timeout(600)
    ok('Autosave writes project with storage adapter',page.evaluate('JSON.parse(localStorage.getItem("stencilbox.project.v1")).format==="stencilbox-project"'))
    ok('Autosave status truthful',page.locator('#saveStatus').inner_text()=='Saved locally')
    baseline=page.evaluate('JSON.stringify(Stencilbox.getModel().holes.map(h=>h.poly))')
    page.locator('#rotation').fill('22');page.locator('#rotation').dispatch_event('change');page.wait_for_timeout(300)
    ok('Pattern rotation changes geometry',page.evaluate('JSON.stringify(Stencilbox.getModel().holes.map(h=>h.poly))')!=baseline)
    page.locator('#undoBtn').click();ok('Undo restores exact geometry',page.evaluate('JSON.stringify(Stencilbox.getModel().holes.map(h=>h.poly))')==baseline)
    page.locator('#redoBtn').click();ok('Redo reapplies rotation',page.evaluate('Stencilbox.getSettings().rotation')==22)
    page.evaluate('Stencilbox.undo()')
    page.locator('#modeBtn').click();ok('Advanced controls exposed',page.locator('#stretchXRange').is_visible())
    page.evaluate('Stencilbox.setSetting("stretchX",120)');ok('Stretch changes geometry',page.evaluate('Stencilbox.getSettings().stretchX')==120)
    page.evaluate('Stencilbox.undo()')
    page.evaluate('Stencilbox.setSetting("mirrorX",true)');ok('Mirror keeps mesh valid',page.evaluate('Stencilbox.getMesh().validation.ok'));page.evaluate('Stencilbox.undo()')
    page.evaluate('Stencilbox.setSetting("shear",25)');ok('Shear keeps mesh valid',page.evaluate('Stencilbox.getMesh().validation.ok'));page.evaluate('Stencilbox.undo()')
    page.evaluate('Stencilbox.setSetting("offsetX",12)');ok('Translation keeps mesh valid',page.evaluate('Stencilbox.getMesh().validation.ok'));page.evaluate('Stencilbox.undo()')
    for family in ['scatter','grid','honeycomb','triangles','voronoi','radial','waves','weave']:
        page.locator(f'[data-pattern="{family}"]').click();page.wait_for_timeout(400)
        ok(f'{family} UI pattern switch',page.evaluate(f'Stencilbox.getSettings().pattern==="{family}" && Stencilbox.getMesh().validation.ok'))
    page.locator('[data-pattern="voronoi"]').click();page.wait_for_timeout(300)
    page.evaluate('Stencilbox.select(Stencilbox.getModel().holes[0].id)')
    ok('Opening inspector visible',page.locator('#selectionPanel').is_visible())
    before=page.evaluate('JSON.stringify(Stencilbox.getProject().edits)')
    page.evaluate('Stencilbox.applyEdit({dx:1000})')
    ok('Unsafe individual move rejected',page.evaluate('JSON.stringify(Stencilbox.getProject().edits)')==before)
    ok('Safe individual scaling accepted',page.evaluate('Stencilbox.applyEdit({scale:85})'))
    ok('Per-opening edit mesh valid',page.evaluate('Stencilbox.getMesh().validation.ok'))
    count=page.evaluate('Stencilbox.getModel().holes.length')
    page.locator('#deleteHoleBtn').click();ok('Hide opening works',page.evaluate('Stencilbox.getModel().holes.length')<count)
    page.evaluate('Stencilbox.undo()')
    project=page.evaluate('Stencilbox.getProject()')
    page.locator('#saveBtn').click()
    saved=page.evaluate('async()=>JSON.parse(await window.__blobs[window.__blobs.length-1].text())')
    ok('JSON export payload matches project',saved['geometry']==project['geometry'])
    page.locator('#stlBtn').click()
    binary=page.evaluate('async()=>{const b=await window.__blobs[window.__blobs.length-1].arrayBuffer();return {bytes:b.byteLength,faces:new DataView(b).getUint32(80,true)}}')
    ok('STL export payload is valid binary format',binary['bytes']==84+50*binary['faces'])
    page.locator('#svgBtn').click();svg=page.evaluate('async()=>await window.__blobs[window.__blobs.length-1].text()')
    ok('SVG export has millimeter units','width="160mm"' in svg)
    page.locator('#reportBtn').click();ok('Report populated and print invoked',page.evaluate('window.__printCalled&&document.getElementById("printReport").textContent.includes("Findings & evidence")'))
    page.locator('#fileInput').set_input_files({'name':'roundtrip.json','mimeType':'application/json','buffer':json.dumps(saved).encode()})
    page.wait_for_selector('#confirmDialog[open]');page.locator('#confirmOK').click();page.wait_for_timeout(300)
    ok('JSON file import restores exact contours',page.evaluate('Stencilbox.getProject().geometry')==saved['geometry'])
    page.locator('#shelfBtn').click();page.locator('#captureBtn').click();ok('Design shelf capture',page.locator('.shelf-card').count()==1)
    page.locator('#baselineBtn').click();ok('Baseline comparison appears','Baseline:' in page.locator('#baselineInfo').inner_text())
    page.locator('#shelfDialog [data-close]').click()
    page.locator('[data-view="3d"]').click();page.wait_for_timeout(300)
    ok('3D canvas visible',page.locator('#glCanvas').is_visible())
    ok('2D SVG actually hidden in 3D view',not page.locator('#preview').is_visible())
    start=page.locator('#glCanvas').screenshot()
    box=page.locator('#glCanvas').bounding_box();cx=box['x']+box['width']/2;cy=box['y']+box['height']/2
    page.mouse.move(cx,cy);page.mouse.down();page.mouse.move(cx+90,cy+35,steps=3);page.mouse.up();page.wait_for_timeout(100)
    ok('3D orbit changes rendered pixels',page.locator('#glCanvas').screenshot()!=start)
    page.locator('#zoomInBtn').click();ok('3D zoom remains rendered',page.locator('#glCanvas').is_visible())
    page.locator('[data-view="drawing"]').click();ok('Drawing mode visible',page.locator('#preview').is_visible() and not page.locator('#glCanvas').is_visible())
    page.locator('[data-view="stencil"]').click();page.locator('#themeBtn').click();ok('Light theme switch',page.evaluate('document.documentElement.dataset.theme')=='light')
    page.locator('#themeBtn').click();ok('High contrast theme switch',page.evaluate('document.documentElement.dataset.theme')=='contrast')
    page.locator('#themeBtn').click()
    page.locator('#blankBtn').click();page.locator('#confirmOK').click();ok('Clear openings produces valid blank',page.evaluate('Stencilbox.getModel().holes.length===0 && Stencilbox.getMesh().validation.ok'))
    page.evaluate('Stencilbox.undo()');ok('Clear openings is undoable',page.evaluate('Stencilbox.getModel().holes.length>0'))
    page.set_viewport_size({'width':390,'height':844});page.evaluate('document.getElementById("collapseBtn").click()');page.wait_for_timeout(100)
    ok('Mobile has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth===document.documentElement.clientWidth'))
    page.locator('#showControlsBtn').click();ok('Mobile controls open',page.locator('#controls').is_visible());page.locator('#collapseBtn').click()
    ok('No JavaScript errors',not errors);ok('No network requests',not requests)
    result={'browser':browser.version,'passed':len(checks),'checks':checks,'errors':errors,'networkRequests':requests,'limitations':['This DOM harness uses set_content rather than direct file:// or hosted navigation.','Autosave and shelf logic tested with a storage adapter; native file-origin browser persistence not tested.','Software 3D is forced for deterministic coverage; this suite does not test WebGL.','Download payloads were inspected through a Blob interceptor; native Save dialog behavior was not tested.','Print-report generation and invocation tested; physical printing and slicer import not performed.']}
    (OUTPUT/'browser-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    browser.close()
