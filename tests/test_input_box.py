"""Unit tests for InputBox: a plain text-entry widget (click to focus, type,
backspace, auto-widening)."""
from __future__ import annotations

import pygame

from pygame_core.ui_widgets.input_box import InputBox


def test_construction_sets_rect_text_and_defaults():
    box = InputBox(10, 20, 200, 32, text="hi")
    assert box.rect.topleft == (10, 20)
    assert box.rect.size == (200, 32)
    assert box.text == "hi"
    assert box.active is True
    assert box.color == pygame.Color("dodgerblue2")


def test_construction_defaults_to_empty_text():
    box = InputBox(0, 0, 200, 32)
    assert box.text == ""


# ── handle_event: focus via click ──────────────────────────────────────


def test_click_inside_activates_and_uses_active_color():
    box = InputBox(0, 0, 200, 32)
    box.active = False
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10))

    box.handle_event(event, (10, 10))

    assert box.active is True
    assert box.color == pygame.Color("dodgerblue2")


def test_click_outside_deactivates_and_uses_inactive_color():
    box = InputBox(0, 0, 200, 32)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(500, 500))

    box.handle_event(event, (500, 500))

    assert box.active is False
    assert box.color == pygame.Color("lightskyblue3")


# ── handle_event: typing ────────────────────────────────────────────────


def test_keydown_while_active_appends_character():
    box = InputBox(0, 0, 200, 32, text="ab")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, unicode="c")

    box.handle_event(event, (0, 0))

    assert box.text == "abc"


def test_backspace_removes_last_character():
    box = InputBox(0, 0, 200, 32, text="abc")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode="")

    box.handle_event(event, (0, 0))

    assert box.text == "ab"


def test_backspace_on_empty_text_is_a_no_op():
    box = InputBox(0, 0, 200, 32, text="")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode="")

    box.handle_event(event, (0, 0))

    assert box.text == ""


def test_keydown_while_inactive_is_ignored():
    box = InputBox(0, 0, 200, 32, text="ab")
    box.active = False
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, unicode="c")

    box.handle_event(event, (0, 0))

    assert box.text == "ab"


def test_unrelated_event_type_is_ignored():
    box = InputBox(0, 0, 200, 32, text="ab")
    event = pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0))

    box.handle_event(event, (0, 0))

    assert box.text == "ab"
    assert box.active is True


# ── update: auto-widen ──────────────────────────────────────────────────


def test_update_widens_rect_to_fit_long_text():
    box = InputBox(0, 0, 50, 32, text="a very long string of text indeed")
    box.update()
    assert box.rect.w == box.txt_surface.get_width() + 10


def test_update_never_shrinks_rect_below_current_width():
    box = InputBox(0, 0, 500, 32, text="hi")
    box.update()
    assert box.rect.w == 500  # short text, but rect never shrinks


def test_update_never_goes_below_the_200px_floor():
    box = InputBox(0, 0, 50, 32, text="")
    box.update()
    assert box.rect.w == 200


# ── draw ──────────────────────────────────────────────────────────────


def test_draw_paints_a_border_in_the_current_color():
    box = InputBox(10, 10, 100, 40)
    surface = pygame.Surface((200, 200))
    surface.fill((0, 0, 0))

    box.draw(surface)

    # a 2px border is drawn at the rect's edge; check a point on the top edge
    assert surface.get_at((50, 10)) == box.color
    # and the interior (away from border and text) stays untouched
    assert surface.get_at((50, 30)) == (0, 0, 0, 255)
