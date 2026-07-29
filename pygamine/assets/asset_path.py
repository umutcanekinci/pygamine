from __future__ import annotations

import os
from typing import Union


class AssetPath(os.PathLike):
    """Game asset path — string-compatible but type-safe."""

    def __init__(self, name: str, folder: str = "", extension: str = "png",
                 base: str = "assets"):
        self.name = name
        self.folder = folder
        self.extension = extension.lstrip(".")
        self.base = base

    @property
    def full_path(self) -> str:
        parts = [self.base]
        if self.folder:
            parts.append(self.folder)
        rel = f"{'/'.join(parts)}/{self.name}.{self.extension}"
        # Absolute, not relative. On Android, SDL2's SDL_RWFromFile (used under
        # the hood by pygame.image.load / mixer.Sound / font.Font) treats a
        # *relative* path as an APK-asset lookup via AAssetManager — but p4a
        # unpacks our assets into the private files dir, not the APK asset
        # namespace, so a relative string fails ("No file ... found in working
        # directory"). An absolute path (leading '/') makes SDL fall back to
        # fopen and read the real file. Anchored to the CWD, which is the app
        # root on both desktop (run from the project root) and Android (p4a
        # chdir's to files/app) — the same assumption load_manifest("config/…")
        # already relies on. On desktop this is just a harmless absolute path.
        return os.path.abspath(rel)

    def __str__(self) -> str:
        return self.full_path

    def __fspath__(self) -> str:
        # os.PathLike protocol — pygame.image.load(path) accepts this
        return self.full_path

    def __repr__(self) -> str:
        return f"AssetPath({self.full_path!r})"


class ImagePath(AssetPath):
    def __init__(self, name: str, folder: str = "", extension: str = "png"):
        super().__init__(name, folder, extension, base="assets/images")


class FontPath(AssetPath):
    def __init__(self, name: str, folder: str = "", extension: str = "ttf"):
        super().__init__(name, folder, extension, base="assets/fonts")


class SoundPath(AssetPath):
    def __init__(self, name: str, folder: str = "", extension: str = "ogg"):
        super().__init__(name, folder, extension, base="assets/sounds")


PathLike = Union[str, "os.PathLike[str]"]
