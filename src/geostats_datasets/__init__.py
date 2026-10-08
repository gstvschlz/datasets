"""Download mining and oil & gas geostatistics datasets by name and cache them locally."""

import os
import shutil
import zipfile
from pathlib import Path

import pooch

__version__ = "0.1.0"

# The GitHub release holding one <dataset>.zip per dataset.
DATA_RELEASE = "data-v1.0.0"

_DATA = pooch.create(
    path=Path(os.environ.get("GEOSTATS_DATASETS_DIR") or pooch.os_cache("geostats-datasets"))
    / DATA_RELEASE,
    base_url=f"https://github.com/gstvschlz/datasets/releases/download/{DATA_RELEASE}/",
)
_DATA.load_registry(Path(__file__).with_name("registry.txt"))


def list():
    """Names of all datasets, e.g. 'walker-lake'."""
    return sorted(name.removesuffix(".zip") for name in _DATA.registry)


def fetch(name, file=None):
    """Download a dataset and return the local path of its folder, or of one of its files.

    The zip is checked against its sha256, downloaded once and unpacked into the cache.
    """
    if f"{name}.zip" not in _DATA.registry:
        raise ValueError(f"Unknown dataset {name!r}; see geostats_datasets.list() for names.")
    archive = Path(_DATA.fetch(f"{name}.zip"))
    folder = archive.with_suffix("")
    if not folder.exists():
        # Unpack beside the cache and move into place, so an interrupted unpack leaves no folder.
        partial = archive.with_suffix(".partial")
        shutil.rmtree(partial, ignore_errors=True)
        with zipfile.ZipFile(archive) as zipped:
            zipped.extractall(partial)
        (partial / name).rename(folder)
        shutil.rmtree(partial)
    if file is None:
        return folder
    path = folder / file
    if not path.is_file():
        files = sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())
        raise ValueError(f"{name!r} has no file {file!r}; its files are: {', '.join(files)}.")
    return path
