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
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    root = resource_root()
    # From source, three levels up from this package's own paths.py
    # (pygamine/paths.py -> pygamine/ -> src/pygamine/ -> project root)
    # is wherever pygamine itself is checked out, not necessarily a host
    # game project -- just assert it's a real, existing directory, since
    # the exact location depends on how this test suite is run.
    assert root.is_dir()


def test_resource_path_joins_onto_resource_root(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path("config", "towers.yaml") == tmp_path / "config" / "towers.yaml"


def test_resource_path_with_no_parts_equals_resource_root(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path() == Path(tmp_path)
