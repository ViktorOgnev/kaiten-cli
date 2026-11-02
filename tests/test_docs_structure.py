from __future__ import annotations

from pathlib import Path

from kaiten_cli import __version__


def test_primary_docs_and_archive_layout_are_explicit():
    root = Path(__file__).resolve().parents[1]

    primary_docs = {
        "README.md",
        "COMMAND_REFERENCE.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "LIVE_VALIDATION.md",
        "API_BEHAVIOR_MATRIX.md",
        "SECURITY.md",
        "docs/USAGE.md",
        "docs/CONTRIBUTING.md",
    }

    for name in primary_docs:
        assert (root / name).is_file(), name

    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert "/docs/archive/" in gitignore
    assert "/PLAN*.md" in gitignore
    assert "/PARITY_CHECKLIST.md" in gitignore
    assert ".env_private" in gitignore
    assert ".DS_Store" in gitignore

    assert not (root / "docs" / "archive" / "README.md").exists()
    assert not (root / "docs" / "archive" / "PLAN.md").exists()
    assert not (root / "docs" / "archive" / "PLAN_EXTERNAL_REVIEW.md").exists()
    assert not (root / "docs" / "archive" / "PLAN_TRIZ_VERIFICATION.md").exists()
    assert not (root / "docs" / "archive" / "PARITY_CHECKLIST.md").exists()
    assert (root / "scripts" / "benchmark_reference_workflows.py").is_file()


def test_primary_docs_expose_current_install_safety_and_live_metadata():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    usage = (root / "docs" / "USAGE.md").read_text(encoding="utf-8")
    reference = (root / "COMMAND_REFERENCE.md").read_text(encoding="utf-8")
    live_validation = (root / "LIVE_VALIDATION.md").read_text(encoding="utf-8")
    behavior_matrix = (root / "API_BEHAVIOR_MATRIX.md").read_text(encoding="utf-8")

    assert f"@v{__version__}" in readme
    assert "@v0.1.29" not in readme
    assert "@v0.1.23" not in readme
    assert "`v0.2.0` — граница совместимости" in usage
    assert "stats.pagination_compatibility" in usage
    assert "KAITEN_CLI_READ_ONLY" in readme
    assert "KAITEN_CLI_UPDATE_CHECK" in readme
    assert "--no-update-check" in readme
    assert "kaiten --locale ru completion install" in readme
    assert "kaiten --locale ru completion status" in readme
    assert "kaiten --locale ru completion uninstall" in readme
    assert "Bash версии 4.4" in readme
    assert "update-check.json" in readme
    assert "http-cache.sqlite3" in usage
    assert "snapshots.sqlite3" in usage
    assert "live suite **не запускался**" in live_validation
    assert "Последняя полная live campaign" in behavior_matrix

    assert readme.split("## ", 1)[1].startswith("Установка\n")
    assert "brew install ViktorOgnev/tap/kaiten-cli" in readme
    assert "pip install kaiten-cli" in readme
    assert "pipx install kaiten-cli" in readme
    assert "uv tool install kaiten-cli" in readme
    assert "## Обновление содержимого документов" not in readme
    assert "--content-mode yjs" not in readme
    assert "docs/USAGE.md#документы-чтение-экспорт-и-обновление" in readme
    assert "docs/CONTRIBUTING.md" in readme
    assert "--content-mode yjs" in usage
    assert "--allow-unsafe-content-replace" in usage
    assert "DOCUMENT_YJS_VERIFICATION.md#temporary-fallback-and-retirement" in usage
    assert "BEGIN GENERATED COMMAND SUMMARY" not in readme
    assert reference.index("## Module Index") < reference.index("## Conventions")
