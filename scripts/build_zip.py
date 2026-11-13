#!/usr/bin/env python3
"""Build the upload package for Perplexity (Plugins -> Add custom -> Upload plugin or skill).

Runs scripts/validate.py first, then writes dist/wapliss-whatsapp-<version>.zip
with plugin.json at the root of the archive, as Perplexity requires.
Created by netdigitaltech.

  python3 scripts/build_zip.py
"""
import json, pathlib, subprocess, sys, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE = ["plugin.json", "mcp.json", "README.md", "LICENSE", "CHANGELOG.md", "assets", "skills"]

if subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")]).returncode != 0:
    sys.exit("validate.py failed: fix the errors before building the package")

manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
out = ROOT / "dist" / f"{manifest['name']}-{manifest['version']}.zip"
out.parent.mkdir(exist_ok=True)
files = []
for item in PACKAGE:
    p = ROOT / item
    files += [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file())
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, f.relative_to(ROOT).as_posix())
with zipfile.ZipFile(out) as z:
    names = z.namelist()
assert "plugin.json" in names and "mcp.json" in names, "plugin.json and mcp.json must be at the archive root"
print(f"\nBuilt {out.relative_to(ROOT)}: {len(names)} files, {out.stat().st_size} bytes")
