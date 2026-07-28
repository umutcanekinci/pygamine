# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/); versioning
follows [SemVer](https://semver.org/) with the 0.y.z caveat it defines
itself — this is major version zero, so a MINOR bump can and does include
breaking changes, since the public API isn't considered stable yet.

No tags existed before this file was added (2026-07-28) despite `pyproject.toml`
carrying a `version` field since `e5c1fa6` — the four releases below were cut
retroactively from git history at that point, grouped by what actually shipped
together rather than reconstructing a commit-by-commit rationale for every
change. Anything before `e5c1fa6` (the commit that first introduced
`pyproject.toml` itself) isn't versioned at all; see `git log` for that era.

## [0.6.0] — 2026-07-29

- **Changed** (breaking): renamed the package/distribution/repository from
  `pygame_core`/`pygame-core` to **`pygamine`** -- PyPI already has an
  unrelated package literally named `pygame-core` (and a near-identical
  `pygame-pygame-core`), so publishing this under that name was never
  actually available. `import pygamine` replaces `import pygame_core`
  everywhere (deep-path imports too: `pygamine.ecs.game_object`, etc.);
  the GitHub repository itself moved to
  `https://github.com/umutcanekinci/pygamine` (old URL redirects, but
  consumers should point `.gitmodules`/`pyproject.toml` at the new one
  directly rather than relying on that indefinitely). No behavioral
  changes -- this is a pure rename, every module/class/function keeps its
  previous name and semantics.

## [0.5.0] — 2026-07-28

- **Added** `Application.restore_window_settings(saved_settings)`,
  `.window_settings()`, and `.reset_window_settings()` -- the window-mode/
  resolution slice of a `SaveStore`-style settings dict, extracted after
  chokepoint and standoff both independently grew the exact same three
  private methods (`_restore_window_mode`/`_save_settings`/
  `_reset_settings`) around this. Deliberately has no opinion on
  audio/gameplay settings a project also wants to persist alongside it --
  merge `window_settings()`'s dict into a larger one before saving.

## [0.4.1] — 2026-07-28

- **Fixed** a real regression from 0.4.0, caught immediately by a consumer's
  own test suite: `GameObject.image` was a read-only property, which broke
  every entity that manages its own image directly with no `SpriteRenderer2D`
  involved at all (e.g. one rendered straight from text) and expects a plain
  `self.image = ...` assignment to keep working -- `AttributeError: property
  'image' of 'GameObject' object has no setter`. `image` is now a full
  property backed by `_image`: a direct assignment takes priority over the
  `SpriteRenderer2D` fallback, exactly matching the pre-0.4.0 behavior for
  anything that never explicitly sets it.

## [0.4.0] — 2026-07-28

- **Changed** (breaking): `Camera.draw(surface, entity)` now reads `entity.image`
  directly instead of guessing between `entity.rotated_image` (when
  `entity.is_rotated`) and `entity.get_component(SpriteRenderer2D).image` --
  `Camera` no longer imports or knows about `SpriteRenderer2D`, ECS
  components, or rotation at all. `GameObject` gained a default `image`
  property (resolves to the attached `SpriteRenderer2D`'s image, or `None`
  without one) satisfying the new `Drawable` protocol for free; an entity
  that switches between multiple images (a rotated variant of its base
  sprite, an animation frame, ...) overrides that property itself instead
  of `Camera` special-casing `is_rotated`/`rotated_image` by name.
  Consumers with their own rotating/multi-image entities (e.g. chokepoint's
  `RotatableObject`) need to add an `image` property override before
  bumping past this version, or rotated sprites will silently render
  un-rotated instead of raising.

## [0.3.1] — 2026-07-28

- **Added** a CI lint job (`ruff check .`) and a `[tool.ruff.lint]` config,
  deliberately narrow: `F` (pyflakes — real bugs) and `I002` specifically
  (enforces `from __future__ import annotations` repo-wide via isort's
  required-imports check, not the full `I` sort-order category). Fixed the
  handful of files this caught: two real files missing the future import
  (`animation_clip.py`, `ui_widgets/input_box.py`), an unused `pathlib.Path`
  import, and every test file that was also missing it.
- **Fixed** a real bug this surfaced: `MouseInteractive.is_clicked()` computed
  a local `pressed` variable that was never used, and had a string literal
  positioned one line too late to actually function as the method's
  docstring (docstrings must be the first statement in the body).
- **Added** type hints (return types, mostly) to `Component`/`Behaviour`/
  `MonoBehaviour`, `Database`, `Camera`, `MouseInteractive`/`Anchorable`
  (`utils.py`), and a full pass (hints + a class docstring) on
  `ui_widgets/input_box.py`, which previously had neither.

## [0.3.0] — 2026-07-28

- **Added** a curated public API at the package root: `from pygamine import
  Application, GameObject, Camera, ...` now covers the ~66 names actually used
  across every consumer project, resolved lazily (PEP 562 module `__getattr__`)
  so importing a lightweight name never forces optional dependencies
  (`pyyaml`/`pytmx`) that a consumer might not otherwise need. Deep-path
  imports still work unchanged.
- **Added** `Application.splash` / `Application.show_splash()` — `run()` calls
  it automatically before the main loop, replacing the identical `run()`
  override + comment every consumer project had duplicated for this.
- **Added** `Application(..., fixed_aspect=True)` — locks `self.window` to the
  constructor's `size` as a genuine fixed design resolution regardless of the
  real display's shape, letterboxing/pillarboxing it with black bars
  (`Mouse.offset` added to keep click coordinates correct) instead of either
  distorting it or letting the default dynamic-canvas behavior reveal extra
  world space on a mismatched monitor.
- **Changed** `AnimationClip` now lives in its own `ecs.components.animation_clip`
  module instead of inside `animator.py` (which still re-exports it — source
  compatible either way).
- **Changed** every ECS/rendering module from tab to space indentation (no
  functional change, pure PEP 8 cleanup).
- **Fixed** README's module map, which was missing 7 modules including the
  entire `net` (protocol/transport) subsystem.
- **Fixed** (documentation) — every consumer's `[tool.uv.sources]` override for
  an editable local install had no effect, since none of them actually listed
  `pygamine` under `[project.dependencies]`; documented in the README so
  it's not copy-pasted as dead boilerplate again.

## [0.2.0] — 2026-07-08

- **Changed** (breaking): `self.window` is now dynamically rebuilt to always
  match the real display's current size/aspect ratio (scaled by the new
  `render_scale`), instead of being a fixed authored-resolution surface
  scaled onto the display via `pygame.FULLSCREEN | pygame.SCALED`. Consumers
  relying on the old fixed-canvas behavior need `fixed_aspect=True` (added in
  0.3.0) to get an equivalent result.
- **Added** `render_scale` — decouples internal render resolution from the
  real display's, so a project can render at a fraction of the display's
  pixels and let `_present()` upscale.
- **Changed** (breaking) the `windowed_resolution` API was renamed to
  `resolution`, and window mode / resolution became independent settings —
  picking a resolution no longer forces a mode switch.
- **Added** a windowed-resolution picker (`available_resolutions()`,
  `cycle_resolution()`, `set_resolution()`, `clear_resolution_override()`) and
  a borderless-fullscreen window mode (screen-filling, no exclusive mode
  switch — avoids the flash/flicker of a real display-mode change).
- **Added** `SaveStore` — JSON-backed key-value persistence for settings/saves,
  atomic writes, plus `SaveStore.delete()`.
- **Added** a `Slider` UI widget, registered as a panel factory type.
- **Fixed** the window re-centering on every `minimize()`, not just at startup.
- **Fixed** `_scale_def`'s centre-remapping for non-top-left anchors landing
  off-screen.

## [0.1.2] — 2026-07-07

- **Added** a real test suite (one file per module) and CI.
- **Fixed** F11 fullscreen toggle: tracked window-mode state explicitly
  instead of comparing `.size`, which could desync from the actual mode.
- **Fixed** `size: WINDOW` in `make_gui_object` using `parent.size` instead of
  `parent` directly.
- **Fixed** a missing `pytmx` dependency declaration.

## [0.1.1] — first tracked version

Baseline: packaging consolidated into `pyproject.toml` (`setup.py`/
`requirements.txt` dropped). Everything before this point (the initial
`Application`/`Mouse`/`PanelManager`/`AssetManager`/ECS core, ~60 commits) predates
this changelog and was never versioned — see `git log` for that history directly.
