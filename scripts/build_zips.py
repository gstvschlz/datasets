"""Build dist/zips/<group>/<dataset>.zip for each release group in releases/*.json.

Each zip holds one dataset folder exactly as stored in git (LF line endings), with fixed
timestamps so that rebuilding unchanged data gives byte-identical zips. A group's
"untracked" lists files too big for git, by dataset; they are read from the dataset folder,
where the dataset's make.py writes them.
"""

import json
import shutil
import zipfile

from make_registry import ROOT, blobs

files = {}
for path, data in blobs():
    files.setdefault(path.split("/")[2], []).append((path, data))

for record in sorted((ROOT / "releases").glob("*.json")):
    out = ROOT / "dist" / "zips" / record.stem
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(record.read_text(encoding="utf-8"))
    for name in spec["datasets"]:
        if name not in files:
            raise SystemExit(f"{record.name}: no dataset {name!r} in git")
        folder = "/".join(files[name][0][0].split("/")[:3])
        with zipfile.ZipFile(out / f"{name}.zip", "w") as archive:
            for path, data in files[name]:
                relative = path.split("/", 2)[2]  # strip <domain>/<2d|3d>/
                info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
            for file in spec.get("untracked", {}).get(name, []):
                source = ROOT / folder / file
                if not source.exists():
                    raise SystemExit(f"{record.name}: {source} missing; run {folder}/make.py first")
                info = zipfile.ZipInfo(f"{name}/{file}", (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                with open(source, "rb") as src, archive.open(info, "w", force_zip64=True) as dst:
                    shutil.copyfileobj(src, dst, 1 << 24)
        print(out / f"{name}.zip")
