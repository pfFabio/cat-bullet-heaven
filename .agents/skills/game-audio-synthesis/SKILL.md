---
name: game-audio-synthesis
description: >-
  Procedural sound generation and PCM digital signal synthesis for 2D games using Python and Pygame mixer.
  Use this skill when generating standalone sound effects (lasers, hits, coin pickups, level up fanfares,
  explosions, UI clicks) dynamically in memory without relying on external .wav or .mp3 audio asset files.
---

# Procedural Game Audio & PCM Sound Synthesis

This skill covers generating crisp, zero-dependency procedural sound effects (SFX) directly in memory via 44.1 kHz 16-bit PCM wave synthesis.

---

## 1. PCM Synthesis Fundamentals in Pygame-CE

Pygame's `pygame.mixer.Sound(buffer=bytes)` accepts raw binary 16-bit signed integer byte arrays (`<h` in Python `struct`):

```python
import math
import struct
import random
import pygame
from typing import Callable, Tuple

def create_pcm_sound(duration_sec: float, wave_fn: Callable[[float, float], Tuple[float, float]]) -> pygame.mixer.Sound:
    """
    Generates a pygame.mixer.Sound.
    wave_fn(t: float, total_duration: float) -> (frequency: float, amplitude: float)
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration_sec)
    raw_bytes = bytearray()
    
    for i in range(num_samples):
        t = i / sample_rate
        freq, amp = wave_fn(t, duration_sec)
        
        # Linear envelope decay to guarantee zero-crossing at end (prevents audio pop/clicks)
        decay = max(0.0, 1.0 - (t / duration_sec))
        sample_value = math.sin(2.0 * math.pi * freq * t) * amp * decay
        
        # Clamp to signed 16-bit range (-32767 to 32767)
        int_sample = int(max(-1.0, min(1.0, sample_value)) * 32767)
        raw_bytes.extend(struct.pack("<h", int_sample))
        
    return pygame.mixer.Sound(buffer=bytes(raw_bytes))
```

---

## 2. Classic Game Sound Recipes (Formulas)

### A. Laser / Projectile Shot (Downward Frequency Slide)
```python
def sfx_laser(t: float, d: float) -> Tuple[float, float]:
    # Slides from 950 Hz down to 250 Hz in 90ms
    freq = 950.0 - (t / d) * 700.0
    return max(100.0, freq), 0.35
```

### B. Enemy Hit / Crunch (Low Frequency Pitch Drop + Jitter)
```python
def sfx_hit(t: float, d: float) -> Tuple[float, float]:
    # Rapid drop from 240 Hz to 60 Hz with high punch
    freq = 240.0 - (t / d) * 180.0
    return max(40.0, freq), 0.40
```

### C. Gem / Coin Pickup (Sparkling Two-Tone Ping)
```python
def sfx_coin(t: float, d: float) -> Tuple[float, float]:
    # First half 987 Hz (B5), second half 1318 Hz (E6)
    freq = 987.77 if t < (d * 0.45) else 1318.51
    return freq, 0.30
```

### D. Level Up Fanfare (Ascending 4-Note Major Arpeggio)
```python
def sfx_levelup(t: float, d: float) -> Tuple[float, float]:
    # C5 (523), E5 (659), G5 (784), C6 (1046)
    notes = [523.25, 659.25, 783.99, 1046.50]
    step = min(3, int((t / d) * 4))
    return notes[step], 0.45
```

### E. Explosion (Filtered White Noise + Exponential Decay)
```python
def create_explosion_sound(duration_sec: float = 0.4) -> pygame.mixer.Sound:
    sample_rate = 44100
    num_samples = int(sample_rate * duration_sec)
    raw_bytes = bytearray()
    
    last_sample = 0.0
    for i in range(num_samples):
        t = i / sample_rate
        decay = math.exp(-6.0 * (t / duration_sec)) # Fast exponential falloff
        
        # White noise with 1st-order low-pass filter (Brownian rumble)
        noise = random.uniform(-1.0, 1.0)
        filtered = 0.85 * last_sample + 0.15 * noise
        last_sample = filtered
        
        val = filtered * 0.7 * decay
        int_sample = int(max(-1.0, min(1.0, val)) * 32767)
        raw_bytes.extend(struct.pack("<h", int_sample))
        
    return pygame.mixer.Sound(buffer=bytes(raw_bytes))
```

---

## 3. Safe Channel Management & Volume Architecture
1. **Master Bus**: Scales both Music and SFX (`effective_sfx = master * sfx_volume`).
2. **Polyphony Pool**: Reserve 8-16 mixer channels with `pygame.mixer.set_num_channels(16)`.
3. **Sound Cache**: Pre-synthesize all procedural sounds during engine initialization to avoid latency hitch during gameplay.
