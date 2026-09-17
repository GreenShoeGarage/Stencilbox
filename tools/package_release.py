#!/usr/bin/env python3
"""Create a reproducible repository ZIP and portable HTML; never publish anything."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    'index.html', 'README.md', 'VERSION', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
    'CHANGELOG.md', 'CONTRIBUTING.md', 'SECURITY.md', 'build.py', 'package.json',
    'requirements-dev.txt', '.gitignore', '.gitattributes', '.editorconfig',
    '.nojekyll', '.nvmrc', '.python-version',
}
DIRECTORIES = {'.github', 'src', 'vendor', 'examples', 'docs', 'tests', 'tools'}
EXCLUDED_PARTS = {'.git', '__pycache__', 'node_modules', '.venv', '.pytest_cache'}

def files_for_release() -> list[Path]:
    files: list[Path] = []
    for name in sorted(ROOT_FILES):
        candidate = ROOT / name
        if candidate.is_symlink() or not candidate.is_file():
            raise ValueError(f'Required release file missing or a symlink: {name}')
        files.append(candidate)
    for name in sorted(DIRECTORIES):
        folder = ROOT / name
        if folder.is_symlink() or not folder.is_dir():
            raise ValueError(f'Required directory missing or a symlink: {name}')
        for candidate in sorted(folder.rglob('*')):
            relative = candidate.relative_to(ROOT)
            if set(relative.parts) & EXCLUDED_PARTS:
                continue
            if candidate.name == '.DS_Store' or candidate.name.startswith('.env') or candidate.suffix in {'.pyc', '.pyo', '.log'}:
                continue
            if candidate.is_symlink():
                raise ValueError(f'Refusing symlink: {relative}')
            if candidate.is_file():
                files.append(candidate)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    try:
        subprocess.run([sys.executable, str(ROOT / 'build.py'), '--check'], check=True)
        version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        if not re.fullmatch(r'\d+\.\d+\.\d+', version):
            raise ValueError('Invalid VERSION')
        files = files_for_release()
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        archive = output / f'stencilbox-v{version}-repo.zip'
        portable = output / f'stencilbox-v{version}.html'
        temporary = archive.with_suffix('.zip.tmp')
        with ZipFile(temporary, 'w', compression=ZIP_DEFLATED, compresslevel=9) as zf:
            for path in files:
                info = ZipInfo('stencilbox/' + path.relative_to(ROOT).as_posix(), (1980, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                zf.writestr(info, path.read_bytes(), compresslevel=9)
        with ZipFile(temporary) as zf:
            bad = zf.testzip()
            if bad:
                raise ValueError(f'ZIP integrity failure: {bad}')
        temporary.replace(archive)
        portable.write_bytes((ROOT / 'index.html').read_bytes())
        checksums = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in [archive, portable])
        (output / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8', newline='\n')
        print(f'Created {archive.name}: {len(files)} files, {archive.stat().st_size:,} bytes')
        print(f'Created {portable.name} and SHA256SUMS.txt')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'Packaging failed: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
