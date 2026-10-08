import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_registry_matches_tracked_files():
    """Every dataset file in git is in registry.txt with its current sha256."""
    check = subprocess.run(
        [sys.executable, ROOT / "scripts" / "make_registry.py", "--check"], check=False
    )
    assert check.returncode == 0, "registry.txt is stale: run `mise run registry`"
