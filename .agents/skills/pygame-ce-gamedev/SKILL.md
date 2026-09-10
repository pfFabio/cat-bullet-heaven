---
name: pygame-ce-gamedev
description: >-
  Expert guide and best practices for developing high-performance 2D games with Pygame-CE (Community Edition).
  Use this skill when implementing game loops, optimizing frame rates (60+ FPS), managing delta time (dt),
  handling sprite batching, vector mathematics, spatial partitioning (grid/hash) for collision detection,
  particle systems, camera scrolling, screen shake, and headless test execution.
---

# Pygame-CE Game Development Guide

This skill provides architectural patterns, performance optimizations, and mathematical utilities for building robust 2D games with **Pygame-CE (Community Edition)**.

---

## 1. Core Architecture & Delta Time Loop

Always decouple frame rate from game logic using delta time (`dt`), clamped to prevent tunneling or spiral-of-death on frame drops:

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
clock = pygame.time.Clock()
TARGET_FPS = 60
running = True

while running:
    # dt in seconds (capped at 0.1s to avoid physics breakdown on lag spikes)
    dt = min(clock.tick(TARGET_FPS) / 1000.0, 0.1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Route events to current scene / UI

    # Update logic (passing dt)
    # Draw scene
    pygame.display.flip()
```

---

## 2. Fast Vectors & Movement Mathematics

Always use `pygame.Vector2` (implemented in C) instead of manual tuples or integer rects for continuous spatial movement:

```python
from pygame.math import Vector2

pos = Vector2(x, y)
target = Vector2(target_x, target_y)
direction = target - pos

if direction.length_squared() > 0:
    velocity = direction.normalize() * speed
    pos += velocity * dt
```

### Key Vector Operations:
- `vec.length_squared()`: 10x faster than `vec.length()` because it avoids `sqrt`. Ideal for range/distance checks (e.g. `dist_sq <= range * range`).
- `vec.clamp_magnitude_ip(max_speed)`: Limits acceleration without manual hypotenuse calculations.
- `vec.lerp(target_vec, smooth_factor)`: Smooth interpolation for camera follow, magnet attraction, and UI easing.

---

## 3. Spatial Partitioning for High Entity Counts (Bullet Heavens)

When tracking hundreds of enemies, projectiles, and collectables, naive $O(N \times M)$ nested collision loops destroy FPS. Use a **Spatial Grid Hash** to achieve near $O(1)$ query complexity.

```python
class SpatialGrid:
    """Fast spatial hash for 2D entity collision partitioning."""
    def __init__(self, cell_size: int = 128):
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        self.grid.clear()

    def _hash(self, x: float, y: float):
        return int(x // self.cell_size), int(y // self.cell_size)

    def insert(self, entity, x: float, y: float):
        cell = self._hash(x, y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)

    def query_radius(self, x: float, y: float, radius: float):
        min_cell_x = int((x - radius) // self.cell_size)
        max_cell_x = int((x + radius) // self.cell_size)
        min_cell_y = int((y - radius) // self.cell_size)
        max_cell_y = int((y + radius) // self.cell_size)
        
        results = []
        r_sq = radius * radius
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                for entity in self.grid.get((cx, cy), []):
                    dx = entity.x - x
                    dy = entity.y - y
                    if dx * dx + dy * dy <= r_sq:
                        results.append(entity)
        return results
```

---

## 4. Visual Polish & "Juice" Techniques

### A. Screen Shake
```python
import random

class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.shake_duration = 0.0
        self.shake_intensity = 0.0

    def trigger_shake(self, intensity: float = 6.0, duration: float = 0.2):
        self.shake_intensity = intensity
        self.shake_duration = duration

    def update(self, dt: float):
        if self.shake_duration > 0:
            self.shake_duration -= dt
            self.offset.x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.offset.y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.offset = pygame.Vector2(0, 0)
```

### B. Flash on Damage (White/Red Hit Effect)
```python
def create_tinted_surface(source_surf: pygame.Surface, tint_color: tuple) -> pygame.Surface:
    """Creates a flash surface preserving alpha."""
    tinted = source_surf.copy()
    tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted
```

---

## 5. Performance Checklist
- [x] Call `.convert_alpha()` on every loaded image/surface immediately after loading.
- [x] Avoid creating `pygame.font.Font` instances inside the game loop; cache them in an `AssetManager`.
- [x] Use integer coordinates `int(x), int(y)` only during `surface.blit()`, maintaining `float` coordinates for physics and logic.
- [x] Pre-render static UI backgrounds and composite dynamic elements over them.
- [x] Set `SDL_VIDEODRIVER="dummy"` and `SDL_AUDIODRIVER="dummy"` when running automated CI/unit tests.
