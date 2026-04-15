from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from kaiten_cli import __version__
from kaiten_cli.app import cli


def test_cli_version_option_reports_package_version(runner):
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output
    assert "kaiten" in result.output


def test_python_module_entrypoint_help():
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    src_path = str(root / "src")
    env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"

    result = subprocess.run(
        [sys.executable, "-m", "kaiten_cli", "--help"],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "search-tools" in result.stdout


def test_python_module_entrypoint_version():
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    src_path = str(root / "src")
    env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"

    result = subprocess.run(
        [sys.executable, "-m", "kaiten_cli", "--version"],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert __version__ in result.stdout
