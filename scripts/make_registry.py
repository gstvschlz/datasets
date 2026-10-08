"""Write src/geostats_datasets/registry.txt: each dataset file staged in git and its sha256.

Hashes are taken from the git blobs (LF line endings, as GitHub serves them), not from the
checkout, which may have CRLF. Stage data changes with `git add` before running this.
With --check, exit 1 instead of writing if the registry is out of date.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "geostats_datasets" / "registry.txt"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def blobs():
    """(path, bytes) of every dataset file in the git index."""
    for line in git("ls-files", "-s", "-z", "mining", "oil-gas").decode().split("\0"):
        if line:
            meta, path = line.split("\t", 1)
            yield path, git("cat-file", "blob", meta.split()[1])


def registry():
    return "".join(f"{path} {hashlib.sha256(data).hexdigest()}\n" for path, data in blobs())


if __name__ == "__main__":
    text = registry()
    if "--check" in sys.argv:
        sys.exit(REGISTRY.read_text() != text)
    REGISTRY.write_text(text, newline="\n")
