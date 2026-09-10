---
name: spritesheet-animation-pipeline
description: >-
  Pipeline, slicing algorithms, and animation state machines for 8-directional 2D pixel art spritesheets in Pygame.
  Use this skill when importing character and creature sprite sheets, calculating frame rectangles,
  implementing 8-directional movement animations (idle, walk, run, sit, hurt, death), dynamic drop shadows,
  hit flash tints, and graceful fallback rendering.
---

# Spritesheet & 8-Directional Animation Pipeline

This skill guides the extraction, caching, and playback of 2D character spritesheets and creature animations (e.g., Minifantasy creatures, 8-directional feline sheets).

---

## 1. 8-Directional Angle Mapping

Convert 2D velocity $(v_x, v_y)$ into an 8-direction index ($0$ to $7$) with optimal sector boundaries:

```python
import math

# Direction names mapping (Clockwise from South/Down or East/Right)
DIRECTIONS_8 = [
    "down",       # 0: ~270° (or -90° / South)
    "down_right", # 1: ~315°
    "right",      # 2: 0° (East)
    "up_right",   # 3: ~45°
    "up",         # 4: 90° (North)
    "up_left",    # 5: ~135°
    "left",       # 6: 180° (West)
    "down_left"   # 7: ~225°
]

def get_8_direction(vx: float, vy: float) -> str:
    """Calculates the 8-directional orientation string from velocity vector."""
    if abs(vx) < 0.001 and abs(vy) < 0.001:
        return "down" # Default orientation
    
    # Angle in radians (-pi to pi), 0 is (1, 0) Right, pi/2 is (0, 1) Down in screen coordinates
    angle = math.atan2(vy, vx)
    # Convert to degrees (0 to 360)
    deg = (math.degrees(angle) + 360) % 360
    
    # 8 sectors of 45 degrees each, offset by 22.5 to center sectors
    sector = int((deg + 22.5) // 45) % 8
    
    mapping = {
        0: "right",
        1: "down_right",
        2: "down",
        3: "down_left",
        4: "left",
        5: "up_left",
        6: "up",
        7: "up_right"
    }
    return mapping[sector]
```

---

## 2. Spritesheet Grid Slicing & Frame Extraction

Always load spritesheets, extract frames into individual `pygame.Surface` instances with `.convert_alpha()`, and cache them in memory:

```python
import pygame
from typing import List, Dict

def slice_spritesheet(
    sheet_surface: pygame.Surface, 
    frame_width: int, 
    frame_height: int, 
    rows: int, 
    cols: int,
    scale: float = 1.0
) -> List[List[pygame.Surface]]:
    """Slices a grid spritesheet into a 2D matrix of [row][col] surfaces."""
    frames_grid = []
    
    for row in range(rows):
        row_frames = []
        for col in range(cols):
            rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
            sub_surf = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            sub_surf.blit(sheet_surface, (0, 0), rect)
            
            if scale != 1.0:
                new_w = int(frame_width * scale)
                new_h = int(frame_height * scale)
                sub_surf = pygame.transform.scale(sub_surf, (new_w, new_h))
                
            row_frames.append(sub_surf.convert_alpha())
        frames_grid.append(row_frames)
        
    return frames_grid
```

---

## 3. Dynamic Drop Shadow Renderer

A smooth procedural ellipse shadow grounds characters in the 2D world:

```python
def draw_drop_shadow(
    surface: pygame.Surface, 
    center_x: int, 
    center_y: int, 
    radius_x: int = 18, 
    radius_y: int = 8, 
    alpha: int = 100
):
    """Draws a soft translucent oval shadow under the entity."""
    shadow_surf = pygame.Surface((radius_x * 2, radius_y * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(
        shadow_surf, 
        (0, 0, 0, alpha), 
        (0, 0, radius_x * 2, radius_y * 2)
    )
    surface.blit(shadow_surf, (center_x - radius_x, center_y - radius_y))
```

---

## 4. Flash On Hit & White Shaders

When an entity takes damage, brief 60-100ms white/red flash provides instant feedback:

```python
def get_flash_frame(frame: pygame.Surface, flash_color: tuple = (255, 255, 255)) -> pygame.Surface:
    """Generates an instantaneous silhouette flash preserving alpha transparency."""
    flash = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
    flash.fill((flash_color[0], flash_color[1], flash_color[2], 255))
    flash.blit(frame, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return flash
```

---

## 5. Graceful Geometric Fallbacks

When asset files are absent, always render stylish geometric neon shapes so development and testing never crash:
- **Hero**: Cyan Neon Rounded Cube with glowing border.
- **Basic Enemy**: Red Square with pulsing outline.
- **Fast Enemy**: Orange Diamond / Sharp Triangle.
- **Tank Enemy**: Purple Hexagon / Large Rounded Box.
