#!/usr/bin/env python3
"""19 November 2026 in one image.

The image is committed as entry.png; this program only copies it to the
grader's output. Nothing is fetched, and two runs write identical bytes.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
print(f"wrote {OUT / 'entry.png'}")
