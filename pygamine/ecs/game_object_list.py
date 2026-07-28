from __future__ import annotations

import pygame


class GameObjectList(list):
    def __init__(self) -> None:
        super().__init__()

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        for obj in self:
            if not hasattr(obj, "handle_event"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.handle_event(event, mouse_position)

    def update(self) -> None:
        for obj in self:
            if not hasattr(obj, "update"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.update()

    def draw(self, surface) -> None:
        for obj in self:
            if not hasattr(obj, "draw"): continue
            if hasattr(obj, "active") and not obj.active: continue
            obj.draw(surface)
