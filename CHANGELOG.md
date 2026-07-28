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

## [0.3.0] — 2026-07-28

- **Added** a curated public API at the package root: `from pygame_core import
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
  `pygame-core` under `[project.dependencies]`; documented in the README so
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
