#!/usr/bin/env python3
"""make.fun entry runner for bounty news-image-20261119.

Copies the committed editorial illustration (entry.png, which sits beside
this script) into the output directory. Python 3.13 standard library only,
no network access, fully deterministic: the output bytes are always an
exact copy of the source bytes.

Output directory: $MAKEFUN_OUTPUT_DIR, defaulting to /output.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    src = Path(__file__).resolve().parent / "entry.png"

    if not src.is_file():
        print(f"error: source image not found: {src}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)

    data = dst.read_bytes()
    print(f"wrote {dst} ({len(data)} bytes)")
    print(f"sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
