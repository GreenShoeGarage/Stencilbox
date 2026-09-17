#!/usr/bin/env python3
"""Optional source packer; opening the checked-in index.html needs no build."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "CSS": "src/style.css", "VENDOR": "vendor/earcut.js",
    "ENGINE": "src/engine.js", "VIEWER": "src/viewer.js", "APP": "src/app.js",
}

def render() -> str:
    html = (ROOT / "src/index.template.html").read_text(encoding="utf-8")
    for token, filename in SOURCES.items():
        marker = f"/*__{token}__*/"
        if html.count(marker) != 1:
            raise ValueError(f"Expected exactly one {marker} in the template")
        html = html.replace(marker, (ROOT / filename).read_text(encoding="utf-8"))
    return html

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if output differs; never write files")
    parser.add_argument("--output", type=Path, default=ROOT / "index.html", help="Alternate output path")
    args = parser.parse_args()
    try:
        data = render().encode("utf-8")
        if args.check:
            if not args.output.is_file() or args.output.read_bytes() != data:
                print("Packaged HTML is out of date. Run: python3 build.py", file=sys.stderr)
                return 1
            print(f"PASS: {args.output.name} matches the editable sources ({len(data):,} bytes)")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(data)
            print(f"Built {args.output.name} ({len(data):,} bytes)")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
