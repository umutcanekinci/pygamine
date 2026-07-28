# pygame_core

Shared pygame-ce utilities used across personal game projects. Provides an `Application` base, a component-based game-object layer, a YAML-driven panel/UI system, asset loaders, and a handful of helpers (camera, sprite sheet, audio, database).

## Installation

This package is consumed as a **git submodule** by the host project — typically vendored under `src/pygame_core/` and added to `PYTHONPATH` (or `sys.path`) by the host's entry point.

```bash
git submodule add https://github.com/umutcanekinci/pygame-core.git src/pygame_core
```

Then in the host's entry script:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src" / "pygame_core"))

# Now imports work:
from pygame_core.application import Application
```

It can also be installed via pip directly from GitHub:

```bash
pip install git+https://github.com/umutcanekinci/pygame-core.git
```

Requires Python 3.12+ and `pygame-ce`.

## Module map

### Game loop
| Module | Exports | Notes |
|---|---|---|
| `application` | `Application` | Top-level run loop (`init/run/handle_event/update/draw`), fullscreen toggle, debug overlay hook |
| `mouse` | `Mouse` | Cursor position + optional custom-cursor `GameObject` |
| `camera` | `Camera` | Edge-scroll camera with world↔screen transforms |
| `splash_screen` | splash helper | Pre-loop splash render |
| `debug` | debug helpers | Wireframes and live state overlay |

### Assets
| Module | Exports |
|---|---|
| `asset_path` | `AssetPath`, `ImagePath`, `FontPath`, `SoundPath`, `PathLike` |
| `asset_manager` | `AssetManager` — loads images/sounds/fonts from a YAML manifest |
| `image` | `load_image`, `scale`, `scale_by`, `nine_slice_scale` |
| `font` | `load_font` (asset-key first, falls back to `SysFont`) |
| `sprite_sheet` | `SpriteSheet` (`from_path`, `strip`, `grid`, `frame`) |
| `database` | `Database` — thin SQLite wrapper, stores `.db` under `databases/` |

### Panel / UI system
| Module | Exports |
|---|---|
| `panel_manager` | `PanelManager` — named panels with `current_panel` switching |
| `panel_loader` | `PanelLoader` — YAML → objects via registered factories |
| `panel_loader_ext` | `PanelLoaderExt` — adds `object_templates` inheritance |
| `panel_factory` | `make_factory`, `make_text_factory` |

### ECS
| Module | Exports |
|---|---|
| `ecs.game_object` | `GameObject` (active/hierarchy/`invoke[_repeating]`/components) |
| `ecs.game_object_dict` | `GameObjectDict` — named child container with lifecycle dispatch |
| `ecs.state_object` | `StateObject`, `HoverableStateObject` |
| `ecs.animated_sprite` | `AnimatedSprite`, `AnimatedSpriteFactory` |
| `ecs.game_audio` | `GameAudio` — music + sfx channels with volume control |
| `ecs.components.component` | `Component`, `Behaviour`, `MonoBehaviour` |
| `ecs.components.transform` | `Transform` — anchored pos/size relative to parent |
| `ecs.components.sprite_renderer2d` | `SpriteRenderer2D` |
| `ecs.components.rigidbody2d` | `Rigidbody2D` |
| `ecs.components.animator` | `Animator`, `AnimationClip` |

### UI widgets
| Module | Exports |
|---|---|
| `ui_widgets.text_object` | `TextObject` — single- or multi-state label |
| `ui_widgets.menu_controller` | `MenuController` — keyboard-navigable button list |
| `ui_widgets.input_box` | `InputBox` |

### Utilities
| Module | Exports |
|---|---|
| `utils` | `MouseInteractive`, `Anchorable`, `resolve_size`, `ANCHORS` |
| `math_utils` | Vector and angle helpers |

## Quick examples

### Load a sprite sheet → animated sprite

```python
from pygame_core.sprite_sheet import SpriteSheet
from pygame_core.ecs.components.animation_clip import AnimationClip
from pygame_core.ecs.animated_sprite import AnimatedSprite

frames = SpriteSheet.from_path("coin_strip4.png").strip(4)
coin = AnimatedSprite(frames=frames, fps=8, pos=(100, 100))
# inside the game loop:
coin.update()
coin.draw(surface)
```

### Asset path helpers

```python
from pygame_core.asset_path import ImagePath, FontPath, SoundPath

ImagePath("player")             # → assets/images/player.png
ImagePath("hero", "sprites")    # → assets/images/sprites/hero.png
FontPath("comic")               # → assets/fonts/comic.ttf
SoundPath("jump")               # → assets/sounds/jump.ogg
```

All `AssetPath` subclasses implement `__fspath__`, so they can be passed directly to `pygame.image.load` / `pygame.font.Font` / `pygame.mixer.Sound`.

### Database

```python
from pygame_core.database import Database

db = Database("savefile")
rows = db.execute_safely(
    "SELECT name, value FROM scores ORDER BY value DESC LIMIT 10",
    fetch=True,
)
```

`execute_safely` handles connect/commit/disconnect in one call; use `connect/execute/commit/disconnect` directly when you need to batch operations.

## Adding a new module

1. Create `pygame_core/<module>.py`
2. Import it where needed: `from pygame_core.<module> import ...`
3. No reinstall required when consumed as a submodule on `sys.path`