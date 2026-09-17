#!/usr/bin/env python3
"""Check the single-file app and repository assets using only the Python standard library."""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class RuntimeAssets(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.external: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        targets = []
        if tag in {'script', 'img', 'iframe', 'audio', 'video', 'source'}:
            targets.append(values.get('src'))
        if tag == 'link' and values.get('rel') in {'stylesheet', 'preload', 'modulepreload'}:
            targets.append(values.get('href'))
        self.external.extend(v for v in targets if v and not v.startswith('data:'))

def main() -> int:
    errors: list[str] = []
    required = [
        'index.html', 'VERSION', 'README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
        'CONTRIBUTING.md', 'SECURITY.md', '.nojekyll', '.gitignore', '.gitattributes',
        '.editorconfig', '.nvmrc', '.python-version', 'package.json', 'requirements-dev.txt',
        'src/index.template.html', 'src/engine.js', 'src/viewer.js', 'src/app.js',
        'src/style.css', 'vendor/earcut.js', 'vendor/EARCUT-LICENSE.txt',
        '.github/workflows/ci.yml', '.github/workflows/pages.yml',
        '.github/ISSUE_TEMPLATE/bug_report.yml', '.github/ISSUE_TEMPLATE/feature_request.yml',
        '.github/pull_request_template.md', '.github/dependabot.yml',
        'docs/ARCHITECTURE.md', 'docs/TESTING.md', 'docs/DEPLOYMENT.md', 'docs/DEVELOPMENT.md',
        'tools/check_repo.py', 'tools/package_release.py',
    ]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f'Missing required file: {name}')
    if errors:
        print('\n'.join(errors))
        return 1
    spec = importlib.util.spec_from_file_location('stencilbox_build', ROOT / 'build.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('Cannot load build.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    payload = (ROOT / 'index.html').read_bytes()
    if payload != builder.render().encode('utf-8'):
        errors.append('index.html differs from source; run python3 build.py')
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        errors.append('VERSION must be a three-part version')
    metadata = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
    if metadata.get('version') != version:
        errors.append('package.json and VERSION do not agree')
    engine = (ROOT / 'src/engine.js').read_text(encoding='utf-8')
    if not re.search(r"VERSION\s*=\s*['\"]" + re.escape(version) + r"['\"]", engine):
        errors.append('Engine version and VERSION do not agree')
    html = payload.decode('utf-8')
    parser = RuntimeAssets()
    parser.feed(html)
    if parser.external:
        errors.append(f'External runtime assets: {parser.external}')
    if re.search(r'/\*__(CSS|VENDOR|ENGINE|VIEWER|APP)__\*/', html):
        errors.append('Unexpanded build marker in index.html')
    if 'Copyright (c) 2016, Mapbox' not in html:
        errors.append('Embedded vendor copyright is missing')
    for family in ['scatter', 'grid', 'honeycomb', 'triangles', 'voronoi', 'radial', 'waves', 'weave']:
        for suffix in ['json', 'stl', 'svg']:
            path = ROOT / 'examples' / f'{family}-study.{suffix}'
            if not path.is_file() or not path.stat().st_size:
                errors.append(f'Missing or empty example: {path.name}')
        project = ROOT / 'examples' / f'{family}-study.json'
        if project.is_file():
            data = json.loads(project.read_text(encoding='utf-8'))
            if data.get('generatorVersion') != version or data.get('units') != 'mm':
                errors.append(f'Example version or units mismatch: {project.name}')
    local_links = 0
    for doc in list(ROOT.glob('*.md')) + list((ROOT / 'docs').glob('*.md')):
        text = doc.read_text(encoding='utf-8')
        for match in re.finditer(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)', text):
            target = match.group(1).strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (doc.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                errors.append(f'Broken link in {doc.relative_to(ROOT)}: {target}')
            local_links += 1
    report = {
        'suite': 'STENCILBOX repository checks', 'version': version, 'passed': not errors,
        'requiredFiles': len(required), 'localDocumentationLinks': local_links,
        'externalRuntimeAssets': parser.external,
        'indexSha256': hashlib.sha256(payload).hexdigest(), 'errors': errors,
    }
    out = ROOT / 'artifacts/test-results'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'repository-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
