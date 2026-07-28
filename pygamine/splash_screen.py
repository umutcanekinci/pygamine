from __future__ import annotations

import os
from typing import Union

import pygame

PathArg = Union[str, "os.PathLike[str]"]


class SplashScreen:
    """Displays a sequence of images, each with a fade-in then hold.

    Advances to the next image automatically when fade+hold elapses, or
    immediately on any mouse click or key press (except ESC, which is
    handled by the caller).  When the last image is done, is_done = True.
    """

    def __init__(self, image_paths: list[PathArg], fade_ms: int = 1500, hold_ms: int = 1000) -> None:
        self._images         = [pygame.image.load(p).convert_alpha() for p in image_paths]
        self._fade_ms        = fade_ms
        self._hold_ms        = hold_ms
        self._index          = 0
        self._current_alpha  = 0
        self._start_time: int | None = None
        self.is_done         = False

    def run(self, surface: pygame.Surface, clock: pygame.time.Clock, fps: int) -> None:
        self._fit_images(surface.get_size())
        self._start_time = pygame.time.get_ticks()
        while not self.is_done:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                self.handle_event(event)
            self.update()
            self.draw(surface)
            pygame.display.update()

    def _fit_images(self, target_size: tuple[int, int]) -> None:
        tw, th = target_size
        fitted = []
        for img in self._images:
            iw, ih = img.get_size()
            scale = min(tw / iw, th / ih)
            new_size = (int(iw * scale), int(ih * scale))
            fitted.append(pygame.transform.smoothscale(img, new_size))
        self._images = fitted

    def start(self) -> None:
        self._start_time = pygame.time.get_ticks()

    def advance(self) -> None:
        if self._index < len(self._images) - 1:
            self._index     += 1
            self._start_time = pygame.time.get_ticks()
            self._current_alpha = 0
        else:
            self.is_done = True

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.advance()
        elif event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE:
            self.advance()

    def update(self) -> None:
        if self.is_done or self._start_time is None:
            return

        elapsed = pygame.time.get_ticks() - self._start_time

        if elapsed >= self._fade_ms + self._hold_ms:
            self.advance()
            return

        self._current_alpha = (
            255 if elapsed >= self._fade_ms
            else int(255 * elapsed / self._fade_ms)
        )

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_done:
            return
        surface.fill((0, 0, 0))
        frame = self._images[self._index].copy()
        frame.fill((255, 255, 255, self._current_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        rect = frame.get_rect(center=surface.get_rect().center)
        surface.blit(frame, rect)
