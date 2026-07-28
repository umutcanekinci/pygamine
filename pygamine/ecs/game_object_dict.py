from __future__ import annotations

import pygame
from typing import Any


class GameObjectDict:
    def __init__(self) -> None:
        self._objects: dict[str, Any] = {}

    def __getitem__(self, key: str) -> Any:
        return self._objects[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._objects[key] = value

    def __contains__(self, key: object) -> bool:
        return key in self._objects

    def values(self):
        return self._objects.values()

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        for obj in self._objects.values():
            if not hasattr(obj, "handle_event"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.handle_event(event, mouse_position)

    def update(self) -> None:
        for obj in self._objects.values():
            if not hasattr(obj, "update"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.update()

    def draw(self, surface) -> None:
        for obj in self._objects.values():
            if not hasattr(obj, "draw"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.draw(surface)