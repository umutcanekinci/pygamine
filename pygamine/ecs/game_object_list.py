from __future__ import annotations

import pygame

from pygamine.ecs._dispatch import dispatch_draw, dispatch_handle_event, dispatch_update


class GameObjectList(list):
    def __init__(self) -> None:
        super().__init__()

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        dispatch_handle_event(self, event, mouse_position)

    def update(self) -> None:
        dispatch_update(self)

    def draw(self, surface) -> None:
        dispatch_draw(self, surface)
