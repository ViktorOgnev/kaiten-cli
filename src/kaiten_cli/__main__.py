"""Module entrypoint for `python -m kaiten_cli`."""

from __future__ import annotations

from kaiten_cli.app import main


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
