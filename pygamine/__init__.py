"""pygamine: a shared pygame-ce application/ECS/asset toolkit.

This top-level module re-exports the package's public API so consumers can
write `from pygamine import Application, GameObject, Camera` instead of
reaching into individual submodules (`pygamine.ecs.game_object`,
`pygamine.ecs.components.transform`, ...). Importing from the deeper
paths still works -- this is purely a convenience surface, not a move --
but new code should prefer the shallow form.

Exports are resolved lazily (PEP 562's module `__getattr__`), not imported
eagerly here, on purpose: `asset_manager`/`tilemap` pull in `pyyaml`/
`pytmx`, and not every consumer of this package uses those subsystems (some
projects deliberately skip the YAML-driven AssetManager/panel system and
only depend on the ECS core). Eagerly importing everything at
`import pygamine` time would force *every* consumer to have *every*
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
    # `as X` on every name is the standard "redundant alias" idiom type
    # checkers and ruff (F401) both recognize as an intentional re-export --
    # without it, every one of these reads as an unused import, since
    # nothing in this file references them outside of __all__/_EXPORTS.

    # Application / window management
    from pygamine.application import Application as Application
    from pygamine.mouse import Mouse as Mouse
    from pygamine.camera import Camera as Camera, Drawable as Drawable
    from pygamine.debug import Debug as Debug
    from pygamine.splash_screen import SplashScreen as SplashScreen

    # ECS core
    from pygamine.ecs.game_object import GameObject as GameObject
    from pygamine.ecs.game_object_dict import GameObjectDict as GameObjectDict
    from pygamine.ecs.game_object_list import GameObjectList as GameObjectList
    from pygamine.ecs.state_object import StateObject as StateObject, HoverableStateObject as HoverableStateObject
    from pygamine.ecs.animated_sprite import AnimatedSprite as AnimatedSprite, AnimatedSpriteFactory as AnimatedSpriteFactory
    from pygamine.ecs.game_audio import GameAudio as GameAudio, MUSIC_CHANNEL as MUSIC_CHANNEL, SFX_CHANNEL as SFX_CHANNEL
    from pygamine.ecs.sound_manager import SoundManager as SoundManager

    # ECS components
    from pygamine.ecs.components.component import (
        Component as Component, Behaviour as Behaviour, MonoBehaviour as MonoBehaviour,
    )
    from pygamine.ecs.components.transform import Transform as Transform
    from pygamine.ecs.components.sprite_renderer2d import SpriteRenderer2D as SpriteRenderer2D
    from pygamine.ecs.components.rigidbody2d import Rigidbody2D as Rigidbody2D
    from pygamine.ecs.components.animator import Animator as Animator
    from pygamine.ecs.components.animation_clip import AnimationClip as AnimationClip

    # Assets
    from pygamine.asset_path import (
        AssetPath as AssetPath, ImagePath as ImagePath, FontPath as FontPath,
        SoundPath as SoundPath, PathLike as PathLike,
    )
    from pygamine.asset_manager import AssetManager as AssetManager
    from pygamine.sprite_sheet import SpriteSheet as SpriteSheet
    from pygamine.image import (
        load_image as load_image, scale as scale, scale_by as scale_by, nine_slice_scale as nine_slice_scale,
    )
    from pygamine.font import load_font as load_font

    # Panels / UI
    from pygamine.panel_manager import PanelManager as PanelManager
    from pygamine.panel_loader import PanelLoader as PanelLoader
    from pygamine.panel_loader_ext import PanelLoaderExt as PanelLoaderExt
    from pygamine.panel_factory import (
        make_factory as make_factory, make_animated_factory as make_animated_factory,
        make_slider_factory as make_slider_factory, make_text_factory as make_text_factory,
    )
    from pygamine.ui_widgets.text_object import TextObject as TextObject
    from pygamine.ui_widgets.slider import Slider as Slider
    from pygamine.ui_widgets.input_box import InputBox as InputBox
    from pygamine.ui_widgets.menu_controller import MenuController as MenuController

    # Utils
    from pygamine.utils import (
        Anchorable as Anchorable, MouseInteractive as MouseInteractive, resolve_size as resolve_size,
    )
    from pygamine.math_utils import (
        distance as distance, angle_between_points as angle_between_points,
        angle_between_delta as angle_between_delta,
    )

    # Persistence / world data
    from pygamine.save_store import SaveStore as SaveStore
    from pygamine.database import Database as Database
    from pygamine.spatial_grid import SpatialGrid as SpatialGrid
    from pygamine.tilemap import TiledMap as TiledMap
    from pygamine.paths import resource_root as resource_root, resource_path as resource_path

    # Networking
    from pygamine.net.protocol import (
        Protocol as Protocol, ProtocolError as ProtocolError, Codec as Codec,
        JSONCodec as JSONCodec, TypedJSONCodec as TypedJSONCodec, PickleCodec as PickleCodec,
    )
    from pygamine.net.transport import (
        Connection as Connection, BaseClient as BaseClient, BaseServer as BaseServer,
    )

# name -> the submodule that actually defines it, for the lazy __getattr__
# below. Grouped identically to the TYPE_CHECKING block above; keep both in
# sync when adding a new public export.
_EXPORTS: dict[str, str] = {
    # Application / window management
    "Application": "pygamine.application",
    "Mouse": "pygamine.mouse",
    "Camera": "pygamine.camera",
    "Drawable": "pygamine.camera",
    "Debug": "pygamine.debug",
    "SplashScreen": "pygamine.splash_screen",
    # ECS core
    "GameObject": "pygamine.ecs.game_object",
    "GameObjectDict": "pygamine.ecs.game_object_dict",
    "GameObjectList": "pygamine.ecs.game_object_list",
    "StateObject": "pygamine.ecs.state_object",
    "HoverableStateObject": "pygamine.ecs.state_object",
    "AnimatedSprite": "pygamine.ecs.animated_sprite",
    "AnimatedSpriteFactory": "pygamine.ecs.animated_sprite",
    "GameAudio": "pygamine.ecs.game_audio",
    "MUSIC_CHANNEL": "pygamine.ecs.game_audio",
    "SFX_CHANNEL": "pygamine.ecs.game_audio",
    "SoundManager": "pygamine.ecs.sound_manager",
    # ECS components
    "Component": "pygamine.ecs.components.component",
    "Behaviour": "pygamine.ecs.components.component",
    "MonoBehaviour": "pygamine.ecs.components.component",
    "Transform": "pygamine.ecs.components.transform",
    "SpriteRenderer2D": "pygamine.ecs.components.sprite_renderer2d",
    "Rigidbody2D": "pygamine.ecs.components.rigidbody2d",
    "Animator": "pygamine.ecs.components.animator",
    "AnimationClip": "pygamine.ecs.components.animation_clip",
    # Assets
    "AssetPath": "pygamine.asset_path",
    "ImagePath": "pygamine.asset_path",
    "FontPath": "pygamine.asset_path",
    "SoundPath": "pygamine.asset_path",
    "PathLike": "pygamine.asset_path",
    "AssetManager": "pygamine.asset_manager",
    "SpriteSheet": "pygamine.sprite_sheet",
    "load_image": "pygamine.image",
    "scale": "pygamine.image",
    "scale_by": "pygamine.image",
    "nine_slice_scale": "pygamine.image",
    "load_font": "pygamine.font",
    # Panels / UI
    "PanelManager": "pygamine.panel_manager",
    "PanelLoader": "pygamine.panel_loader",
    "PanelLoaderExt": "pygamine.panel_loader_ext",
    "make_factory": "pygamine.panel_factory",
    "make_animated_factory": "pygamine.panel_factory",
    "make_slider_factory": "pygamine.panel_factory",
    "make_text_factory": "pygamine.panel_factory",
    "TextObject": "pygamine.ui_widgets.text_object",
    "Slider": "pygamine.ui_widgets.slider",
    "InputBox": "pygamine.ui_widgets.input_box",
    "MenuController": "pygamine.ui_widgets.menu_controller",
    # Utils
    "Anchorable": "pygamine.utils",
    "MouseInteractive": "pygamine.utils",
    "resolve_size": "pygamine.utils",
    "distance": "pygamine.math_utils",
    "angle_between_points": "pygamine.math_utils",
    "angle_between_delta": "pygamine.math_utils",
    # Persistence / world data
    "SaveStore": "pygamine.save_store",
    "Database": "pygamine.database",
    "SpatialGrid": "pygamine.spatial_grid",
    "TiledMap": "pygamine.tilemap",
    "resource_root": "pygamine.paths",
    "resource_path": "pygamine.paths",
    # Networking
    "Protocol": "pygamine.net.protocol",
    "ProtocolError": "pygamine.net.protocol",
    "Codec": "pygamine.net.protocol",
    "JSONCodec": "pygamine.net.protocol",
    "TypedJSONCodec": "pygamine.net.protocol",
    "PickleCodec": "pygamine.net.protocol",
    "Connection": "pygamine.net.transport",
    "BaseClient": "pygamine.net.transport",
    "BaseServer": "pygamine.net.transport",
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
