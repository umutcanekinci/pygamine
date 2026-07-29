"""Filesystem anchors that work both from source and inside a PyInstaller
bundle.

A frozen game typically loads assets/config with paths relative to the
current working directory, which only holds when the process runs from the
project root. When PyInstaller freezes the app, data files bundled via the
spec's ``datas`` are unpacked next to the executable (onedir) or extracted
to a temp dir (onefile); either way their location is exposed as
``sys._MEIPASS``. A host project's entry point chdirs into
:func:`resource_root` at startup so its existing cwd-relative paths stay
valid in both modes; anything that must resolve a bundled path without
relying on the cwd uses :func:`resource_path` instead.

Assumes the standard submodule layout, ``<project_root>/src/pygamine/`` --
:func:`resource_root` walks up from this file's location, so a host project
vendoring pygamine somewhere else needs its own variant instead.
"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    """Directory that contains the bundled ``assets/`` (and similar) trees.

    Frozen: the PyInstaller extraction dir. From source: the project root
    two levels up from ``src/pygamine/pygamine/paths.py``.
    """
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle is not None:
        return Path(bundle)
    return Path(__file__).resolve().parents[3]


def resource_path(*parts: str) -> Path:
    """Absolute path to a bundled resource, e.g. ``resource_path("config", "towers.yaml")``."""
    return resource_root().joinpath(*parts)
