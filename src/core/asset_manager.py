"""
Gerenciador de fontes, sprites de personagens (Cats & Minifantasy) e renderização gráfica.
"""
import os
import pygame
from typing import Dict, Tuple, Optional, List
from src.core.constants import (
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
)


class AssetManager:
    """Gerencia fontes de sistema, spritesheets animados (Gatos e Criaturas) e utilitários visuais."""

    # Mapeamento de direções para índice de linha no spritesheet de gatos
    CAT_DIRECTION_ROWS = {
        "down": 1,
        "down_left": 3,
        "left": 5,
        "up_left": 7,
        "up": 9,
        "up_right": 11,
        "right": 13,
        "down_right": 15,
 
    }

    # Mapeamento de colunas de animação no spritesheet de gatos (start_col, frame_count)
    CAT_ANIM_COLS = {
        "sit": (0, 4),
        "look": (4, 4),
        "lay": (8, 4),
        "walk": (12, 4),
        "run": (16, 4),
        "run_fast": (20, 4),
        "beg": (24, 4),
    }

    def __init__(self):
        self.fonts: Dict[Tuple[str, int, bool], pygame.font.Font] = {}
        self.cat_cache: Dict[Tuple[str, str, str, Tuple[int, int]], List[pygame.Surface]] = {}
        self.enemy_cache: Dict[Tuple[str, str, Tuple[int, int]], List[pygame.Surface]] = {}
        self.raw_sheets: Dict[str, pygame.Surface] = {}
        self.shadow_cache: Dict[Tuple[int, int, int], pygame.Surface] = {}
        self.bg_cache: Dict[Tuple[int, int], pygame.Surface] = {}

        # Determina os caminhos base para os assets
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.cats_dir = os.path.join(base_dir, "Cats Download", "Cats Download")
        if not os.path.exists(self.cats_dir):
            self.cats_dir = os.path.join(base_dir, "Cats Download")

        self.minifantasy_dir = os.path.join(
            base_dir,
            "Minifantasy_Creatures_v3.3_Free_Version",
            "Minifantasy_Creatures_v3.3_Free_Version",
            "Minifantasy_Creatures_Assets"
        )

        self.bg_path = os.path.join(base_dir, "BG.jpg")
        if not os.path.exists(self.bg_path):
            # Tenta buscar com outras extensões ou nomes se necessário
            for alt_name in ["BG.png", "bg.jpg", "bg.png", "background.jpg", "background.png"]:
                alt_path = os.path.join(base_dir, alt_name)
                if os.path.exists(alt_path):
                    self.bg_path = alt_path
                    break

        pygame.font.init()

    def get_background(self, size: Tuple[int, int] = (1280, 720)) -> Optional[pygame.Surface]:
        """Retorna o plano de fundo do jogo (BG.jpg) redimensionado e em cache."""
        if size in self.bg_cache:
            return self.bg_cache[size]

        if not os.path.exists(self.bg_path):
            return None

        try:
            raw_bg = pygame.image.load(self.bg_path).convert()
            scaled_bg = pygame.transform.scale(raw_bg, size)
            self.bg_cache[size] = scaled_bg
            return scaled_bg
        except Exception:
            return None

    def get_font(self, size: int = 24, bold: bool = False, font_name: Optional[str] = None) -> pygame.font.Font:
        """Obtém ou cria uma fonte em cache com tamanho e peso especificados."""
        key = (font_name or "default", size, bold)
        if key in self.fonts:
            return self.fonts[key]

        font = None
        candidate_fonts = ["segoeui", "trebuchetms", "arial", "helvetica", "dejavusans"]
        if font_name:
            candidate_fonts.insert(0, font_name)

        for candidate in candidate_fonts:
            try:
                font = pygame.font.SysFont(candidate, size, bold=bold)
                if font:
                    break
            except Exception:
                continue

        if not font:
            font = pygame.font.Font(None, size)
            if bold:
                font.set_bold(True)

        self.fonts[key] = font
        return font

    def render_text(
        self,
        surface: pygame.Surface,
        text: str,
        pos: Tuple[int, int],
        size: int = 24,
        color: Tuple[int, int, int] = COLOR_TEXT_LIGHT,
        bold: bool = False,
        align: str = "topleft",
        shadow: bool = True,
        shadow_color: Tuple[int, int, int] = (0, 0, 0),
        shadow_offset: Tuple[int, int] = (2, 2)
    ) -> pygame.Rect:
        """Renderiza texto com opção de sombra suave e alinhamento flexível."""
        font = self.get_font(size=size, bold=bold)

        if shadow:
            shadow_surf = font.render(text, True, shadow_color)
            shadow_rect = shadow_surf.get_rect(**{align: (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1])})
            surface.blit(shadow_surf, shadow_rect)

        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(**{align: pos})
        surface.blit(text_surf, text_rect)
        return text_rect

    def get_cat_frames(
        self,
        cat_name: str = "blue_0",
        action: str = "run",
        direction: str = "down",
        scale: Tuple[int, int] = (44, 44)
    ) -> List[pygame.Surface]:
        """
        Retorna uma lista de quadros animados (pygame.Surface) para o gato especificado,
        na ação e direção desejadas, redimensionados para a escala indicada.
        """
        direction = direction.lower()
        if direction not in self.CAT_DIRECTION_ROWS:
            direction = "down"

        action = action.lower()
        if action not in self.CAT_ANIM_COLS:
            action = "run"

        cache_key = (cat_name, action, direction, scale)
        if cache_key in self.cat_cache:
            return self.cat_cache[cache_key]

        # Carrega o spritesheet se ainda não carregado
        sheet_path = os.path.join(self.cats_dir, f"{cat_name}.png")
        if not os.path.exists(sheet_path):
            # Tenta fallback para blue_0 ou qualquer .png disponível
            sheet_path = os.path.join(self.cats_dir, "blue_0.png")

        if not os.path.exists(sheet_path):
            return []

        if sheet_path not in self.raw_sheets:
            try:
                self.raw_sheets[sheet_path] = pygame.image.load(sheet_path).convert_alpha()
            except Exception:
                return []

        sheet = self.raw_sheets[sheet_path]
        row_idx = self.CAT_DIRECTION_ROWS[direction]
        start_col, count = self.CAT_ANIM_COLS[action]

        frames: List[pygame.Surface] = []
        cell_size = 32
        for i in range(count):
            c = start_col + i
            rect = pygame.Rect(c * cell_size, row_idx * cell_size, cell_size, cell_size)
            try:
                sub = sheet.subsurface(rect)
                if scale != (cell_size, cell_size):
                    scaled = pygame.transform.scale(sub, scale)
                else:
                    scaled = sub
                frames.append(scaled)
            except Exception:
                continue

        if frames:
            self.cat_cache[cache_key] = frames
        return frames

    def get_enemy_frames(
        self,
        enemy_type: str = "basic",
        action: str = "walk",
        scale: Tuple[int, int] = (36, 36)
    ) -> List[pygame.Surface]:
        """
        Retorna quadros animados para os tipos de inimigos e chefes baseados no pacote Minifantasy Creatures.
        """
        cache_key = (enemy_type, action, scale)
        if cache_key in self.enemy_cache:
            return self.enemy_cache[cache_key]

        img_path = None
        if enemy_type == "boss_minotaur":
            if action == "attack":
                img_path = os.path.join(self.minifantasy_dir, "Monsters", "Minotaur", "MinotaurAttack.png")
            else:
                img_path = os.path.join(self.minifantasy_dir, "Monsters", "Minotaur", "MinotaurWalk.png")
        elif enemy_type == "boss_cyclop":
            if action == "attack":
                img_path = os.path.join(self.minifantasy_dir, "Monsters", "Cyclop", "CyclopAttack.png")
            else:
                img_path = os.path.join(self.minifantasy_dir, "Monsters", "Cyclop", "CyclopWalk.png")
        elif enemy_type == "slime_mother":
            img_path = os.path.join(self.minifantasy_dir, "Slimes", "Green_Mother_Slime", "MotherSlimeGreenJumpAttack.png")
            if not os.path.exists(img_path or ""):
                img_path = os.path.join(self.minifantasy_dir, "Slimes", "Green_Mother_Slime", "MotherSlimeGreenIdle.png")
        elif enemy_type == "slime":
            img_path = os.path.join(self.minifantasy_dir, "Slimes", "Green_Slime", "SlimeGreenJumpAttack.png")
            if not os.path.exists(img_path or ""):
                img_path = os.path.join(self.minifantasy_dir, "Slimes", "Green_Slime", "SlimeGreenIdle.png")
        elif enemy_type == "fast":
            # Morcego
            img_path = os.path.join(self.minifantasy_dir, "Beasts", "Bat", "BatFlyIdle.png")
        elif enemy_type == "tank":
            # Troll
            img_path = os.path.join(self.minifantasy_dir, "Monsters", "Troll", "TrollWalk.png")
        else:  # basic
            # Lobo
            img_path = os.path.join(self.minifantasy_dir, "Beasts", "Wolf", "WolfJump.png")

        if not img_path or not os.path.exists(img_path):
            return []

        if img_path not in self.raw_sheets:
            try:
                self.raw_sheets[img_path] = pygame.image.load(img_path).convert_alpha()
            except Exception:
                return []

        sheet = self.raw_sheets[img_path]
        frames: List[pygame.Surface] = []
        cell_size = 32
        frame_count = max(1, sheet.get_width() // cell_size)

        # Linha 0 (Front / Facing camera)
        for i in range(frame_count):
            rect = pygame.Rect(i * cell_size, 0, cell_size, min(cell_size, sheet.get_height()))
            try:
                sub = sheet.subsurface(rect)
                if scale != (cell_size, cell_size):
                    scaled = pygame.transform.scale(sub, scale)
                else:
                    scaled = sub
                frames.append(scaled)
            except Exception:
                continue

        if frames:
            self.enemy_cache[cache_key] = frames
        return frames

    def draw_shadow(
        self,
        surface: pygame.Surface,
        center_x: int,
        center_y: int,
        radius_x: int = 14,
        radius_y: int = 6,
        alpha: int = 70
    ) -> None:
        """Desenha uma sombra elíptica suave e translúcida sob o personagem/entidade."""
        key = (radius_x, radius_y, alpha)
        if key not in self.shadow_cache:
            shadow_surf = pygame.Surface((radius_x * 2, radius_y * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, alpha), shadow_surf.get_rect())
            self.shadow_cache[key] = shadow_surf

        shadow = self.shadow_cache[key]
        surface.blit(shadow, (center_x - radius_x, center_y - radius_y))

    @staticmethod
    def draw_styled_cube(
        surface: pygame.Surface,
        rect: pygame.Rect,
        base_color: Tuple[int, int, int],
        border_color: Optional[Tuple[int, int, int]] = None,
        glow: bool = True,
        border_width: int = 2
    ) -> None:
        """Desenha um cubo colorido estilizado com brilho sutil e face destacada (fallback / UI)."""
        if glow:
            glow_surf = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            glow_color = (*base_color[:3], 45)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=6)
            surface.blit(glow_surf, (rect.x - 6, rect.y - 6))

        pygame.draw.rect(surface, base_color, rect, border_radius=4)

        highlight_color = (
            min(255, int(base_color[0] * 1.35)),
            min(255, int(base_color[1] * 1.35)),
            min(255, int(base_color[2] * 1.35))
        )
        inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, max(2, rect.width - 4), max(2, int(rect.height * 0.35)))
        pygame.draw.rect(surface, highlight_color, inner_rect, border_radius=2)

        b_color = border_color or (
            max(0, int(base_color[0] * 0.6)),
            max(0, int(base_color[1] * 0.6)),
            max(0, int(base_color[2] * 0.6))
        )
        pygame.draw.rect(surface, b_color, rect, width=border_width, border_radius=4)

