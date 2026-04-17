from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_generated_docs_are_in_sync():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/generate_reference_docs.py", "--check"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
