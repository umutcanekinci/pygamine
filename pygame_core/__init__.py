"""pygame_core: a shared pygame-ce application/ECS/asset toolkit.

This top-level module re-exports the package's public API so consumers can
write `from pygame_core import Application, GameObject, Camera` instead of
reaching into individual submodules (`pygame_core.ecs.game_object`,
`pygame_core.ecs.components.transform`, ...). Importing from the deeper
paths still works -- this is purely a convenience surface, not a move --
but new code should prefer the shallow form.

Exports are resolved lazily (PEP 562's module `__getattr__`), not imported
eagerly here, on purpose: `asset_manager`/`tilemap` pull in `pyyaml`/
`pytmx`, and not every consumer of this package uses those subsystems (some
projects deliberately skip the YAML-driven AssetManager/panel system and
only depend on the ECS core). Eagerly importing everything at
`import pygame_core` time would force *every* consumer to have *every*
optional dependency installed just to use `Application`/`GameObject`. Each
name below is only actually imported -- and its real dependency touched --
the first time it's accessed.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For type checkers / IDE autocomplete only -- never executed at runtime
    # (see the lazy __getattr__ below for why these aren't real imports).

    # Application / window management
    from pygame_core.application import Application
    from pygame_core.mouse import Mouse
    from pygame_core.camera import Camera
    from pygame_core.debug import Debug
    from pygame_core.splash_screen import SplashScreen

    # ECS core
    from pygame_core.ecs.game_object import GameObject
    from pygame_core.ecs.game_object_dict import GameObjectDict
    from pygame_core.ecs.game_object_list import GameObjectList
    from pygame_core.ecs.state_object import StateObject, HoverableStateObject
    from pygame_core.ecs.animated_sprite import AnimatedSprite, AnimatedSpriteFactory
    from pygame_core.ecs.game_audio import GameAudio, MUSIC_CHANNEL, SFX_CHANNEL
    from pygame_core.ecs.sound_manager import SoundManager

    # ECS components
    from pygame_core.ecs.components.component import Component, Behaviour, MonoBehaviour
    from pygame_core.ecs.components.transform import Transform
    from pygame_core.ecs.components.sprite_renderer2d import SpriteRenderer2D
    from pygame_core.ecs.components.rigidbody2d import Rigidbody2D
    from pygame_core.ecs.components.animator import Animator
    from pygame_core.ecs.components.animation_clip import AnimationClip

    # Assets
    from pygame_core.asset_path import AssetPath, ImagePath, FontPath, SoundPath, PathLike
    from pygame_core.asset_manager import AssetManager
    from pygame_core.sprite_sheet import SpriteSheet
    from pygame_core.image import load_image, scale, scale_by, nine_slice_scale
    from pygame_core.font import load_font

    # Panels / UI
    from pygame_core.panel_manager import PanelManager
    from pygame_core.panel_loader import PanelLoader
    from pygame_core.panel_loader_ext import PanelLoaderExt
    from pygame_core.panel_factory import (
        make_factory, make_animated_factory, make_slider_factory, make_text_factory,
    )
    from pygame_core.ui_widgets.text_object import TextObject
    from pygame_core.ui_widgets.slider import Slider
    from pygame_core.ui_widgets.input_box import InputBox
    from pygame_core.ui_widgets.menu_controller import MenuController

    # Utils
    from pygame_core.utils import Anchorable, MouseInteractive, resolve_size
    from pygame_core.math_utils import distance, angle_between_points, angle_between_delta

    # Persistence / world data
    from pygame_core.save_store import SaveStore
    from pygame_core.database import Database
    from pygame_core.spatial_grid import SpatialGrid
    from pygame_core.tilemap import TiledMap

    # Networking
    from pygame_core.net.protocol import (
        Protocol, ProtocolError, Codec, JSONCodec, TypedJSONCodec, PickleCodec,
    )
    from pygame_core.net.transport import Connection, BaseClient, BaseServer

# name -> the submodule that actually defines it, for the lazy __getattr__
# below. Grouped identically to the TYPE_CHECKING block above; keep both in
# sync when adding a new public export.
_EXPORTS: dict[str, str] = {
    # Application / window management
    "Application": "pygame_core.application",
    "Mouse": "pygame_core.mouse",
    "Camera": "pygame_core.camera",
    "Debug": "pygame_core.debug",
    "SplashScreen": "pygame_core.splash_screen",
    # ECS core
    "GameObject": "pygame_core.ecs.game_object",
    "GameObjectDict": "pygame_core.ecs.game_object_dict",
    "GameObjectList": "pygame_core.ecs.game_object_list",
    "StateObject": "pygame_core.ecs.state_object",
    "HoverableStateObject": "pygame_core.ecs.state_object",
    "AnimatedSprite": "pygame_core.ecs.animated_sprite",
    "AnimatedSpriteFactory": "pygame_core.ecs.animated_sprite",
    "GameAudio": "pygame_core.ecs.game_audio",
    "MUSIC_CHANNEL": "pygame_core.ecs.game_audio",
    "SFX_CHANNEL": "pygame_core.ecs.game_audio",
    "SoundManager": "pygame_core.ecs.sound_manager",
    # ECS components
    "Component": "pygame_core.ecs.components.component",
    "Behaviour": "pygame_core.ecs.components.component",
    "MonoBehaviour": "pygame_core.ecs.components.component",
    "Transform": "pygame_core.ecs.components.transform",
    "SpriteRenderer2D": "pygame_core.ecs.components.sprite_renderer2d",
    "Rigidbody2D": "pygame_core.ecs.components.rigidbody2d",
    "Animator": "pygame_core.ecs.components.animator",
    "AnimationClip": "pygame_core.ecs.components.animation_clip",
    # Assets
    "AssetPath": "pygame_core.asset_path",
    "ImagePath": "pygame_core.asset_path",
    "FontPath": "pygame_core.asset_path",
    "SoundPath": "pygame_core.asset_path",
    "PathLike": "pygame_core.asset_path",
    "AssetManager": "pygame_core.asset_manager",
    "SpriteSheet": "pygame_core.sprite_sheet",
    "load_image": "pygame_core.image",
    "scale": "pygame_core.image",
    "scale_by": "pygame_core.image",
    "nine_slice_scale": "pygame_core.image",
    "load_font": "pygame_core.font",
    # Panels / UI
    "PanelManager": "pygame_core.panel_manager",
    "PanelLoader": "pygame_core.panel_loader",
    "PanelLoaderExt": "pygame_core.panel_loader_ext",
    "make_factory": "pygame_core.panel_factory",
    "make_animated_factory": "pygame_core.panel_factory",
    "make_slider_factory": "pygame_core.panel_factory",
    "make_text_factory": "pygame_core.panel_factory",
    "TextObject": "pygame_core.ui_widgets.text_object",
    "Slider": "pygame_core.ui_widgets.slider",
    "InputBox": "pygame_core.ui_widgets.input_box",
    "MenuController": "pygame_core.ui_widgets.menu_controller",
    # Utils
    "Anchorable": "pygame_core.utils",
    "MouseInteractive": "pygame_core.utils",
    "resolve_size": "pygame_core.utils",
    "distance": "pygame_core.math_utils",
    "angle_between_points": "pygame_core.math_utils",
    "angle_between_delta": "pygame_core.math_utils",
    # Persistence / world data
    "SaveStore": "pygame_core.save_store",
    "Database": "pygame_core.database",
    "SpatialGrid": "pygame_core.spatial_grid",
    "TiledMap": "pygame_core.tilemap",
    # Networking
    "Protocol": "pygame_core.net.protocol",
    "ProtocolError": "pygame_core.net.protocol",
    "Codec": "pygame_core.net.protocol",
    "JSONCodec": "pygame_core.net.protocol",
    "TypedJSONCodec": "pygame_core.net.protocol",
    "PickleCodec": "pygame_core.net.protocol",
    "Connection": "pygame_core.net.transport",
    "BaseClient": "pygame_core.net.transport",
    "BaseServer": "pygame_core.net.transport",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_path), name)
    globals()[name] = value  # cache on the module so repeat access skips __getattr__
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
