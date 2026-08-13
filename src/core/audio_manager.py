"""
Gerenciador de áudio com suporte a canais de volume (Master, BGM, SFX)
e sintetizador procedural de efeitos sonoros em memória (sem necessidade de arquivos de áudio externos).
"""
import math
import struct
import logging
import pygame
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AudioManager:
    """Controla canais de áudio e sintetiza efeitos sonoros para feedback imediato."""

    def __init__(self, master_vol: float = 0.8, music_vol: float = 0.7, sfx_vol: float = 0.9):
        self.master_volume = master_vol
        self.music_volume = music_vol
        self.sfx_volume = sfx_vol
        self.initialized = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

        self._init_mixer()
        if self.initialized:
            self._generate_procedural_sounds()
            self.apply_volumes()

    def _init_mixer(self) -> None:
        """Inicializa o mixer do Pygame de forma segura."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.initialized = True
        except Exception as e:
            logger.warning(f"Não foi possível inicializar áudio: {e}. Executando em modo mudo.")
            self.initialized = False

    def _create_pcm_sound(self, duration_sec: float, freq_func) -> Optional[pygame.mixer.Sound]:
        """Gera um Sound a partir de uma função matemática de onda senoidal de 44.1kHz 16-bit mono."""
        if not self.initialized:
            return None
        sample_rate = 44100
        num_samples = int(sample_rate * duration_sec)
        raw_bytes = bytearray()

        for i in range(num_samples):
            t = i / sample_rate
            freq, amp = freq_func(t, duration_sec)
            # Envoltória de atenuação para evitar cliques
            decay = max(0.0, 1.0 - (t / duration_sec))
            val = math.sin(2.0 * math.pi * freq * t) * amp * decay
            # Converte para signed 16-bit (-32767 a 32767)
            int_val = int(max(-1.0, min(1.0, val)) * 32767)
            raw_bytes.extend(struct.pack("<h", int_val))

        try:
            return pygame.mixer.Sound(buffer=bytes(raw_bytes))
        except Exception as e:
            logger.debug(f"Erro ao gerar som sintético: {e}")
            return None

    def _generate_procedural_sounds(self) -> None:
        """Sintetiza efeitos sonoros para a UI e gameplay."""
        if not self.initialized:
            return

        # Som de Hover no Menu (blip suave)
        def hover_wave(t, d):
            return 880, 0.15

        # Som de Clique / Confirmar (duplo tom alegre)
        def click_wave(t, d):
            f = 523.25 if t < d / 2 else 659.25
            return f, 0.35

        # Som de Selecionar / Play (acorde subindo)
        def select_wave(t, d):
            f = 440 + (t / d) * 440
            return f, 0.4

        # Som de Disparo (tiro de projétil)
        def shoot_wave(t, d):
            f = 900 - (t / d) * 600
            return max(100, f), 0.25

        # Som de Acerto / Hit (crunch metálico rápido)
        def hit_wave(t, d):
            f = 220 - (t / d) * 150
            return max(50, f), 0.35

        # Som de Gema / XP coletado (brilho cristalino)
        def gem_wave(t, d):
            f = 1200 + (t / d) * 600
            return f, 0.25

        # Som de Level Up (som ascendente brilhante)
        def levelup_wave(t, d):
            step = int((t / d) * 4)
            notes = [523.25, 659.25, 783.99, 1046.50]
            return notes[min(step, 3)], 0.45

        snd_hover = self._create_pcm_sound(0.04, hover_wave)
        snd_click = self._create_pcm_sound(0.08, click_wave)
        snd_select = self._create_pcm_sound(0.18, select_wave)
        snd_shoot = self._create_pcm_sound(0.09, shoot_wave)
        snd_hit = self._create_pcm_sound(0.07, hit_wave)
        snd_gem = self._create_pcm_sound(0.08, gem_wave)
        snd_levelup = self._create_pcm_sound(0.35, levelup_wave)

        if snd_hover:
            self.sounds["ui_hover"] = snd_hover
        if snd_click:
            self.sounds["ui_click"] = snd_click
        if snd_select:
            self.sounds["ui_select"] = snd_select
        if snd_shoot:
            self.sounds["shoot"] = snd_shoot
        if snd_hit:
            self.sounds["hit"] = snd_hit
        if snd_gem:
            self.sounds["gem"] = snd_gem
        if snd_levelup:
            self.sounds["levelup"] = snd_levelup

    def apply_volumes(self) -> None:
        """Aplica os volumes calculados aos canais de efeitos e música."""
        effective_sfx_vol = self.master_volume * self.sfx_volume
        for sound in self.sounds.values():
            sound.set_volume(effective_sfx_vol)

        if pygame.mixer.get_init():
            effective_music_vol = self.master_volume * self.music_volume
            pygame.mixer.music.set_volume(effective_music_vol)

    def play_sfx(self, sound_name: str) -> None:
        """Toca um efeito sonoro caso exista."""
        if not self.initialized:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()

    def set_master_volume(self, val: float) -> None:
        self.master_volume = max(0.0, min(1.0, val))
        self.apply_volumes()

    def set_music_volume(self, val: float) -> None:
        self.music_volume = max(0.0, min(1.0, val))
        self.apply_volumes()

    def set_sfx_volume(self, val: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, val))
        self.apply_volumes()
