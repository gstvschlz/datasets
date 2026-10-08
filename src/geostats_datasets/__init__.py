"""Download mining and oil & gas geostatistics datasets by name and cache them locally."""

from pathlib import Path

import pooch

__version__ = "0.1.0.dev0"

# Released versions read the files of their own git tag; dev versions read main.
_REF = "main" if "dev" in __version__ else f"v{__version__}"

_DATA = pooch.create(
    path=pooch.os_cache("geostats-datasets"),
    base_url=f"https://raw.githubusercontent.com/gstvschlz/datasets/{_REF}/",
    env="GEOSTATS_DATASETS_DIR",
)
_DATA.load_registry(Path(__file__).with_name("registry.txt"))


def list():
    """Names of all datasets, e.g. 'walker-lake'."""
    return sorted({path.split("/")[2] for path in _DATA.registry})


def fetch(name, file=None):
    """Download a dataset, or one of its files, and return its local path.

    Files are checked against their sha256 and downloaded only once.
    """
    files = [path for path in _DATA.registry if path.split("/")[2] == name]
    if not files:
        raise ValueError(f"Unknown dataset {name!r}; see geostats_datasets.list() for names.")
    folder = "/".join(files[0].split("/")[:3])
    if file is not None:
        path = f"{folder}/{file}"
        if path not in _DATA.registry:
            names = ", ".join(sorted(p.removeprefix(folder + "/") for p in files))
            raise ValueError(f"{name!r} has no file {file!r}; its files are: {names}.")
        return Path(_DATA.fetch(path))
    for path in files:
        _DATA.fetch(path)
    return Path(_DATA.abspath) / folder
