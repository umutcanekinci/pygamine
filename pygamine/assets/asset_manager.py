from __future__ import annotations

from pathlib import Path
import pygame
import yaml

from pygamine.assets.asset_path import ImagePath, FontPath, SoundPath


class AssetManager:
    """Manifest-driven asset registry. Single source of truth for asset paths."""

    def __init__(self):
        self._images: dict[str, ImagePath] = {}
        self._fonts: dict[str, FontPath] = {}
        self._sounds: dict[str, SoundPath] = {}
        self._image_cache: dict[str, pygame.Surface] = {}

    def load_manifest(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Asset manifest not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        for key, cfg in (data.get("images", {}) or {}).items():
            self._images[key] = ImagePath(
                name=cfg["name"],
                folder=cfg.get("folder", ""),
                extension=cfg.get("extension", "png"),
            )

        for key, cfg in (data.get("fonts", {}) or {}).items():
            self._fonts[key] = FontPath(
                name=cfg["name"],
                folder=cfg.get("folder", ""),
                extension=cfg.get("extension", "ttf"),
            )

        for key, cfg in (data.get("sounds", {}) or {}).items():
            self._sounds[key] = SoundPath(
                name=cfg["name"],
                folder=cfg.get("folder", ""),
                extension=cfg.get("extension", "ogg"),
            )

    def validate(self) -> list[str]:
        """Validate that every registered path exists on disk. Returns the missing ones."""
        missing = []
        for key, path in {**self._images, **self._fonts, **self._sounds}.items():
            if not Path(str(path)).exists():
                missing.append(f"{key} → {path}")
        return missing

    def image_path(self, key: str) -> ImagePath:
        if key not in self._images:
            raise KeyError(f"Unknown image asset: '{key}'. Known: {list(self._images)[:5]}...")
        return self._images[key]

    def get_image(self, key: str) -> pygame.Surface:
        """Cached surface — one instance per key."""
        if key not in self._image_cache:
            path = self.image_path(key)
            self._image_cache[key] = pygame.image.load(path).convert_alpha()
        return self._image_cache[key]

    def font_path(self, key: str) -> FontPath:
        if key not in self._fonts:
            raise KeyError(f"Unknown font asset: '{key}'")
        return self._fonts[key]

    def sound_path(self, key: str) -> SoundPath:
        if key not in self._sounds:
            raise KeyError(f"Unknown sound asset: '{key}'")
        return self._sounds[key]