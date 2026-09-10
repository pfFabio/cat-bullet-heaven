---
name: purr-survivors-workflow
description: >-
  Specific architecture runbook and development workflows for Purr Survivors: Cats vs Dogs (Bullet Heaven 2D).
  Use this skill when modifying or extending this game codebase: adding new cat skins to skin_catalog.py,
  creating new enemy/boss behaviors in gameplay_scene.py, adding upgrade cards and powers,
  updating save/load persistence in save_system.py, and executing automated test suites.
---

# Purr Survivors: Cats vs Dogs — Developer Runbook

This skill is the project-specific developer guide for **Purr Survivors**.

---

## 1. Project Directory Map

```text
bullet-heaven/
├── .agents/skills/             # Workspace skills (customizations)
├── saves/
│   ├── settings.json          # Audio/Video settings
│   └── progress.json          # Gold, High Score, Unlocked Skins, Upgrades
├── src/
│   ├── main.py                # Entrypoint
│   ├── core/
│   │   ├── constants.py       # Screen dimensions, colors, default dicts
│   │   ├── engine.py          # 60 FPS GameEngine & Scene switcher
│   │   ├── save_system.py     # Safe JSON save/load with deep merging
│   │   ├── skin_catalog.py    # 50 Cat skins, rarities, lore, & POWER_DEFINITIONS
│   │   ├── audio_manager.py   # PCM sound synthesizer and mixer
│   │   └── asset_manager.py   # Font cache, spritesheets, shadows, fallback shapes
│   ├── ui/
│   │   ├── components.py      # Button, Slider, Toggle, Panel, UpgradeCard
│   │   └── particle.py        # Ambient floating dust particle system
│   └── scenes/
│       ├── base_scene.py      # Abstract BaseScene interface
│       ├── main_menu_scene.py # Main menu & Career Stats modal
│       ├── settings_scene.py  # Tabbed settings (Audio, Video, Controls)
│       ├── cat_shop_scene.py  # Sanctuary: Cat skin browser and purchase
│       └── gameplay_scene.py  # Main bullet heaven game loop
└── tests/                     # Unittest suite
```

---

## 2. Adding a New Cat Skin & Special Power

### Step A: Define the Power in `src/core/skin_catalog.py`
```python
POWER_DEFINITIONS["laser_burst"] = {
    "name": "Rajada Laser",
    "description": "Dispara 3 feixes concentrados a cada 4 segundos.",
    "icon": "⚡",
    "trigger": "timer", # 'timer', 'passive', 'on_hit', 'on_kill'
    "cooldown": 4.0,
    "damage_mult": 1.5,
}
```

### Step B: Register the Skin Entry in `SKIN_CATALOG`
```python
"cosmic_nebula": {
    "id": "cosmic_nebula",
    "name": "Nebula Cósmica",
    "rarity": "legendary",      # common, uncommon, rare, epic, legendary
    "cost": 1500,               # Gold cost in shop (0 for default unlocked)
    "spritesheet": "Cats Download/Sprite-0004.png",
    "color": (168, 85, 247),
    "power_id": "laser_burst",
    "lore": "Nascido da poeira estelar de uma supernova felina.",
    "stats": {
        "max_hp_bonus": 25,
        "damage_bonus": 15,
        "speed_bonus": 30,
        "pickup_bonus": 40
    }
}
```

---

## 3. Adding a New Enemy Archetype in `src/scenes/gameplay_scene.py`

In `gameplay_scene.py`, create or configure the enemy class:

```python
class EnemyGhost(Enemy):
    """Fast phasing enemy that intermittently becomes invulnerable."""
    def __init__(self, x: float, y: float, scaling: float = 1.0):
        super().__init__(
            x=x, y=y,
            hp=int(35 * scaling),
            speed=210.0,
            damage=12,
            color=(147, 197, 253),
            xp_value=3,
            gold_chance=0.25
        )
        self.phase_timer = 0.0
        self.is_phasing = False

    def update(self, dt: float, player_pos: pygame.Vector2):
        self.phase_timer += dt
        if self.phase_timer >= 3.0:
            self.is_phasing = not self.is_phasing
            self.phase_timer = 0.0
        super().update(dt, player_pos)
```

---

## 4. Save Migration & Safe Persistence Pattern

When adding new settings or progress fields:
1. Update `DEFAULT_SETTINGS` or `DEFAULT_PROGRESS` in `src/core/constants.py`.
2. `SaveSystem.load_data()` in `src/core/save_system.py` automatically performs a **deep merge** of defaults with existing disk files, preventing crashes on old user save files.

---

## 5. Testing & Verification Runbook

Always verify changes by executing the test suite:

```bash
# Run all unit and integration tests
python -m unittest discover tests

# Run specific test modules
python -m unittest tests/test_cat_powers.py
python -m unittest tests/test_save_and_engine.py
python -m unittest tests/test_scenes_integration.py
```
