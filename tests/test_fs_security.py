from __future__ import annotations

import os
import stat

import pytest

from kaiten_cli.runtime.fs_security import (
    ensure_private_file,
    open_private_append,
    secure_existing_file,
)


def test_secure_existing_file_rejects_directory_without_changing_mode(tmp_path):
    directory = tmp_path / "not-a-file"
    directory.mkdir(mode=0o755)
    directory.chmod(0o755)

    with pytest.raises(OSError, match="not a regular file"):
        secure_existing_file(directory)

    assert stat.S_IMODE(directory.stat().st_mode) == 0o755


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO is not supported")
def test_ensure_private_file_rejects_fifo_without_changing_mode(tmp_path):
    fifo = tmp_path / "not-a-file"
    os.mkfifo(fifo, mode=0o644)
    fifo.chmod(0o644)

    with pytest.raises(OSError, match="not a regular file"):
        ensure_private_file(fifo)

    assert stat.S_IMODE(fifo.stat().st_mode) == 0o644


def test_open_private_append_rejects_final_symlink(tmp_path):
    target = tmp_path / "target.jsonl"
    target.write_text("keep\n", encoding="utf-8")
    link = tmp_path / "trace.jsonl"
    link.symlink_to(target)

    with pytest.raises(OSError, match="symlinked private file"):
        with open_private_append(link) as stream:
            stream.write("secret\n")

    assert target.read_text(encoding="utf-8") == "keep\n"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO is not supported")
def test_open_private_append_rejects_fifo_without_blocking(tmp_path):
    fifo = tmp_path / "trace.jsonl"
    os.mkfifo(fifo, mode=0o600)

    with pytest.raises(OSError):
        with open_private_append(fifo) as stream:
            stream.write("secret\n")
