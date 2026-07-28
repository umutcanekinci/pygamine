from __future__ import annotations

from pygame import mixer

class SoundManager:
    @staticmethod
    def get_volume(channel: int) -> float:
        return mixer.Channel(channel).get_volume()

    @staticmethod
    def play_sound(channel: int, sound_path, loops=0) -> None:
        mixer.Channel(channel).play(mixer.Sound(sound_path), loops)

    @staticmethod
    def set_volume(channel: int, volume: float) -> None:
        mixer.Channel(channel).set_volume(max(0.0, min(1.0, volume)))
