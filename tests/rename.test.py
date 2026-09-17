"""Rebrand and same-origin storage-copy tests; uses a storage adapter, not native permissions."""
from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get('STENCILBOX_TEST_OUTPUT', ROOT / 'artifacts/test-results'))
OUTPUT.mkdir(parents=True, exist_ok=True)
HTML = (ROOT / 'index.html').read_text()
LEGACY = json.loads((ROOT / 'tests/fixtures/legacy/voronoi-study.json').read_text())
checks, errors = [], []

def check(name, condition):
    assert condition, name
    checks.append(name)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'), headless=True, args=['--no-sandbox','--disable-webgl'])
    def load(data, reject_writes=False):
        page = browser.new_page(viewport={'width':1440,'height':1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.evaluate('''({data,rejectWrites})=>{
          const map=new Map(Object.entries(data));
          Object.defineProperty(window,'localStorage',{value:{
            getItem:k=>map.has(k)?map.get(k):null,
            setItem:(k,v)=>{if(rejectWrites)throw new Error('Storage unavailable');map.set(k,String(v));},
            removeItem:k=>map.delete(k)
          }});
          window.__blobs=[];
          URL.createObjectURL=blob=>{window.__blobs.push(blob);return 'blob:stencilbox-test';};
          URL.revokeObjectURL=()=>{};
          HTMLAnchorElement.prototype.click=function(){};
          window.print=()=>{window.__printCalled=true;};
        }''', {'data':data,'rejectWrites':reject_writes})
        page.set_content(HTML)
        page.wait_for_function('window.__stencilboxReady === true')
        page.wait_for_timeout(650)
        return page
    snapshot={'settings':LEGACY['settings'],'edits':LEGACY['edits'],'metrics':{'holes':len(LEGACY['geometry']['openings']),'openPercent':20,'volume':10,'web':2}}
    old={
        'traceform.project.v1': json.dumps(LEGACY),
        'traceform.preferences.v1': json.dumps({'advanced':True,'theme':'light'}),
        'traceform.shelf.v1': json.dumps([snapshot]),
        'traceform.baseline.v1': json.dumps(snapshot),
    }
    page=load(old)
    check('Page title uses STENCILBOX',page.title().startswith('STENCILBOX'))
    check('Visible app brand uses STENCILBOX',page.locator('.brand').inner_text().startswith('STENCILBOX'))
    check('Legacy geometry restores exactly',page.evaluate('Stencilbox.getProject().geometry')==LEGACY['geometry'])
    check('Legacy user project title is preserved',page.evaluate('Stencilbox.getSettings().name')==LEGACY['settings']['name'])
    check('Legacy preferences restore',page.evaluate('document.body.classList.contains("advanced") && document.documentElement.dataset.theme==="light"'))
    for key,value in old.items():
        check(f'Original {key} remains untouched',page.evaluate('(k)=>localStorage.getItem(k)',key)==value)
        check(f'New {key.replace("traceform","stencilbox")} is populated',page.evaluate('(k)=>localStorage.getItem(k)!==null',key.replace('traceform','stencilbox')))
    check('New autosave format is STENCILBOX',page.evaluate('JSON.parse(localStorage.getItem("stencilbox.project.v1")).format')=='stencilbox-project')
    check('Legacy hooks remain available',page.evaluate('window.Traceform===window.Stencilbox && window.__traceformReady===true'))
    check('New JSON exports use STENCILBOX',page.evaluate('Stencilbox.getProject().format')=='stencilbox-project')
    page.locator('#shelfBtn').click()
    check('Legacy shelf is shown',page.locator('.shelf-card').count()==1)
    check('Legacy baseline is shown','Baseline:' in page.locator('#baselineInfo').inner_text())
    page.locator('#shelfDialog [data-close]').click()
    page.locator('#reportBtn').click()
    check('Report uses new brand',page.locator('#printReport').text_content().startswith('STENCILBOX / Stencil record'))
    page.close()
    current={**LEGACY,'format':'stencilbox-project','settings':{**LEGACY['settings'],'name':'Existing STENCILBOX design'}}
    mixed={**old,'stencilbox.project.v1':json.dumps(current),'stencilbox.preferences.v1':json.dumps({'advanced':False,'theme':'contrast'}),'stencilbox.shelf.v1':'[]','stencilbox.baseline.v1':'null'}
    page=load(mixed)
    check('Current project takes precedence',page.evaluate('Stencilbox.getSettings().name')=='Existing STENCILBOX design')
    check('Current preferences take precedence',page.evaluate('!document.body.classList.contains("advanced") && document.documentElement.dataset.theme==="contrast"'))
    page.locator('#shelfBtn').click()
    check('Current empty shelf takes precedence',page.locator('.shelf-card').count()==0)
    check('Current cleared baseline takes precedence','No comparison baseline' in page.locator('#baselineInfo').inner_text())
    page.close()
    page=load(old,reject_writes=True)
    check('Legacy geometry usable when migration writes fail',page.evaluate('Stencilbox.getProject().geometry')==LEGACY['geometry'])
    check('Failed new autosave asks for JSON backup',page.locator('#saveStatus').inner_text()=='Export JSON to save')
    check('Failed write leaves legacy data intact',page.evaluate('localStorage.getItem("traceform.project.v1")')==old['traceform.project.v1'])
    page.close()
    page=load({})
    check('Clean installation saves under new key',page.evaluate('JSON.parse(localStorage.getItem("stencilbox.project.v1")).format')=='stencilbox-project')
    check('Clean installation does not create legacy keys',page.evaluate('localStorage.getItem("traceform.project.v1")===null'))
    page.close()
    check('No browser JavaScript errors',not errors)
    result={'suite':'STENCILBOX rename and storage compatibility','browser':browser.version,'passed':len(checks),'checks':checks,'errors':errors,'limitations':['Storage adapter tests application copy/precedence logic, not browser-native origin permissions.','Different-origin storage cannot be copied; use JSON export/import.','No remote repository or site was changed.']}
    (OUTPUT/'rename-browser-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    browser.close()
