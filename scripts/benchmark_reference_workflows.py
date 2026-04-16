#!/usr/bin/env python3
"""Run reference kaiten-cli workflows from a JSON spec and summarize cost."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


def _load_spec(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("workflows"), list):
        raise SystemExit("Spec must be a JSON object with a workflows array.")
    return payload


def _command_tokens(command: Any) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    if isinstance(command, list) and all(isinstance(item, str) for item in command):
        return list(command)
    raise SystemExit("Each workflow command must be a string or an array of strings.")


def _read_trace_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _summarize_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "commands": len(entries),
        "duration_ms": round(sum(float(entry.get("duration_ms", 0.0)) for entry in entries), 2),
        "http_request_count": sum(int(entry.get("http_request_count", 0)) for entry in entries),
        "retry_count": sum(int(entry.get("retry_count", 0)) for entry in entries),
        "cache_hits": {
            "request": sum(int(entry.get("cache_hits", {}).get("request", 0)) for entry in entries),
            "inflight_dedup": sum(int(entry.get("cache_hits", {}).get("inflight_dedup", 0)) for entry in entries),
            "disk": sum(int(entry.get("cache_hits", {}).get("disk", 0)) for entry in entries),
        },
    }


def _run_workflow(workflow: dict[str, Any], *, workdir: Path) -> dict[str, Any]:
    name = str(workflow.get("name") or "unnamed")
    commands = workflow.get("commands")
    if not isinstance(commands, list) or not commands:
        raise SystemExit(f"Workflow {name!r} must contain a non-empty commands list.")

    extra_env = workflow.get("env") or {}
    if not isinstance(extra_env, dict) or not all(isinstance(key, str) for key in extra_env):
        raise SystemExit(f"Workflow {name!r} env must be an object with string keys.")

    with tempfile.TemporaryDirectory(prefix="kaiten-bench-") as temp_dir:
        trace_path = Path(temp_dir) / "trace.jsonl"
        env = os.environ.copy()
        env.update({key: str(value) for key, value in extra_env.items()})
        env.setdefault("KAITEN_TRACE_FILE", str(trace_path))

        command_results: list[dict[str, Any]] = []
        workflow_started = time.perf_counter()
        for raw_command in commands:
            argv = _command_tokens(raw_command)
            started = time.perf_counter()
            completed = subprocess.run(
                argv,
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            duration_ms = round((time.perf_counter() - started) * 1000.0, 2)
            command_results.append(
                {
                    "argv": argv,
                    "exit_code": completed.returncode,
                    "duration_ms": duration_ms,
                    "stdout_bytes": len(completed.stdout.encode("utf-8")),
                    "stderr_bytes": len(completed.stderr.encode("utf-8")),
                }
            )
        workflow_duration_ms = round((time.perf_counter() - workflow_started) * 1000.0, 2)
        trace_entries = _read_trace_entries(trace_path)
        summary = _summarize_entries(trace_entries)
        summary["wall_time_ms"] = workflow_duration_ms
        summary["stdout_bytes"] = sum(item["stdout_bytes"] for item in command_results)
        summary["stderr_bytes"] = sum(item["stderr_bytes"] for item in command_results)

        return {
            "name": name,
            "commands": command_results,
            "trace": summary,
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run reference kaiten-cli workflows and summarize wall time, trace stats, and output size."
    )
    parser.add_argument("--spec", required=True, help="Path to a JSON spec with workflow definitions.")
    parser.add_argument(
        "--workdir",
        default=".",
        help="Working directory for workflow commands. Defaults to the current directory.",
    )
    args = parser.parse_args()

    spec = _load_spec(Path(args.spec))
    workdir = Path(args.workdir).resolve()
    results = [_run_workflow(workflow, workdir=workdir) for workflow in spec["workflows"]]
    print(json.dumps({"workflows": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
