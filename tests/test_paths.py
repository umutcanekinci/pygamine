"""Unit tests for pygamine.assets.paths: resource_root()/resource_path(), the
frozen-vs-source filesystem anchor host projects chdir into at startup.
"""
from __future__ import annotations

import sys
from pathlib import Path

from pygamine.assets.paths import resource_path, resource_root


def test_resource_root_uses_meipass_when_frozen(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_root() == tmp_path


def test_resource_root_falls_back_to_project_root_when_not_frozen(monkeypatch):
    """Deliberately not just `root.is_dir()`: every ancestor of this file is
    itself a real, existing directory, so that assertion alone would pass
    even at the wrong depth (e.g. one level short, landing on `src/pygamine`
    instead of the true project root) -- which is exactly the regression
    this caught when paths.py moved into assets/ and the parents[N] index
    needed to grow by one but didn't, immediately at the next opportunity.
    Instead, verify resource_root() actually contains this file at its
    known, fixed relative path (src/pygamine/pygamine/assets/paths.py)."""
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    root = resource_root()
    this_file = Path(__file__).resolve().parents[1] / "pygamine" / "assets" / "paths.py"
    expected = root / "src" / "pygamine" / "pygamine" / "assets" / "paths.py"
    assert expected.resolve() == this_file.resolve()


def test_resource_path_joins_onto_resource_root(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path("config", "towers.yaml") == tmp_path / "config" / "towers.yaml"


def test_resource_path_with_no_parts_equals_resource_root(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path() == Path(tmp_path)
