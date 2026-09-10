"""
Script utilitário para pré-visualizar e sintetizar efeitos sonoros procedurais PCM.
Execute via terminal: python .agents/skills/game-audio-synthesis/scripts/preview_sfx.py
"""
import time
import math
import struct
import random
import pygame

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    print("=== Antigravity Audio Preview Utility ===")
    
    def generate_sound(duration, func):
        samples = int(44100 * duration)
        raw = bytearray()
        for i in range(samples):
            t = i / 44100
            freq, amp = func(t, duration)
            decay = max(0.0, 1.0 - (t / duration))
            val = math.sin(2.0 * math.pi * freq * t) * amp * decay
            int_val = int(max(-1.0, min(1.0, val)) * 32767)
            raw.extend(struct.pack("<h", int_val))
        return pygame.mixer.Sound(buffer=bytes(raw))

    laser = generate_sound(0.09, lambda t, d: (950 - (t/d)*700, 0.35))
    coin = generate_sound(0.1, lambda t, d: (987 if t < d*0.45 else 1318, 0.30))
    levelup = generate_sound(0.35, lambda t, d: ([523.25, 659.25, 783.99, 1046.50][min(3, int(t/d*4))], 0.4))
    
    print("[1/3] Reproduzindo Laser...")
    laser.play()
    time.sleep(0.3)
    
    print("[2/3] Reproduzindo Coin...")
    coin.play()
    time.sleep(0.3)
    
    print("[3/3] Reproduzindo Level Up...")
    levelup.play()
    time.sleep(0.6)
    
    print("Demonstração concluída com sucesso!")

if __name__ == "__main__":
    main()
