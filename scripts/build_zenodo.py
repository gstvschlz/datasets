"""Build dist/zenodo/<record>/<dataset>.zip for each Zenodo record in zenodo/*.json.

Each zip holds one dataset folder exactly as stored in git (LF line endings), with fixed
timestamps so that rebuilding unchanged data gives byte-identical zips.
"""

import json
import zipfile

from make_registry import ROOT, blobs

files = {}
for path, data in blobs():
    files.setdefault(path.split("/")[2], []).append((path, data))

for record in sorted((ROOT / "zenodo").glob("*.json")):
    out = ROOT / "dist" / "zenodo" / record.stem
    out.mkdir(parents=True, exist_ok=True)
    for name in json.loads(record.read_text(encoding="utf-8"))["datasets"]:
        if name not in files:
            raise SystemExit(f"{record.name}: no dataset {name!r} in git")
        with zipfile.ZipFile(out / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for path, data in files[name]:
                relative = path.split("/", 2)[2]  # strip <domain>/<2d|3d>/
                archive.writestr(zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0)), data)
        print(out / f"{name}.zip")
