"""Unit tests for AssetPath and its ImagePath/FontPath/SoundPath subclasses:
the path-construction logic AssetManager builds every asset reference from.
"""
from __future__ import annotations

import os

from pygamine.asset_path import AssetPath, FontPath, ImagePath, SoundPath


def test_full_path_without_folder():
    path = AssetPath(name="logo", base="assets/images")
    assert path.full_path.replace(os.sep, "/").endswith("assets/images/logo.png")


def test_full_path_with_folder():
    path = AssetPath(name="play", folder="buttons", base="assets/images")
    assert path.full_path.replace(os.sep, "/").endswith("assets/images/buttons/play.png")


def test_full_path_is_absolute():
    path = AssetPath(name="logo", base="assets/images")
    assert os.path.isabs(path.full_path)


def test_leading_dot_in_extension_is_stripped():
    path = AssetPath(name="logo", extension=".png", base="assets/images")
    assert path.full_path.endswith("logo.png")
    assert path.extension == "png"


def test_str_and_fspath_both_return_full_path():
    path = AssetPath(name="logo", base="assets/images")
    assert str(path) == path.full_path
    assert os.fspath(path) == path.full_path


# ── subclass defaults ───────────────────────────────────────────────────────


def test_image_path_defaults():
    path = ImagePath(name="logo")
    assert path.extension == "png"
    assert path.full_path.replace(os.sep, "/").endswith("assets/images/logo.png")


def test_font_path_defaults():
    path = FontPath(name="Kenney Future")
    assert path.extension == "ttf"
    assert path.full_path.replace(os.sep, "/").endswith("assets/fonts/Kenney Future.ttf")


def test_sound_path_defaults():
    path = SoundPath(name="click")
    assert path.extension == "ogg"
    assert path.full_path.replace(os.sep, "/").endswith("assets/sounds/click.ogg")


def test_subclass_extension_override():
    path = SoundPath(name="music", extension="mp3")
    assert path.full_path.endswith("music.mp3")
