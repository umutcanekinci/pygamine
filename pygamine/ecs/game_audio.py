"""Channel-based audio: music on channel 0 (looped), SFX on channel 1.

Replaces both 2048's GameAudioMixin (channel-based, no pause/resume) and
tower-defense's SoundManagerExtension (mixer.music-based, music-only).
"""

from __future__ import annotations

import os
from typing import Union

from pygame import mixer

MUSIC_CHANNEL = 0
SFX_CHANNEL   = 1

PathArg = Union[str, "os.PathLike[str]"]


class GameAudio:
    def __init__(self, music_path: PathArg | None = None, autoplay: bool = True) -> None:
        self._music_paused = False
        if music_path is not None and autoplay:
            self.play_music(music_path)

    # ── music ─────────────────────────────────────────────────────────────────

    def play_music(self, path: PathArg, loops: int = -1) -> None:
        mixer.Channel(MUSIC_CHANNEL).play(mixer.Sound(str(path)), loops)
        self._music_paused = False

    def pause_music(self) -> None:
        if self._music_paused:
            return
        mixer.Channel(MUSIC_CHANNEL).pause()
        self._music_paused = True

    def resume_music(self) -> None:
        if not self._music_paused:
            return
        mixer.Channel(MUSIC_CHANNEL).unpause()
        self._music_paused = False

    def toggle_music(self) -> None:
        if self._music_paused:
            self.resume_music()
        else:
            self.pause_music()

    @property
    def is_music_paused(self) -> bool:
        return self._music_paused

    # ── sfx ───────────────────────────────────────────────────────────────────

    @staticmethod
    def play_sfx(path: PathArg) -> None:
        mixer.Channel(SFX_CHANNEL).play(mixer.Sound(str(path)))

    # ── volume ────────────────────────────────────────────────────────────────

    @staticmethod
    def music_volume() -> float:
        return mixer.Channel(MUSIC_CHANNEL).get_volume()

    @staticmethod
    def sfx_volume() -> float:
        return mixer.Channel(SFX_CHANNEL).get_volume()

    def set_music_volume(self, volume: float) -> None:
        self._set_channel_volume(MUSIC_CHANNEL, volume)

    def set_sfx_volume(self, volume: float) -> None:
        self._set_channel_volume(SFX_CHANNEL, volume)

    @staticmethod
    def _set_channel_volume(channel: int, volume: float) -> None:
        mixer.Channel(channel).set_volume(max(0.0, min(1.0, volume)))