---
name: bullet-heaven-game-design
description: >-
  Game design principles, mathematical models, and balancing frameworks for Bullet Heaven / Survivors-like roguelites.
  Use this skill when designing enemy wave spawning algorithms, XP progression curves, level-up card drafting,
  weapon synergies, drop rate tables, damage formulas, knockback physics, and boss encounter pacing.
---

# Bullet Heaven (Survivors-Like) Game Design & Balancing

This skill contains the balancing equations, state machines, and algorithmic patterns standard in modern Bullet Heaven / Roguelite survival games (e.g., *Vampire Survivors*, *Purr Survivors*, *Brotato*, *20 Minutes Till Dawn*).

---

## 1. XP Progression & Level Curve Formulas

Progression pacing requires an exponential or polynomial scaling curve so early levels feel rapid (fast dopamine loop) while late levels require strategic farming.

### Recommended Formulas:

$$\text{XP}_{\text{required}}(L) = \lfloor A \times L^{1.5} + B \times L + C \rfloor$$

Where:
- $A \approx 12$ (Growth curvature factor)
- $B \approx 10$ (Linear slope)
- $C = 15$ (Base cost for Level 1 $\to$ 2)

```python
def calculate_xp_for_level(level: int) -> int:
    """Returns total XP required to advance from current level to level + 1."""
    if level <= 1:
        return 15
    return int(12 * (level ** 1.5) + 10 * level + 15)
```

---

## 2. Dynamic Wave Spawning Director

A survival director manages continuous pressure without sudden unplayable spikes or dead silence.

### A. Perimeter / Off-Screen Spawn Coordinates
Spawn enemies just outside the viewport camera boundary to avoid jarring pop-in:

```python
import math
import random

def get_offscreen_spawn_pos(center_x: float, center_y: float, view_w: int = 1280, view_h: int = 720, margin: int = 60):
    """Generates coordinates in an ellipse/rectangle just outside the player's screen."""
    angle = random.uniform(0, 2 * math.pi)
    rx = (view_w / 2) + margin
    ry = (view_h / 2) + margin
    
    spawn_x = center_x + rx * math.cos(angle)
    spawn_y = center_y + ry * math.sin(angle)
    return spawn_x, spawn_y
```

### B. Dynamic Budget Scaling by Game Time:
$$\text{Enemy Cap}(t) = \min(\text{MaxCap}, \text{BaseCap} + \lfloor t / 15 \rfloor \times 5)$$
$$\text{Spawn Interval}(t) = \max(0.15, \text{BaseInterval} \times e^{-0.003 \times t})$$

---

## 3. Card Drafting & Rarity Weighting Algorithm

When drafting 3 cards upon Level Up:

| Rarity Tier | Base Weight | Color Hex / RGB | Typical Stat Multiplier |
| :--- | :--- | :--- | :--- |
| **Common** | 60% | `#94A3B8` (Slate) | $1.0\times$ (e.g. +10% Damage) |
| **Uncommon** | 25% | `#22C55E` (Emerald) | $1.5\times$ (e.g. +15% Damage + 5% Speed) |
| **Rare** | 10% | `#3B82F6` (Sapphire) | $2.2\times$ (e.g. +25% Damage + Piercing +1) |
| **Epic** | 4% | `#A855F7` (Mystic Purple) | $3.5\times$ (e.g. +40% Attack Speed + Multi-shot) |
| **Legendary** | 1% | `#FFCC00` (Gold) | Unique Game-Changer (e.g. Orbiting Shield / Beam) |

```python
def roll_rarity(luck_multiplier: float = 1.0) -> str:
    weights = {
        "common": 60,
        "uncommon": 25 * luck_multiplier,
        "rare": 10 * luck_multiplier,
        "epic": 4 * (luck_multiplier ** 1.2),
        "legendary": 1 * (luck_multiplier ** 1.5),
    }
    total = sum(weights.values())
    r = random.uniform(0, total)
    current = 0
    for rarity, w in weights.items():
        current += w
        if r <= current:
            return rarity
    return "common"
```

---

## 4. Damage & Knockback Physics

### Damage Formula with Defense/Armor:
$$\text{Damage Taken} = \max\left(1, \lfloor \text{Incoming Damage} \times \frac{100}{100 + \text{Armor}} \rfloor\right)$$

### Knockback Impulse Decay:
When an enemy is struck, apply an instantaneous impulse vector $\vec{K}$ away from the damage source, decaying with friction each frame:
```python
enemy.knockback_vector += (enemy.pos - hit_source.pos).normalize() * knockback_force
# In enemy update loop:
enemy.pos += enemy.knockback_vector * dt
enemy.knockback_vector *= math.pow(0.05, dt)  # Exponential friction decay
```

---

## 5. Loot Drop Tables & Magnet Mechanics

1. **XP Gems**: Always drop or have high drop probability ($90\%+$).
2. **Gold Coins**: $15-30\%$ chance on normal enemies, $100\%$ on Elites and Chests.
3. **Magnet Curve**: Magnet attraction speed should accelerate as the gem approaches the player:
$$v_{\text{gem}} = v_{\text{base}} + \frac{k}{(d + 1)}$$
Where $d$ is the distance to the player and $k$ is an acceleration constant.
