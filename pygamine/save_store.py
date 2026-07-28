"""JSON-backed key-value persistence for settings and game saves.

Mirrors Database's `databases/<name>.db` (cwd-relative, auto-creating
folder) convention but for simple, human-readable JSON blobs instead of
SQL -- settings and save-game data are small, don't need relational
queries, and benefit from being easy to inspect/hand-edit for support.
Writes are atomic (temp file + os.replace) so a crash or power loss
mid-write can't corrupt the store.

One class serves both use cases -- a project typically keeps two named
stores, e.g. `SaveStore("settings")` and `SaveStore("save")`, both under
the same `saves/` folder.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class SaveStore:
    def __init__(self, name: str, directory: str = "saves") -> None:
        self.name = name
        self.directory = Path(directory)
        self.path = self.directory / f"{name}.json"

    def load(self, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """Read the stored data. Returns a copy of `default` (or {}) if
        the file doesn't exist yet, or is unreadable/corrupt."""
        if not self.path.exists():
            return dict(default) if default else {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return dict(default) if default else {}
        return data if isinstance(data, dict) else (dict(default) if default else {})

    def save(self, data: dict[str, Any]) -> None:
        """Atomically overwrite the store with `data` (a full replace,
        not a merge -- see `update()` for merging)."""
        self.directory.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.path)

    def update(self, **changes: Any) -> dict[str, Any]:
        """Merge `changes` into the existing stored data and persist."""
        data = self.load()
        data.update(changes)
        self.save(data)
        return data

    def get(self, key: str, default: Any = None) -> Any:
        return self.load().get(key, default)

    def exists(self) -> bool:
        return self.path.exists()

    def delete(self) -> None:
        """Remove the store entirely (e.g. clearing a game-over save so
        "Continue" doesn't offer to resume a run that's already lost).
        A no-op if there's nothing to delete."""
        self.path.unlink(missing_ok=True)
