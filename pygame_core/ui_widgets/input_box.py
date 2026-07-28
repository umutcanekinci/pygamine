from __future__ import annotations

import pygame


class InputBox:
    """A single-line text field: click to focus, type to edit, backspace to
    delete. Grows to fit its content (never shrinks below 200px wide)."""

    def __init__(self, x: int, y: int, w: int, h: int, text: str = '') -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('dodgerblue2')
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, True, self.color)
        self.active = True

    def handle_event(self, event: pygame.event.Event, mouse_position) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(mouse_position)
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

            self.txt_surface = pygame.font.Font(None, 32).render(self.text, True, self.color)

    def update(self) -> None:
        width = max(200, self.txt_surface.get_width() + 10)
        if self.rect.w < width:
            self.rect.w = width

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
