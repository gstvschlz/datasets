import subprocess
from pathlib import Path

import geostats_datasets

ROOT = Path(__file__).resolve().parents[1]


def test_registry_lists_every_dataset():
    """registry.txt has one zip per dataset folder in git."""
    tracked = subprocess.run(
        ["git", "ls-files", "mining", "oil-gas"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    folders = {path.split("/")[2] for path in tracked}
    assert set(geostats_datasets.list()) == folders, (
        "registry.txt is stale: run `mise run zips` and publish a new data release"
    )
