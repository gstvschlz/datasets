"""Build dist/zips/<dataset>.zip for every dataset and write the package registry.

Each zip holds one dataset folder as stored in git (LF line endings, as GitHub serves them),
plus the files too big for git listed in UNTRACKED, which the dataset's make.py writes.
Fixed timestamps make rebuilds of unchanged data byte-identical. Publish the zips with
`gh release create data-vX.Y.Z dist/zips/*.zip`, then set DATA_RELEASE in the package.
"""

import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "zips"
REGISTRY = ROOT / "src" / "geostats_datasets" / "registry.txt"
UNTRACKED = {
    "f3-survey": [
        "seismic.sgy",
        "horizons.csv",
        "faults.csv",
        "wells.csv",
        "logs.csv",
        "tops.csv",
        "checkshots.csv",
    ],
}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def entry(name):
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


folders = {}
for line in git("ls-files", "-s", "-z", "mining", "oil-gas").decode().split("\0"):
    if line:
        meta, path = line.split("\t", 1)
        folders.setdefault("/".join(path.split("/")[:3]), []).append((path, meta.split()[1]))

OUT.mkdir(parents=True, exist_ok=True)
registry = []
for folder, files in sorted(folders.items(), key=lambda item: item[0].rsplit("/", 1)[1]):
    name = folder.rsplit("/", 1)[1]
    target = OUT / f"{name}.zip"
    with zipfile.ZipFile(target, "w") as archive:
        for path, blob in files:
            archive.writestr(entry(path.split("/", 2)[2]), git("cat-file", "blob", blob))
        for file in UNTRACKED.get(name, []):
            source = ROOT / folder / file
            if not source.exists():
                raise SystemExit(f"{source} is missing: run {folder}/make.py first")
            with (
                open(source, "rb") as src,
                archive.open(entry(f"{name}/{file}"), "w", force_zip64=True) as dst,
            ):
                shutil.copyfileobj(src, dst, 1 << 24)
    registry.append(f"{name}.zip {hashlib.sha256(target.read_bytes()).hexdigest()}\n")
    print(target)
REGISTRY.write_text("".join(registry), newline="\n")
