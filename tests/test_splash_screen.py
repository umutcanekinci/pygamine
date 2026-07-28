"""Unit tests for SplashScreen: a fade-in/hold image sequence, advanced by
elapsed time, a click, or a keypress (except Escape, which the run() loop
itself intercepts to bail out early).

Timing is driven through the fake_ticks fixture (patches
pygame.time.get_ticks) for deterministic, instant tests.
"""
from __future__ import annotations

import pygame
import pytest

from pygame_core.splash_screen import SplashScreen


def _save_png(path, size, color):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    pygame.image.save(surf, str(path))


@pytest.fixture
def image_paths(tmp_path):
    pygame.display.set_mode((1, 1))  # convert_alpha() needs a display mode set
    paths = []
    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        path = tmp_path / f"img{i}.png"
        _save_png(path, (20, 10), color)
        paths.append(path)
    return paths


# ── construction ────────────────────────────────────────────────────────


def test_construction_loads_all_images(image_paths):
    splash = SplashScreen(image_paths)
    assert len(splash._images) == 3


def test_construction_defaults():
    splash = SplashScreen([])
    assert splash._fade_ms == 1500
    assert splash._hold_ms == 1000
    assert splash._index == 0
    assert splash._current_alpha == 0
    assert splash._start_time is None
    assert splash.is_done is False


def test_construction_custom_timings(image_paths):
    splash = SplashScreen(image_paths, fade_ms=200, hold_ms=100)
    assert splash._fade_ms == 200
    assert splash._hold_ms == 100


# ── _fit_images ─────────────────────────────────────────────────────


def test_fit_images_scales_down_preserving_aspect_ratio_width_constrained(image_paths):
    """Source is 20x10 (2:1); fitting into a 100x100 target is width-
    constrained (100/20=5 < 100/10=10), so the result uses the smaller
    factor on both axes."""
    splash = SplashScreen(image_paths)
    splash._fit_images((100, 100))
    assert splash._images[0].get_size() == (100, 50)


def test_fit_images_scales_down_preserving_aspect_ratio_height_constrained(image_paths):
    splash = SplashScreen(image_paths)
    splash._fit_images((100, 20))  # 100/20=5 > 20/10=2 -- height-constrained
    assert splash._images[0].get_size() == (40, 20)


# ── start ─────────────────────────────────────────────────────────────


def test_start_sets_start_time(fake_ticks):
    splash = SplashScreen([])
    fake_ticks["t"] = 500
    splash.start()
    assert splash._start_time == 500


# ── advance ─────────────────────────────────────────────────────────


def test_advance_moves_to_the_next_image(image_paths, fake_ticks):
    splash = SplashScreen(image_paths)
    splash._current_alpha = 200
    fake_ticks["t"] = 1000

    splash.advance()

    assert splash._index == 1
    assert splash._start_time == 1000
    assert splash._current_alpha == 0
    assert splash.is_done is False


def test_advance_on_the_last_image_marks_done(image_paths):
    splash = SplashScreen(image_paths)
    splash._index = len(splash._images) - 1

    splash.advance()

    assert splash.is_done is True
    assert splash._index == len(splash._images) - 1  # unchanged


# ── handle_event ────────────────────────────────────────────────────


def test_mousebuttondown_advances(image_paths):
    splash = SplashScreen(image_paths)
    splash.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1))
    assert splash._index == 1


def test_keydown_advances(image_paths):
    splash = SplashScreen(image_paths)
    splash.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert splash._index == 1


def test_escape_key_does_not_advance(image_paths):
    splash = SplashScreen(image_paths)
    splash.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert splash._index == 0


def test_unrelated_event_does_not_advance(image_paths):
    splash = SplashScreen(image_paths)
    splash.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0)))
    assert splash._index == 0


# ── update ──────────────────────────────────────────────────────────


def test_update_is_a_no_op_when_done(image_paths, fake_ticks):
    splash = SplashScreen(image_paths, fade_ms=100, hold_ms=100)
    splash.is_done = True
    splash.start()
    fake_ticks["t"] = 50

    splash.update()

    assert splash._current_alpha == 0


def test_update_is_a_no_op_before_start_is_called(image_paths):
    splash = SplashScreen(image_paths)
    splash.update()  # _start_time is still None
    assert splash._current_alpha == 0


def test_update_computes_partial_fade_alpha(image_paths, fake_ticks):
    splash = SplashScreen(image_paths, fade_ms=100, hold_ms=100)
    fake_ticks["t"] = 0
    splash.start()

    fake_ticks["t"] = 50  # halfway through the fade
    splash.update()

    assert splash._current_alpha == 127  # int(255 * 50 / 100)


def test_update_holds_at_full_alpha_after_fade_completes(image_paths, fake_ticks):
    splash = SplashScreen(image_paths, fade_ms=100, hold_ms=100)
    fake_ticks["t"] = 0
    splash.start()

    fake_ticks["t"] = 150  # fade done, still within the hold window
    splash.update()

    assert splash._current_alpha == 255


def test_update_auto_advances_once_fade_and_hold_elapse(image_paths, fake_ticks):
    splash = SplashScreen(image_paths, fade_ms=100, hold_ms=100)
    fake_ticks["t"] = 0
    splash.start()

    fake_ticks["t"] = 250  # past fade(100) + hold(100)
    splash.update()

    assert splash._index == 1
    assert splash._start_time == 250  # reset by advance()


# ── draw ────────────────────────────────────────────────────────────


def test_draw_is_a_no_op_when_done(image_paths):
    splash = SplashScreen(image_paths)
    splash.is_done = True
    surface = pygame.Surface((20, 20))
    surface.fill((123, 45, 67))

    splash.draw(surface)

    assert surface.get_at((10, 10)) == (123, 45, 67, 255)  # untouched


def test_draw_at_full_alpha_shows_the_frame_unmodified(image_paths):
    splash = SplashScreen(image_paths)
    splash._fit_images((20, 10))
    splash._current_alpha = 255

    surface = pygame.Surface((20, 10))
    splash.draw(surface)

    assert surface.get_at((10, 5)) == (255, 0, 0, 255)  # first image is red


def test_draw_at_zero_alpha_shows_pure_black(image_paths):
    splash = SplashScreen(image_paths)
    splash._fit_images((20, 10))
    splash._current_alpha = 0

    surface = pygame.Surface((20, 10))
    splash.draw(surface)

    assert surface.get_at((10, 5)) == (0, 0, 0, 255)


def test_draw_shows_the_current_index_not_the_first(image_paths):
    splash = SplashScreen(image_paths)
    splash._fit_images((20, 10))
    splash._index = 1  # green
    splash._current_alpha = 255

    surface = pygame.Surface((20, 10))
    splash.draw(surface)

    assert surface.get_at((10, 5)) == (0, 255, 0, 255)


# ── run() ─────────────────────────────────────────────────────────────


def test_run_returns_immediately_on_escape(image_paths, monkeypatch, fake_ticks):
    splash = SplashScreen(image_paths)
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    )
    surface = pygame.Surface((20, 10))

    splash.run(surface, pygame.time.Clock(), fps=0)

    assert splash.is_done is False  # bailed out via `return`, not via completion


def test_run_raises_systemexit_on_quit_event(image_paths, monkeypatch, fake_ticks):
    splash = SplashScreen(image_paths)
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])
    surface = pygame.Surface((20, 10))

    with pytest.raises(SystemExit):
        splash.run(surface, pygame.time.Clock(), fps=0)


def test_run_advances_through_all_images_via_a_click_and_completes(image_paths, monkeypatch, fake_ticks):
    splash = SplashScreen(image_paths)
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)]
    )
    surface = pygame.Surface((20, 10))

    splash.run(surface, pygame.time.Clock(), fps=0)

    assert splash.is_done is True
