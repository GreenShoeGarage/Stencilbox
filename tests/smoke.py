from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
OUTPUT=Path(os.environ.get('STENCILBOX_SCREENSHOT_OUTPUT', ROOT/'artifacts/screenshots'))
OUTPUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'),headless=True, args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width':1440,'height':1050}, device_scale_factor=1)
    errors=[]; requests=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('request',lambda r: requests.append(r.url))
    page.set_content((ROOT/'index.html').read_text(), wait_until='load')
    page.wait_for_function('window.__stencilboxReady===true')
    page.screenshot(path=str(OUTPUT/'screenshot-desktop.png'),full_page=True)
    print('INITIAL',page.evaluate('({holes:Stencilbox.getModel().holes.length,mesh:Stencilbox.getMesh().validation,ms:window.__lastBuildMs})'))
    page.get_by_role('button',name='3D object',exact=True).click()
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUTPUT/'screenshot-3d.png'))
    print('3D',page.evaluate("({shown:!document.getElementById('glCanvas').hidden,w:document.getElementById('glCanvas').width,h:document.getElementById('glCanvas').height})"))
    page.get_by_role('button',name='On paper',exact=True).click()
    page.screenshot(path=str(OUTPUT/'screenshot-drawing.png'))
    page.get_by_role('button',name='Stencil',exact=True).click()
    page.get_by_role('button',name='Export STL',exact=False).click()
    page.wait_for_timeout(300)
    print('ERRORS',errors)
    print('REQUESTS',requests)
    print('OVERFLOW',page.evaluate('({w:document.documentElement.clientWidth,s:document.documentElement.scrollWidth})'))
    print('JSON-ROUNDTRIP',page.evaluate('(()=>{const p=Stencilbox.getProject();const r=TraceEngine.deserialize(JSON.parse(JSON.stringify(p)));return {holes:r.model.holes.length,match:JSON.stringify(r.model.holes.map(h=>h.poly))===JSON.stringify(Stencilbox.getModel().holes.map(h=>h.poly))}})()'))
    page.set_viewport_size({'width':390,'height':844})
    page.set_content((ROOT/'index.html').read_text(), wait_until='load');page.wait_for_function('window.__stencilboxReady===true');page.screenshot(path=str(OUTPUT/'screenshot-mobile.png'))
    print('MOBILE',page.evaluate('({w:document.documentElement.clientWidth,s:document.documentElement.scrollWidth,controls:document.body.classList.contains("controls-collapsed")})'))
    browser.close()
