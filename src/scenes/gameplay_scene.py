"""
Cena de Gameplay do Bullet Heaven (Purr Survivors: Cats vs Dogs)
Com personagens e chefes animados, sistema de combate automático,
progressão dinâmica baseada em TEMPO DE JOGO e NÍVEL DO PERSONAGEM,
chefes de fase (Minotauro Furioso e Ciclope Colossal) com barras de vida,
baús de recompensas lendários, separação física suave de inimigos e HUD reformulada.
"""
import math
import random
import pygame
from typing import List, Tuple, Dict, Any, Optional, TYPE_CHECKING
from src.scenes.base_scene import BaseScene
from src.ui.components import Button, Panel, UpgradeCard
from src.core.skin_catalog import get_skin, POWER_DEFINITIONS
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG_DARK,
    COLOR_PLAYER_CUBE,
    COLOR_ENEMY_BASIC,
    COLOR_ENEMY_FAST,
    COLOR_ENEMY_TANK,
    COLOR_ENEMY_SLIME,
    COLOR_ENEMY_BOSS,
    COLOR_PROJECTILE,
    COLOR_BOSS_PROJECTILE,
    COLOR_XP_GEM,
    COLOR_GOLD_COIN,
    COLOR_CHEST,
    COLOR_WARNING,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_GOLD,
    COLOR_CYAN,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_PURPLE,
)

if TYPE_CHECKING:
    from src.core.engine import GameEngine


class DamageNumber:
    """Texto flutuante com valor de dano ou ouro obtido com dispersão para não sobrepor."""

    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int], is_crit: bool = False):
        self.x = x + random.uniform(-14.0, 14.0)
        self.y = y + random.uniform(-6.0, 6.0)
        self.text = text
        self.color = color
        self.is_crit = is_crit
        self.lifetime = 0.85
        self.age = 0.0
        self.vy = -45.0 if not is_crit else -60.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.y += self.vy * dt
        self.vy *= math.pow(0.15, dt)
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        font_size = 22 if self.is_crit else 17
        asset_mgr.render_text(
            surface,
            self.text,
            (int(self.x + offset[0]), int(self.y + offset[1])),
            size=font_size,
            color=self.color,
            bold=True,
            align="center",
            shadow=True
        )


class Projectile:
    """Projétil disparado pelo jogador em direção aos inimigos."""

    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: int = 25, speed: float = 460.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.radius = 6

        dx = target_x - x
        dy = target_y - y
        dist = max(0.001, math.hypot(dx, dy))
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.lifetime = 2.0
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        rect = pygame.Rect(
            int(self.x + offset[0] - self.radius),
            int(self.y + offset[1] - self.radius),
            self.radius * 2,
            self.radius * 2
        )
        asset_mgr.draw_styled_cube(surface, rect, COLOR_PROJECTILE, glow=True)


class BossProjectile:
    """Projétil disparado por chefes de fase em direção ao jogador ou em padrões radiais."""

    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: int = 18, speed: float = 240.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.radius = 8

        dx = target_x - x
        dy = target_y - y
        dist = max(0.001, math.hypot(dx, dy))
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.lifetime = 4.0
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        margin = 60
        if self.x < -margin or self.x > SCREEN_WIDTH + margin or self.y < -margin or self.y > SCREEN_HEIGHT + margin:
            return False

        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        draw_x = int(self.x + offset[0])
        draw_y = int(self.y + offset[1])

        # Halo luminoso carmesim
        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (239, 68, 68, 80), (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow_surf, (draw_x - self.radius * 2, draw_y - self.radius * 2))

        pygame.draw.circle(surface, (255, 220, 220), (draw_x, draw_y), self.radius)
        pygame.draw.circle(surface, COLOR_RED, (draw_x, draw_y), self.radius, width=2)


class MegaBeamProjectile:
    """Projétil gigante que perfura múltiplos inimigos."""

    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, damage: int = 65, speed: float = 680.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.radius = 18
        dist = max(0.001, math.hypot(dir_x, dir_y))
        self.vx = (dir_x / dist) * speed
        self.vy = (dir_y / dist) * speed
        self.lifetime = 2.5
        self.age = 0.0
        self.hit_enemies = set()

    def update(self, dt: float) -> bool:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        margin = 80
        if self.x < -margin or self.x > SCREEN_WIDTH + margin or self.y < -margin or self.y > SCREEN_HEIGHT + margin:
            return False

        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        draw_x = int(self.x + offset[0])
        draw_y = int(self.y + offset[1])

        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 235, 235, 75), (self.radius * 2, self.radius * 2), self.radius * 2)
        pygame.draw.circle(glow_surf, (255, 255, 255, 120), (self.radius * 2, self.radius * 2), int(self.radius * 1.3))
        surface.blit(glow_surf, (draw_x - self.radius * 2, draw_y - self.radius * 2))

        pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), self.radius)
        pygame.draw.circle(surface, COLOR_CYAN, (draw_x, draw_y), self.radius, width=3)


class Enemy:
    """Inimigo com animação Minifantasy, escalonamento dinâmico e separação física."""

    def __init__(self, x: float, y: float, enemy_type: str = "basic", scaling: float = 1.0):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.scaling = scaling
        self.is_boss = False
        self.anim_time = random.uniform(0.0, 1.0)
        self.facing_left = False
        self.flash_timer = 0.0

        # Configura atributos por espécie
        if enemy_type == "fast":  # Morcego
            self.size = 22
            base_hp = 32
            base_speed = 175.0
            self.damage = int(8 + scaling * 2)
            self.color = COLOR_ENEMY_FAST
            self.xp_value = int(16 * max(1.0, scaling * 0.8))
            self.sprite_scale = (36, 36)
        elif enemy_type == "tank":  # Troll
            self.size = 38
            base_hp = 160
            base_speed = 68.0
            self.damage = int(24 + scaling * 4)
            self.color = COLOR_ENEMY_TANK
            self.xp_value = int(45 * max(1.0, scaling * 0.8))
            self.sprite_scale = (54, 54)
        elif enemy_type == "slime_mother":  # Slime Mãe (divide ao morrer)
            self.size = 42
            base_hp = 180
            base_speed = 62.0
            self.damage = int(16 + scaling * 3)
            self.color = COLOR_ENEMY_SLIME
            self.xp_value = int(50 * max(1.0, scaling * 0.8))
            self.sprite_scale = (56, 56)
        elif enemy_type == "slime":  # Slime pequeno
            self.size = 18
            base_hp = 28
            base_speed = 135.0
            self.damage = int(7 + scaling * 1.5)
            self.color = COLOR_ENEMY_SLIME
            self.xp_value = int(12 * max(1.0, scaling * 0.8))
            self.sprite_scale = (28, 28)
        else:  # basic (Lobo)
            self.size = 32
            base_hp = 55
            base_speed = 110.0
            self.damage = int(12 + scaling * 2.5)
            self.color = COLOR_ENEMY_BASIC
            self.xp_value = int(20 * max(1.0, scaling * 0.8))
            self.sprite_scale = (100, 100)

        # Aplica escalonamento de vida e velocidade suave
        self.max_hp = int(base_hp * scaling)
        self.hp = self.max_hp
        self.speed = min(base_speed * 1.4, base_speed * (1.0 + (scaling - 1.0) * 0.12))
        self.melee_hit_cooldown = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)

    def update(self, dt: float, player_x: float, player_y: float) -> None:
        if self.melee_hit_cooldown > 0.0:
            self.melee_hit_cooldown = max(0.0, self.melee_hit_cooldown - dt)

        if self.flash_timer > 0.0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

        dx = player_x - self.x
        dy = player_y - self.y
        dist = max(0.001, math.hypot(dx, dy))
        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

        if dx < -2:
            self.facing_left = True
        elif dx > 2:
            self.facing_left = False

        self.anim_time += dt

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        draw_x = int(self.x + offset[0])
        draw_y = int(self.y + offset[1])

        # Sombra suave sob o inimigo
        asset_mgr.draw_shadow(surface, draw_x, draw_y + self.size // 3, radius_x=int(self.size * 0.6), radius_y=6, alpha=60)

        frames = asset_mgr.get_enemy_frames(self.enemy_type, action="walk", scale=self.sprite_scale)
        if frames:
            fps = 8.0 if self.enemy_type != "fast" else 10.0
            frame_idx = int(self.anim_time * fps) % len(frames)
            frame = frames[frame_idx]
            if self.facing_left:
                frame = pygame.transform.flip(frame, True, False)
            rect = frame.get_rect(center=(draw_x, draw_y))
            surface.blit(frame, rect)
        else:
            shifted_rect = pygame.Rect(draw_x - self.size // 2, draw_y - self.size // 2, self.size, self.size)
            asset_mgr.draw_styled_cube(surface, shifted_rect, self.color, glow=False)

        # Barra de vida se sofreu dano
        if self.hp < self.max_hp:
            bar_w = max(self.size, 28)
            bar_h = 4
            bar_x = draw_x - bar_w // 2
            bar_y = draw_y - self.sprite_scale[1] // 2 - 4
            pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            hp_w = max(0, int(bar_w * (self.hp / self.max_hp)))
            pygame.draw.rect(surface, COLOR_RED, (bar_x, bar_y, hp_w, bar_h), border_radius=2)


class BossEnemy(Enemy):
    """Chefe de fase monumental com ataques especiais, barra de vida de topo e padrões de IA."""

    def __init__(self, x: float, y: float, boss_type: str = "boss_minotaur", scaling: float = 1.0):
        super().__init__(x, y, enemy_type=boss_type, scaling=scaling)
        self.is_boss = True
        self.boss_type = boss_type
        self.action = "walk"

        # Variáveis de ataques especiais
        self.attack_timer = 0.0
        self.is_charging = False
        self.charge_windup = 0.0
        self.charge_dir = (0.0, 0.0)
        self.summon_cooldown = 12.0
        self.summon_timer = 0.0
        self.is_enraged = False

        if boss_type == "boss_cyclop":
            self.name = "CICLOPE COLOSSAL"
            self.title = "O Tirano do Olho de Fogo"
            self.size = 62
            base_hp = 2200
            self.speed = 65.0
            self.damage = int(45 + scaling * 6)
            self.color = COLOR_ENEMY_BOSS
            self.xp_value = 800
            self.sprite_scale = (110, 110)
        else:  # boss_minotaur
            self.name = "MINOTAURO FURIOSO"
            self.title = "Guardião das Planícies Carmesins"
            self.size = 54
            base_hp = 1200
            self.speed = 88.0
            self.damage = int(32 + scaling * 5)
            self.color = COLOR_ENEMY_BOSS
            self.xp_value = 500
            self.sprite_scale = (96, 96)

        self.max_hp = int(base_hp * scaling)
        self.hp = self.max_hp

    def update(self, dt: float, player_x: float, player_y: float) -> None:
        if self.melee_hit_cooldown > 0.0:
            self.melee_hit_cooldown = max(0.0, self.melee_hit_cooldown - dt)

        if self.flash_timer > 0.0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

        # Checa estado enfurecido (< 50% HP)
        if self.hp < self.max_hp * 0.5 and not self.is_enraged:
            self.is_enraged = True
            self.speed *= 1.3

        self.anim_time += dt
        self.attack_timer += dt
        self.summon_timer += dt

        # --- Mecânicas do Minotauro ---
        if self.boss_type == "boss_minotaur":
            if self.is_charging:
                # Executa o avanço veloz
                self.action = "attack"
                self.x += self.charge_dir[0] * 380.0 * dt
                self.y += self.charge_dir[1] * 380.0 * dt
                self.charge_windup -= dt
                if self.charge_windup <= 0:
                    self.is_charging = False
                    self.action = "walk"
                    self.attack_timer = 0.0
                return

            elif self.charge_windup > 0:
                # Carregando investida (telegraph)
                self.action = "attack"
                self.charge_windup -= dt
                if self.charge_windup <= 0:
                    self.is_charging = True
                    self.charge_windup = 0.75  # Duração da corrida
                return

            # Gatilho de investida a cada 5.5s
            if self.attack_timer >= 5.5:
                dx = player_x - self.x
                dy = player_y - self.y
                dist = max(0.001, math.hypot(dx, dy))
                self.charge_dir = (dx / dist, dy / dist)
                self.charge_windup = 0.75  # 0.75s preparando
                self.facing_left = (self.charge_dir[0] < 0)
                return

        # Movimentação padrão em direção ao jogador
        dx = player_x - self.x
        dy = player_y - self.y
        dist = max(0.001, math.hypot(dx, dy))
        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

        if dx < -2:
            self.facing_left = True
        elif dx > 2:
            self.facing_left = False

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        draw_x = int(self.x + offset[0])
        draw_y = int(self.y + offset[1])

        # Aura pulsante carmesim de chefe
        aura_radius = int(self.size * 0.9 + math.sin(self.anim_time * 6.0) * 4)
        aura_surf = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        aura_alpha = 90 if self.is_enraged else 50
        pygame.draw.circle(aura_surf, (*COLOR_RED[:3], aura_alpha), (aura_radius, aura_radius), aura_radius)
        surface.blit(aura_surf, (draw_x - aura_radius, draw_y - aura_radius))

        # Linha de alerta vermelho se estiver preparando investida
        if self.charge_windup > 0 and not self.is_charging:
            end_line_x = draw_x + int(self.charge_dir[0] * 350)
            end_line_y = draw_y + int(self.charge_dir[1] * 350)
            pygame.draw.line(surface, (239, 68, 68, 180), (draw_x, draw_y), (end_line_x, end_line_y), width=3)

        # Sombra gigante
        asset_mgr.draw_shadow(surface, draw_x, draw_y + self.size // 3, radius_x=int(self.size * 0.75), radius_y=10, alpha=90)

        frames = asset_mgr.get_enemy_frames(self.boss_type, action=self.action, scale=self.sprite_scale)
        if frames:
            fps = 9.0
            frame_idx = int(self.anim_time * fps) % len(frames)
            frame = frames[frame_idx]
            if self.facing_left:
                frame = pygame.transform.flip(frame, True, False)
            rect = frame.get_rect(center=(draw_x, draw_y))
            surface.blit(frame, rect)
        else:
            shifted_rect = pygame.Rect(draw_x - self.size // 2, draw_y - self.size // 2, self.size, self.size)
            asset_mgr.draw_styled_cube(surface, shifted_rect, self.color, glow=True)


class DropItem:
    """Itens coletáveis caídos (Gemas de XP, Ouro e Baú Lendário de Chefe)."""

    def __init__(self, x: float, y: float, item_type: str = "xp", value: int = 10):
        self.x = x
        self.y = y
        self.item_type = item_type  # 'xp', 'gold', 'chest'
        self.value = value
        self.anim_time = random.uniform(0.0, 2.0)

        if item_type == "chest":
            self.size = 28
            self.color = COLOR_CHEST
        elif item_type == "gold":
            self.size = 12
            self.color = COLOR_GOLD_COIN
        else:
            self.size = 12
            self.color = COLOR_XP_GEM

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)

    def attract_towards(self, target_x: float, target_y: float, speed: float, dt: float) -> None:
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(0.001, math.hypot(dx, dy))
        self.x += (dx / dist) * speed * dt
        self.y += (dy / dist) * speed * dt

    def draw(self, surface: pygame.Surface, asset_mgr, offset: Tuple[int, int] = (0, 0)) -> None:
        self.anim_time += 0.016
        draw_x = int(self.x + offset[0])
        draw_y = int(self.y + offset[1])

        if self.item_type == "chest":
            # Baú Lendário com anel de luz dourada
            pulse = math.sin(self.anim_time * 5.0) * 3
            aura_size = int(self.size + 14 + pulse)
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 204, 0, 70), (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (draw_x - aura_size, draw_y - aura_size))

            chest_rect = pygame.Rect(draw_x - self.size // 2, draw_y - self.size // 2, self.size, self.size)
            asset_mgr.draw_styled_cube(surface, chest_rect, COLOR_CHEST, glow=True)

            # Etiqueta de Baú
            asset_mgr.render_text(
                surface,
                "👑 BAÚ LENDÁRIO",
                (draw_x, draw_y - 20),
                size=14,
                color=COLOR_GOLD,
                bold=True,
                align="center",
                shadow=True
            )
        else:
            shifted_rect = pygame.Rect(draw_x - self.size // 2, draw_y - self.size // 2, self.size, self.size)
            asset_mgr.draw_styled_cube(surface, shifted_rect, self.color, glow=True)


class GameplayScene(BaseScene):
    """Cena principal de combate e sobrevivência com progressão contínua e chefes de fase."""

    def __init__(self, engine: "GameEngine"):
        super().__init__(engine)
        self.is_paused = False
        self.game_over = False
        self.is_leveling_up = False

        # Animação e Sprite do Protagonista (Gatinho Selecionado)
        self.cat_name = self.engine.save_manager.get_selected_skin()
        self.cat_skin_info = get_skin(self.cat_name)
        self.cat_power = self.cat_skin_info.power_id

        # Estado do Jogador
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_size = 28
        self.player_speed = 220.0
        self.player_max_hp = 200 if self.cat_power == "brawler" else 100
        self.player_hp = self.player_max_hp
        self.player_damage = 25
        self.player_level = 1
        self.player_xp = 0
        self.player_xp_to_next = 50
        self.pickup_radius = 130.0
        self.ability_cooldown_timer = 0.0
        self.radiation_tick_timer = 0.0
        self.radiation_aura_radius = 150.0
        self.player_facing_dir = "down"
        self.player_action = "sit"
        self.player_anim_time = 0.0
        self.player_idle_switch_timer = 0.0
        self.player_is_moving = False
        self.player_sprite_scale = (44, 44)

        # Mapeamento de direções para vetores
        self.DIR_VECTORS = {
            "down": (0.0, 1.0),
            "down_left": (-0.7071, 0.7071),
            "left": (-1.0, 0.0),
            "up_left": (-0.7071, -0.7071),
            "up": (0.0, -1.0),
            "up_right": (0.7071, -0.7071),
            "right": (1.0, 0.0),
            "down_right": (0.7071, 0.7071),
        }

        # Contadores de Melhorias
        self.hp_regen_accumulator = 0.0
        self.upgrade_counts = {
            "hp": 0,
            "damage": 0,
            "attack_speed": 0,
            "move_speed": 0,
            "hp_regen": 0
        }

        # Estatísticas da Partida
        self.time_survived = 0.0
        self.score = 0
        self.kills = 0
        self.gold_earned = 0

        # Entidades
        self.projectiles: List[Projectile] = []
        self.mega_beams: List[MegaBeamProjectile] = []
        self.boss_projectiles: List[BossProjectile] = []
        self.enemies: List[Enemy] = []
        self.drops: List[DropItem] = []
        self.damage_numbers: List[DamageNumber] = []
        self.upgrade_cards: List[UpgradeCard] = []

        # Chefes e Marcos de Spawn
        self.active_boss: Optional[BossEnemy] = None
        self.boss_milestones_triggered = set()
        self.boss_warning_timer = 0.0
        self.boss_warning_text = ""

        # Tremor de Tela (Screen Shake)
        self.screen_shake_timer = 0.0
        self.screen_shake_intensity = 0.0

        # Timers de Combate e Spawn
        self.attack_cooldown = 0.45
        self.attack_timer = 0.0
        self.spawn_timer = 0.0
        self.invulnerable_timer = 0.0

        self._init_ui_overlays()

    def on_enter(self) -> None:
        """Reinicia os dados ao entrar na partida."""
        self.__init__(self.engine)

    def trigger_screen_shake(self, intensity: float = 6.0, duration: float = 0.25) -> None:
        """Aciona efeito de tremor na câmera."""
        if self.engine.save_manager.settings.get("screen_shake", True):
            self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)
            self.screen_shake_timer = max(self.screen_shake_timer, duration)

    def get_progression_scaling(self) -> float:
        """
        Calcula o multiplicador de dificuldade e atributos com base
        no TEMPO DE JOGO e no NÍVEL DO PERSONAGEM.
        """
        time_factor = (self.time_survived / 120.0) * 0.85
        level_factor = (self.player_level - 1) * 0.08
        return 1.0 + time_factor + level_factor

    def _init_ui_overlays(self) -> None:
        """Inicializa os menus de pausa e game over."""
        pause_w, pause_h = 420, 320
        pause_x = SCREEN_WIDTH // 2 - pause_w // 2
        pause_y = SCREEN_HEIGHT // 2 - pause_h // 2
        self.pause_panel = Panel(pygame.Rect(pause_x, pause_y, pause_w, pause_h), title="JOGO PAUSADO")

        btn_w, btn_h = 300, 48
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2

        self.btn_resume = Button(
            pygame.Rect(btn_x, pause_y + 70, btn_w, btn_h),
            "CONTINUAR",
            on_click=self._toggle_pause,
            accent_color=COLOR_GREEN,
            sound_manager=self.engine.audio_manager
        )

        self.btn_pause_settings = Button(
            pygame.Rect(btn_x, pause_y + 135, btn_w, btn_h),
            "CONFIGURAÇÕES",
            on_click=lambda: self.engine.change_scene("settings"),
            accent_color=COLOR_GOLD,
            sound_manager=self.engine.audio_manager
        )

        self.btn_pause_menu = Button(
            pygame.Rect(btn_x, pause_y + 200, btn_w, btn_h),
            "MENU PRINCIPAL",
            on_click=self._quit_to_menu,
            accent_color=COLOR_RED,
            sound_manager=self.engine.audio_manager
        )

        self.pause_buttons = [self.btn_resume, self.btn_pause_settings, self.btn_pause_menu]

        # Tela de Game Over
        go_w, go_h = 480, 380
        go_x = SCREEN_WIDTH // 2 - go_w // 2
        go_y = SCREEN_HEIGHT // 2 - go_h // 2
        self.gameover_panel = Panel(pygame.Rect(go_x, go_y, go_w, go_h), title="FIM DE JOGO")

        self.btn_retry = Button(
            pygame.Rect(btn_x, go_y + 230, btn_w, btn_h),
            "JOGAR NOVAMENTE",
            on_click=self.on_enter,
            accent_color=COLOR_CYAN,
            sound_manager=self.engine.audio_manager
        )

        self.btn_go_menu = Button(
            pygame.Rect(btn_x, go_y + 295, btn_w, btn_h),
            "MENU PRINCIPAL",
            on_click=self._quit_to_menu,
            accent_color=COLOR_GOLD,
            sound_manager=self.engine.audio_manager
        )

        self.gameover_buttons = [self.btn_retry, self.btn_go_menu]

    def _toggle_pause(self) -> None:
        if not self.game_over and not self.is_leveling_up:
            self.is_paused = not self.is_paused

    def _quit_to_menu(self) -> None:
        if not self.game_over and self.gold_earned > 0:
            self.engine.save_manager.record_run_stats(
                score=self.score,
                kills=self.kills,
                time_survived=self.time_survived,
                gold_earned=self.gold_earned
            )
        self.engine.change_scene("main_menu")

    def _trigger_game_over(self) -> None:
        """Processa a derrota e grava estatísticas no savegame."""
        self.game_over = True
        self.trigger_screen_shake(12.0, 0.5)
        self.engine.save_manager.record_run_stats(
            score=self.score,
            kills=self.kills,
            time_survived=self.time_survived,
            gold_earned=self.gold_earned
        )
        self.engine.audio_manager.play_sfx("hit")

    # --- Sistema de Level Up e Escolhas ---

    def _get_all_upgrade_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Retorna o catálogo de melhorias disponíveis no Level Up."""
        return {
            "hp": {
                "title": "Aumentar HP",
                "desc": "+25 HP Máximo\nCura +25 de Vida",
                "preview": f"HP Máx: {self.player_max_hp} -> {self.player_max_hp + 25}",
                "color": COLOR_GREEN,
                "accent": COLOR_GREEN,
                "apply": self._apply_hp_upgrade
            },
            "damage": {
                "title": "Aumentar Dano",
                "desc": "+10% Dano por Disparo\nMais impacto contra chefes",
                "preview": f"Dano: {int(self.player_damage)} -> {int(self.player_damage * 1.1)}",
                "color": COLOR_RED,
                "accent": COLOR_RED,
                "apply": self._apply_damage_upgrade
            },
            "attack_speed": {
                "title": "Velocidade de Ataque",
                "desc": "-6% Tempo de Recarga\nDisparos mais velozes",
                "preview": f"Recarga: {self.attack_cooldown:.2f}s -> {self.attack_cooldown * 0.94:.2f}s",
                "color": COLOR_GOLD,
                "accent": COLOR_GOLD,
                "apply": self._apply_attack_speed_upgrade
            },
            "move_speed": {
                "title": "Velocidade de Movimento",
                "desc": "+30 Velocidade de Corrida\nEsquiva ágil",
                "preview": f"Velocidade: {int(self.player_speed)} -> {int(self.player_speed + 30)}",
                "color": COLOR_CYAN,
                "accent": COLOR_CYAN,
                "apply": self._apply_move_speed_upgrade
            },
            "hp_regen": {
                "title": "Recuperação de HP",
                "desc": "+1% HP Máx / segundo\nRegeneração contínua de vida",
                "preview": f"Regen: {self.upgrade_counts.get('hp_regen', 0)}%/s -> {self.upgrade_counts.get('hp_regen', 0) + 1}%/s",
                "color": (34, 197, 94),
                "accent": (34, 197, 94),
                "apply": self._apply_hp_regen_upgrade
            }
        }

    def _apply_hp_upgrade(self) -> None:
        self.player_max_hp += 25
        self.player_hp = min(self.player_max_hp, self.player_hp + 25)
        self.upgrade_counts["hp"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+25 MAX HP!", COLOR_GREEN, is_crit=True))

    def _apply_damage_upgrade(self) -> None:
        self.player_damage = self.player_damage * 1.1
        self.upgrade_counts["damage"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+10% DANO!", COLOR_RED, is_crit=True))

    def _apply_attack_speed_upgrade(self) -> None:
        self.attack_cooldown = max(0.08, self.attack_cooldown * 0.94)
        self.upgrade_counts["attack_speed"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+ATK SPEED!", COLOR_GOLD, is_crit=True))

    def _apply_move_speed_upgrade(self) -> None:
        self.player_speed += 30.0
        self.upgrade_counts["move_speed"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+VELOCIDADE!", COLOR_CYAN, is_crit=True))

    def _apply_hp_regen_upgrade(self) -> None:
        self.upgrade_counts["hp_regen"] = self.upgrade_counts.get("hp_regen", 0) + 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+1% REGEN/SEG!", COLOR_GREEN, is_crit=True))

    def _trigger_level_up(self) -> None:
        """Inicia a tela de seleção de Level Up sorteando 3 das opções disponíveis."""
        self.is_leveling_up = True
        self.engine.audio_manager.play_sfx("levelup")

        all_upgrades = self._get_all_upgrade_definitions()
        chosen_keys = random.sample(list(all_upgrades.keys()), 3)

        card_w = 270
        card_h = 320
        spacing = 25
        total_w = 3 * card_w + 2 * spacing
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = SCREEN_HEIGHT // 2 - 130

        self.upgrade_cards = []
        for i, key in enumerate(chosen_keys):
            up_data = all_upgrades[key]
            card_rect = pygame.Rect(start_x + i * (card_w + spacing), card_y, card_w, card_h)

            def make_select_callback(apply_fn=up_data["apply"]):
                return lambda: self._on_upgrade_selected(apply_fn)

            card = UpgradeCard(
                rect=card_rect,
                shortcut_num=i + 1,
                upgrade_id=key,
                title=up_data["title"],
                description=up_data["desc"],
                stat_preview=up_data["preview"],
                icon_color=up_data["color"],
                accent_color=up_data["accent"],
                on_click=make_select_callback(),
                sound_manager=self.engine.audio_manager
            )
            self.upgrade_cards.append(card)

    def _on_upgrade_selected(self, apply_fn) -> None:
        """Executa a melhoria selecionada e verifica se há novo level up pendente."""
        apply_fn()

        if self.player_xp >= self.player_xp_to_next:
            self.player_level += 1
            self.player_xp -= self.player_xp_to_next
            self.player_xp_to_next = int(self.player_xp_to_next * 1.35)
            self._trigger_level_up()
        else:
            self.is_leveling_up = False
            self.upgrade_cards.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.is_leveling_up:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_1 or event.key == pygame.K_KP1) and len(self.upgrade_cards) >= 1:
                    if self.upgrade_cards[0].on_click:
                        self.upgrade_cards[0].on_click()
                    return
                elif (event.key == pygame.K_2 or event.key == pygame.K_KP2) and len(self.upgrade_cards) >= 2:
                    if self.upgrade_cards[1].on_click:
                        self.upgrade_cards[1].on_click()
                    return
                elif (event.key == pygame.K_3 or event.key == pygame.K_KP3) and len(self.upgrade_cards) >= 3:
                    if self.upgrade_cards[2].on_click:
                        self.upgrade_cards[2].on_click()
                    return

            for card in self.upgrade_cards:
                if card.handle_event(event):
                    break
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._toggle_pause()
                return
            elif event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                self._activate_special_power()
                return

        if self.game_over:
            for btn in self.gameover_buttons:
                if btn.handle_event(event):
                    break
            return

        if self.is_paused:
            for btn in self.pause_buttons:
                if btn.handle_event(event):
                    break
            return

    def _activate_special_power(self) -> None:
        """Aciona a habilidade ativa do gatinho."""
        if self.is_paused or self.game_over or self.is_leveling_up:
            return

        if self.ability_cooldown_timer > 0.0:
            return

        dir_vec = self.DIR_VECTORS.get(self.player_facing_dir, (0.0, 1.0))

        if self.cat_power == "teleport":
            blink_dist = 150.0
            new_x = self.player_x + dir_vec[0] * blink_dist
            new_y = self.player_y + dir_vec[1] * blink_dist

            half_p = self.player_size // 2
            self.player_x = max(half_p, min(SCREEN_WIDTH - half_p, new_x))
            self.player_y = max(half_p + 30, min(SCREEN_HEIGHT - half_p, new_y))

            self.invulnerable_timer = 0.35
            self.ability_cooldown_timer = 2.5
            self.engine.audio_manager.play_sfx("ui_hover")
            self.trigger_screen_shake(4.0, 0.15)
            self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 25, "⚡ TELEPORTE!", COLOR_PURPLE, is_crit=True))

        elif self.cat_power == "mega_beam":
            beam_dmg = int(self.player_damage * 2.8)
            self.mega_beams.append(
                MegaBeamProjectile(
                    self.player_x,
                    self.player_y,
                    dir_vec[0],
                    dir_vec[1],
                    damage=beam_dmg,
                    speed=700.0
                )
            )
            self.ability_cooldown_timer = 4.0
            self.engine.audio_manager.play_sfx("shoot")
            self.trigger_screen_shake(8.0, 0.2)
            self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 25, "☄️ MEGA TIRO!", COLOR_CYAN, is_crit=True))

    def _check_boss_milestones(self) -> None:
        """Gera chefes de fase monumentais com base no tempo ou nível."""
        # Chefe 1: Minotauro Furioso aos 2m (120s) ou Nível 10
        if "boss_minotaur" not in self.boss_milestones_triggered:
            if self.time_survived >= 120.0 or self.player_level >= 10:
                self.boss_milestones_triggered.add("boss_minotaur")
                scaling = self.get_progression_scaling()
                boss = BossEnemy(SCREEN_WIDTH // 2, -50, boss_type="boss_minotaur", scaling=scaling)
                self.enemies.append(boss)
                self.active_boss = boss
                self.boss_warning_timer = 3.5
                self.boss_warning_text = "⚠️ ALERTA: O MINOTAURO FURIOSO DESPERTOU! ⚠️"
                self.trigger_screen_shake(10.0, 0.8)
                self.engine.audio_manager.play_sfx("levelup")

        # Chefe 2: Ciclope Colossal aos 5m (300s) ou Nível 20
        if "boss_cyclop" not in self.boss_milestones_triggered:
            if self.time_survived >= 300.0 or self.player_level >= 20:
                self.boss_milestones_triggered.add("boss_cyclop")
                scaling = self.get_progression_scaling()
                boss = BossEnemy(SCREEN_WIDTH // 2, -60, boss_type="boss_cyclop", scaling=scaling)
                self.enemies.append(boss)
                self.active_boss = boss
                self.boss_warning_timer = 3.5
                self.boss_warning_text = "⚠️ ALERTA: O CICLOPE COLOSSAL SURGIU! ⚠️"
                self.trigger_screen_shake(14.0, 1.0)
                self.engine.audio_manager.play_sfx("levelup")

    def _spawn_wave(self, dt: float) -> None:
        """Gera ondas de inimigos com taxa e composição baseadas no Tempo e Nível."""
        self._check_boss_milestones()

        # Enquanto houver um chefe de fase ativo e vivo na arena, nenhum outro monstro novo é gerado
        if self.active_boss and self.active_boss in self.enemies and self.active_boss.hp > 0:
            return

        scaling = self.get_progression_scaling()
        max_active_enemies = min(160, int(50 + self.time_survived * 0.4 + self.player_level * 3.0))

        if len(self.enemies) >= max_active_enemies:
            return

        self.spawn_timer += dt
        spawn_interval = max(0.18, 1.6 / (1.0 + (self.time_survived / 90.0) + (self.player_level * 0.05)))

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0

            # Seleciona parede distante para evitar pop-in
            wall_distances = [
                (0, self.player_y),
                (1, SCREEN_WIDTH - self.player_x),
                (2, SCREEN_HEIGHT - self.player_y),
                (3, self.player_x)
            ]
            wall_distances.sort(key=lambda item: item[1], reverse=True)
            side = random.choice([wall_distances[0][0], wall_distances[1][0]])

            margin = 45
            if side == 0:
                sx = random.uniform(0, SCREEN_WIDTH)
                sy = -margin
            elif side == 1:
                sx = SCREEN_WIDTH + margin
                sy = random.uniform(0, SCREEN_HEIGHT)
            elif side == 2:
                sx = random.uniform(0, SCREEN_WIDTH)
                sy = SCREEN_HEIGHT + margin
            else:
                sx = -margin
                sy = random.uniform(0, SCREEN_HEIGHT)

            # Composição dinâmica da horda
            r = random.random()
            if (self.time_survived > 105 or self.player_level >= 8) and r < 0.20:
                etype = "tank"
            elif (self.time_survived > 65 or self.player_level >= 5) and r < 0.35:
                etype = "slime_mother"
            elif (self.time_survived > 30 or self.player_level >= 3) and r < 0.55:
                etype = "fast"
            else:
                etype = "basic"

            self.enemies.append(Enemy(sx, sy, enemy_type=etype, scaling=scaling))

    def _apply_enemy_separation(self) -> None:
        """Aplica repulsão suave mútua entre inimigos para evitar aglomeração em um só pixel."""
        num_enemies = len(self.enemies)
        if num_enemies < 2:
            return

        # Amostra pares vizinhos para performance O(N * k)
        for i in range(num_enemies):
            e1 = self.enemies[i]
            # Compara com os próximos 8 inimigos da lista
            for j in range(i + 1, min(i + 9, num_enemies)):
                e2 = self.enemies[j]
                dx = e1.x - e2.x
                dy = e1.y - e2.y
                dist_sq = dx * dx + dy * dy
                min_dist = (e1.size + e2.size) * 0.52
                if 0.001 < dist_sq < min_dist * min_dist:
                    dist = math.sqrt(dist_sq)
                    push = (min_dist - dist) * 0.5
                    nx = dx / dist
                    ny = dy / dist
                    # Chefes têm mais massa e não são empurrados por inimigos comuns
                    if not e1.is_boss:
                        e1.x += nx * push * 0.6
                        e1.y += ny * push * 0.6
                    if not e2.is_boss:
                        e2.x -= nx * push * 0.6
                        e2.y -= ny * push * 0.6

    def _auto_attack(self, dt: float) -> None:
        """Dispara automaticamente no inimigo mais próximo usando o dano do jogador."""
        if self.cat_power in ("ghost", "radioactive_aura"):
            return

        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            if not self.enemies:
                return

            closest_enemy = min(
                self.enemies,
                key=lambda e: math.hypot(e.x - self.player_x, e.y - self.player_y)
            )

            dist = math.hypot(closest_enemy.x - self.player_x, closest_enemy.y - self.player_y)
            if dist < 650:
                dx = closest_enemy.x - self.player_x
                dy = closest_enemy.y - self.player_y
                base_angle = math.atan2(dy, dx)

                proj_damage = self.player_damage * 0.5 if self.cat_power == "brawler" else self.player_damage

                if self.cat_power == "double_attack":
                    for angle_offset in [-0.18, 0.18]:
                        target_ang = base_angle + angle_offset
                        tx = self.player_x + math.cos(target_ang) * 500
                        ty = self.player_y + math.sin(target_ang) * 500
                        self.projectiles.append(
                            Projectile(self.player_x, self.player_y, tx, ty, damage=proj_damage)
                        )
                else:
                    self.projectiles.append(
                        Projectile(self.player_x, self.player_y, closest_enemy.x, closest_enemy.y, damage=proj_damage)
                    )

                self.engine.audio_manager.play_sfx("shoot")
                self.attack_timer = 0.0

    def update(self, dt: float) -> None:
        if self.is_leveling_up:
            for card in self.upgrade_cards:
                card.update(dt)
            return

        if self.game_over:
            for btn in self.gameover_buttons:
                btn.update(dt)
            return

        if self.is_paused:
            for btn in self.pause_buttons:
                btn.update(dt)
            return

        self.time_survived += dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        if self.boss_warning_timer > 0:
            self.boss_warning_timer = max(0.0, self.boss_warning_timer - dt)

        # Atualiza tremor de tela
        if self.screen_shake_timer > 0:
            self.screen_shake_timer = max(0.0, self.screen_shake_timer - dt)
            if self.screen_shake_timer <= 0:
                self.screen_shake_intensity = 0.0

        # Movimentação do Jogador
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1.0

        if dx != 0 or dy != 0:
            dist = math.hypot(dx, dy)
            self.player_x += (dx / dist) * self.player_speed * dt
            self.player_y += (dy / dist) * self.player_speed * dt
            self.player_is_moving = True
            self.player_action = "run"

            if dx > 0 and dy > 0:
                self.player_facing_dir = "down_right"
            elif dx < 0 and dy > 0:
                self.player_facing_dir = "down_left"
            elif dx > 0 and dy < 0:
                self.player_facing_dir = "up_right"
            elif dx < 0 and dy < 0:
                self.player_facing_dir = "up_left"
            elif dx > 0:
                self.player_facing_dir = "right"
            elif dx < 0:
                self.player_facing_dir = "left"
            elif dy > 0:
                self.player_facing_dir = "down"
            elif dy < 0:
                self.player_facing_dir = "up"
        else:
            self.player_is_moving = False
            self.player_idle_switch_timer += dt
            if self.player_idle_switch_timer > 4.5:
                self.player_action = "look"
                if self.player_idle_switch_timer > 7.5:
                    self.player_idle_switch_timer = 0.0
            else:
                self.player_action = "sit"

        self.player_anim_time += dt

        # Limita dentro da arena
        half_p = self.player_size // 2
        self.player_x = max(half_p, min(SCREEN_WIDTH - half_p, self.player_x))
        self.player_y = max(half_p + 30, min(SCREEN_HEIGHT - half_p, self.player_y))

        if self.ability_cooldown_timer > 0.0:
            self.ability_cooldown_timer = max(0.0, self.ability_cooldown_timer - dt)

        # Disparo e Spawn
        self._auto_attack(dt)
        self._spawn_wave(dt)

        # Projéteis
        self.projectiles = [p for p in self.projectiles if p.update(dt)]
        self.mega_beams = [b for b in self.mega_beams if b.update(dt)]
        self.boss_projectiles = [bp for bp in self.boss_projectiles if bp.update(dt)]

        # Separação suave mútua entre inimigos (evita sobreposição)
        self._apply_enemy_separation()

        # Ataques de Chefes
        for enemy in self.enemies:
            if isinstance(enemy, BossEnemy):
                # Ciclope dispara anel de esferas
                if enemy.boss_type == "boss_cyclop" and enemy.attack_timer >= 4.0:
                    enemy.attack_timer = 0.0
                    num_shots = 10 if enemy.is_enraged else 8
                    for i in range(num_shots):
                        ang = (i / num_shots) * 2 * math.pi + enemy.anim_time
                        tx = enemy.x + math.cos(ang) * 400
                        ty = enemy.y + math.sin(ang) * 400
                        self.boss_projectiles.append(BossProjectile(enemy.x, enemy.y, tx, ty, damage=18))
                    self.engine.audio_manager.play_sfx("shoot")
                    self.trigger_screen_shake(6.0, 0.2)

                # Minotauro desfere Pisotão Sísmico com tremor e onda de choque em área
                elif enemy.boss_type == "boss_minotaur" and enemy.summon_timer >= enemy.summon_cooldown:
                    enemy.summon_timer = 0.0
                    self.damage_numbers.append(DamageNumber(enemy.x, enemy.y - 40, "⚡ PISOTÃO SÍSMICO!", COLOR_RED, is_crit=True))
                    self.trigger_screen_shake(12.0, 0.45)
                    self.engine.audio_manager.play_sfx("hit")

                    dist_to_player = math.hypot(self.player_x - enemy.x, self.player_y - enemy.y)
                    if dist_to_player < 180.0 and self.invulnerable_timer <= 0:
                        stomp_dmg = int(enemy.damage * 0.8)
                        self.player_hp -= stomp_dmg
                        self.invulnerable_timer = 0.5
                        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 20, f"-{stomp_dmg} 💥", COLOR_RED, is_crit=True))
                        if self.player_hp <= 0:
                            self._trigger_game_over()
                            return

        # Atualiza inimigos
        player_rect = pygame.Rect(
            int(self.player_x - half_p),
            int(self.player_y - half_p),
            self.player_size,
            self.player_size
        )

        for enemy in self.enemies:
            enemy.update(dt, self.player_x, self.player_y)

            # Contato Jogador x Inimigo
            if player_rect.colliderect(enemy.rect):
                if self.invulnerable_timer <= 0:
                    damage_taken = max(1, math.ceil(enemy.damage * 0.10)) if self.cat_power == "ghost" else enemy.damage
                    self.player_hp -= damage_taken
                    self.invulnerable_timer = 0.5
                    self.trigger_screen_shake(7.0, 0.25)
                    self.engine.audio_manager.play_sfx("hit")
                    self.damage_numbers.append(
                        DamageNumber(self.player_x, self.player_y - 20, f"-{damage_taken}", COLOR_RED, is_crit=True)
                    )
                    if self.player_hp <= 0:
                        self._trigger_game_over()
                        return

                # Dano corpo-a-corpo infligido ao inimigo
                if enemy.melee_hit_cooldown <= 0.0:
                    if self.cat_power == "ghost":
                        lost_hp = max(0, self.player_max_hp - self.player_hp)
                        melee_damage = max(15, int(self.player_damage + lost_hp * 2.0))
                        enemy.hp -= melee_damage
                        enemy.melee_hit_cooldown = 0.35
                        self.damage_numbers.append(
                            DamageNumber(enemy.x, enemy.y - 14, f"{melee_damage} 👻", (192, 132, 252))
                        )
                        self.score += melee_damage
                        self.engine.audio_manager.play_sfx("hit")
                    elif self.cat_power == "brawler":
                        melee_damage = int(self.player_damage * 2.0)
                        enemy.hp -= melee_damage
                        enemy.melee_hit_cooldown = 0.35
                        self.damage_numbers.append(
                            DamageNumber(enemy.x, enemy.y - 14, f"{melee_damage} 💥", (251, 146, 60))
                        )
                        self.score += melee_damage
                        self.engine.audio_manager.play_sfx("hit")

            # Colisão Projétil Padrão x Inimigo
            for proj in self.projectiles[:]:
                p_rect = pygame.Rect(int(proj.x - 6), int(proj.y - 6), 12, 12)
                if enemy.rect.colliderect(p_rect):
                    enemy.hp -= proj.damage
                    dmg_str = f"{int(proj.damage)}"
                    self.damage_numbers.append(DamageNumber(enemy.x, enemy.y - 12, dmg_str, COLOR_GOLD))

                    if self.cat_power == "lifesteal" and self.player_hp < self.player_max_hp:
                        heal_amount = max(1, math.ceil(proj.damage * 0.05))
                        self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
                        self.damage_numbers.append(
                            DamageNumber(self.player_x, self.player_y - 22, f"+{heal_amount} HP", COLOR_GREEN)
                        )

                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    self.engine.audio_manager.play_sfx("hit")

            # Colisão Mega Beam x Inimigo
            for beam in self.mega_beams:
                b_rect = pygame.Rect(int(beam.x - beam.radius), int(beam.y - beam.radius), beam.radius * 2, beam.radius * 2)
                if enemy not in beam.hit_enemies and enemy.rect.colliderect(b_rect):
                    beam.hit_enemies.add(enemy)
                    enemy.hp -= beam.damage
                    self.damage_numbers.append(
                        DamageNumber(enemy.x, enemy.y - 14, f"{int(beam.damage)} ☄️", COLOR_CYAN, is_crit=True)
                    )
                    self.engine.audio_manager.play_sfx("hit")

        # Dano Contínuo da Aura Radioativa Gama (em todos os inimigos no raio de alcance)
        if self.cat_power == "radioactive_aura":
            self.radiation_tick_timer += dt
            if self.radiation_tick_timer >= 0.15:
                self.radiation_tick_timer = 0.0
                aura_r = self.radiation_aura_radius
                aura_r_sq = aura_r * aura_r
                aura_tick_dmg = max(3, int(self.player_damage * 0.45))
                damaged_any = False

                for enemy in self.enemies:
                    dx = enemy.x - self.player_x
                    dy = enemy.y - self.player_y
                    if dx * dx + dy * dy <= aura_r_sq:
                        enemy.hp -= aura_tick_dmg
                        damaged_any = True
                        if random.random() < 0.35:
                            self.damage_numbers.append(
                                DamageNumber(enemy.x, enemy.y - 10, f"{aura_tick_dmg} ☢️", (74, 222, 128))
                            )
                        if self.cat_power == "lifesteal" and self.player_hp < self.player_max_hp:
                            heal_amount = max(1, math.ceil(aura_tick_dmg * 0.05))
                            self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)

                if damaged_any and random.random() < 0.25:
                    self.engine.audio_manager.play_sfx("hit")

        # Colisão Projéteis de Chefe x Jogador
        for bp in self.boss_projectiles[:]:
            bp_rect = pygame.Rect(int(bp.x - bp.radius), int(bp.y - bp.radius), bp.radius * 2, bp.radius * 2)
            if player_rect.colliderect(bp_rect):
                if self.invulnerable_timer <= 0:
                    damage_taken = max(1, math.ceil(bp.damage * 0.10)) if self.cat_power == "ghost" else bp.damage
                    self.player_hp -= damage_taken
                    self.invulnerable_timer = 0.4
                    self.trigger_screen_shake(8.0, 0.25)
                    self.engine.audio_manager.play_sfx("hit")
                    self.damage_numbers.append(
                        DamageNumber(self.player_x, self.player_y - 22, f"-{damage_taken} 💥", COLOR_RED, is_crit=True)
                    )
                    if self.player_hp <= 0:
                        self._trigger_game_over()
                        return
                if bp in self.boss_projectiles:
                    self.boss_projectiles.remove(bp)

        # Inimigos Derrotados -> Pontuação Equilibrada, Drops e Divisão de Slimes
        alive_enemies = []
        new_split_slimes = []

        for enemy in self.enemies:
            if enemy.hp <= 0:
                self.kills += 1

                # Se for chefe, concede pontuação monumental + Baú Lendário + Mega Ouro
                if isinstance(enemy, BossEnemy):
                    self.score += 250
                    self.drops.append(DropItem(enemy.x, enemy.y, "chest", value=150))
                    self.drops.append(DropItem(enemy.x + 20, enemy.y, "xp", value=400))
                    self.damage_numbers.append(
                        DamageNumber(enemy.x, enemy.y - 30, "👑 CHEFE DERROTADO! 👑", COLOR_GOLD, is_crit=True)
                    )
                    self.trigger_screen_shake(15.0, 0.6)
                    self.engine.audio_manager.play_sfx("levelup")
                    if self.active_boss == enemy:
                        self.active_boss = None

                # Se for Slime Mãe, divide em 2 mini-slimes
                elif enemy.enemy_type == "slime_mother":
                    self.score += 20
                    scaling = self.get_progression_scaling()
                    for offset_ang in [-0.6, 0.6]:
                        spawn_sx = enemy.x + math.cos(offset_ang) * 22
                        spawn_sy = enemy.y + math.sin(offset_ang) * 22
                        new_split_slimes.append(Enemy(spawn_sx, spawn_sy, enemy_type="slime", scaling=scaling))
                    self.drops.append(DropItem(enemy.x, enemy.y, "xp", value=enemy.xp_value))
                    if random.random() < 0.40:
                        self.drops.append(DropItem(enemy.x + random.uniform(-10, 10), enemy.y, "gold", value=random.randint(1, 4)))

                elif enemy.enemy_type == "tank":
                    self.score += 25
                    self.drops.append(DropItem(enemy.x, enemy.y, "xp", value=enemy.xp_value))
                    if random.random() < 0.35:
                        self.drops.append(DropItem(enemy.x + random.uniform(-10, 10), enemy.y, "gold", value=random.randint(1, 4)))

                elif enemy.enemy_type == "fast":
                    self.score += 15
                    self.drops.append(DropItem(enemy.x, enemy.y, "xp", value=enemy.xp_value))
                    if random.random() < 0.30:
                        self.drops.append(DropItem(enemy.x + random.uniform(-10, 10), enemy.y, "gold", value=random.randint(1, 4)))

                else:
                    self.score += 10
                    self.drops.append(DropItem(enemy.x, enemy.y, "xp", value=enemy.xp_value))
                    if random.random() < 0.30:
                        self.drops.append(DropItem(enemy.x + random.uniform(-10, 10), enemy.y, "gold", value=random.randint(1, 4)))
            else:
                alive_enemies.append(enemy)

        self.enemies = alive_enemies + new_split_slimes

        # Atualiza status do chefe ativo se ainda está na lista
        if self.active_boss and self.active_boss not in self.enemies:
            self.active_boss = None

        # Atração e Coleta de Itens Caídos
        remaining_drops = []
        for drop in self.drops:
            dist = math.hypot(drop.x - self.player_x, drop.y - self.player_y)
            if dist < self.pickup_radius:
                drop.attract_towards(self.player_x, self.player_y, speed=380.0, dt=dt)

            if dist < self.player_size + 4:
                if drop.item_type == "chest":
                    self.score += 100
                    self.gold_earned += drop.value
                    self.player_xp += 400
                    self.engine.audio_manager.play_sfx("levelup")
                    self.damage_numbers.append(
                        DamageNumber(self.player_x, self.player_y - 35, f"+{drop.value} OURO & BAÚ!", COLOR_GOLD, is_crit=True)
                    )
                    self._trigger_level_up()
                elif drop.item_type == "gold":
                    self.score += 5
                    self.gold_earned += drop.value
                    self.engine.audio_manager.play_sfx("gem")
                    self.damage_numbers.append(
                        DamageNumber(self.player_x, self.player_y - 18, f"+{drop.value} G", COLOR_GOLD)
                    )
                elif drop.item_type == "xp":
                    self.score += 1
                    self.player_xp += drop.value
                    self.engine.audio_manager.play_sfx("gem")
                    if self.player_xp >= self.player_xp_to_next:
                        self.player_level += 1
                        self.player_xp -= self.player_xp_to_next
                        self.player_xp_to_next = int(self.player_xp_to_next * 1.35)
                        self._trigger_level_up()
                        return
            else:
                remaining_drops.append(drop)

        self.drops = remaining_drops

        # Regeneração contínua de HP
        if self.upgrade_counts.get("hp_regen", 0) > 0 and self.player_hp < self.player_max_hp:
            regen_rate = self.player_max_hp * (self.upgrade_counts["hp_regen"] * 0.01)
            self.hp_regen_accumulator += regen_rate * dt
            if self.hp_regen_accumulator >= 1.0:
                heal_pts = int(self.hp_regen_accumulator)
                self.hp_regen_accumulator -= heal_pts
                self.player_hp = min(self.player_max_hp, self.player_hp + heal_pts)

        # Atualiza números de dano
        self.damage_numbers = [d for d in self.damage_numbers if d.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        # Calcula deslocamento de screen shake
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake_timer > 0 and self.screen_shake_intensity > 0:
            shake_offset_x = int(random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity))
            shake_offset_y = int(random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity))
        cam_offset = (shake_offset_x, shake_offset_y)

        # Fundo do jogo
        bg = self.engine.asset_manager.get_background((SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg:
            surface.blit(bg, cam_offset)
        else:
            surface.fill(COLOR_BG_DARK)
            grid_size = 64
            for x in range(0, SCREEN_WIDTH, grid_size):
                pygame.draw.line(surface, (18, 16, 28), (x + cam_offset[0], 0), (x + cam_offset[0], SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, grid_size):
                pygame.draw.line(surface, (18, 16, 28), (0, y + cam_offset[1]), (SCREEN_WIDTH, y + cam_offset[1]))

        # Renderiza Drops
        for drop in self.drops:
            drop.draw(surface, self.engine.asset_manager, offset=cam_offset)

        # Renderiza Projéteis
        for proj in self.projectiles:
            proj.draw(surface, self.engine.asset_manager, offset=cam_offset)

        for beam in self.mega_beams:
            beam.draw(surface, self.engine.asset_manager, offset=cam_offset)

        for bp in self.boss_projectiles:
            bp.draw(surface, self.engine.asset_manager, offset=cam_offset)

        # Renderiza Inimigos e Chefes
        for enemy in self.enemies:
            enemy.draw(surface, self.engine.asset_manager, offset=cam_offset)

        # Renderiza Jogador
        if not self.game_over:
            p_draw_x = int(self.player_x + cam_offset[0])
            p_draw_y = int(self.player_y + cam_offset[1])

            self.engine.asset_manager.draw_shadow(
                surface,
                p_draw_x,
                p_draw_y + 12,
                radius_x=16,
                radius_y=7,
                alpha=85
            )

            # Renderiza Aura Radioativa pulsante ao redor do gatinho
            if self.cat_power == "radioactive_aura":
                pulse = math.sin(self.player_anim_time * 6.0) * 6
                curr_radius = int(self.radiation_aura_radius + pulse)

                aura_surf = pygame.Surface((curr_radius * 2, curr_radius * 2), pygame.SRCALPHA)
                # Glow de fundo verde neon
                pygame.draw.circle(aura_surf, (74, 222, 128, 32), (curr_radius, curr_radius), curr_radius)
                # Anel de energia intermediário
                pygame.draw.circle(aura_surf, (132, 204, 22, 55), (curr_radius, curr_radius), int(curr_radius * 0.75))
                # Borda externa da aura
                pygame.draw.circle(aura_surf, (163, 230, 53, 170), (curr_radius, curr_radius), curr_radius, width=2)
                surface.blit(aura_surf, (p_draw_x - curr_radius, p_draw_y - curr_radius))

            # Efeito de piscar se invulnerável
            is_visible = (self.invulnerable_timer <= 0 or int(self.invulnerable_timer * 20) % 2 == 0)
            if is_visible:
                frames = self.engine.asset_manager.get_cat_frames(
                    cat_name=self.cat_name,
                    action=self.player_action,
                    direction=self.player_facing_dir,
                    scale=self.player_sprite_scale
                )
                if frames:
                    fps = 10.0 if self.player_is_moving else 3.5
                    frame_idx = int(self.player_anim_time * fps) % len(frames)
                    frame = frames[frame_idx]
                    rect = frame.get_rect(center=(p_draw_x, p_draw_y))
                    surface.blit(frame, rect)
                else:
                    p_rect = pygame.Rect(
                        p_draw_x - self.player_size // 2,
                        p_draw_y - self.player_size // 2,
                        self.player_size,
                        self.player_size
                    )
                    self.engine.asset_manager.draw_styled_cube(surface, p_rect, COLOR_PLAYER_CUBE, glow=True)

        # Renderiza Números de Dano
        for d in self.damage_numbers:
            d.draw(surface, self.engine.asset_manager, offset=cam_offset)

        # ========================================================
        # --- HUD REESTRUTURADA (SEM SOBREPOSIÇÕES) ---
        # ========================================================

        # 1. Barra de XP no topo absoluto
        xp_ratio = min(1.0, self.player_xp / max(1, self.player_xp_to_next))
        pygame.draw.rect(surface, (20, 16, 32), (0, 0, SCREEN_WIDTH, 14))
        pygame.draw.rect(surface, COLOR_CYAN, (0, 0, int(SCREEN_WIDTH * xp_ratio), 14))

        # 2. Informações de Nível e Dificuldade (Canto superior esquerdo)
        scaling_val = self.get_progression_scaling()
        self.engine.asset_manager.render_text(
            surface,
            f"LV {self.player_level}",
            (16, 22),
            size=22,
            color=COLOR_CYAN,
            bold=True
        )
        self.engine.asset_manager.render_text(
            surface,
            f"DIFICULDADE: {scaling_val:.1f}x",
            (85, 25),
            size=14,
            color=COLOR_TEXT_MUTED,
            bold=True
        )

        # 3. Tempo de Sobrevivência (Topo Central)
        mins = int(self.time_survived // 60)
        secs = int(self.time_survived % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        self.engine.asset_manager.render_text(
            surface,
            f"⏱️ {time_str}",
            (SCREEN_WIDTH // 2, 22),
            size=22,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="midtop"
        )

        # 4. Kills, Ouro e Pontuação (Topo Direito)
        score_formatted = f"{int(self.score):,}".replace(",", ".")
        self.engine.asset_manager.render_text(
            surface,
            f"Kills: {self.kills}  |  Ouro: {self.gold_earned} G  |  {score_formatted} pts",
            (SCREEN_WIDTH - 16, 22),
            size=18,
            color=COLOR_GOLD,
            bold=True,
            align="topright"
        )

        # 5. Barra de Vida do Chefe Ativo (Topo Central abaixo do tempo)
        if self.active_boss and self.active_boss.hp > 0:
            boss_bar_w = 560
            boss_bar_h = 22
            boss_bar_x = SCREEN_WIDTH // 2 - boss_bar_w // 2
            boss_bar_y = 56

            # Fundo da barra de chefe
            pygame.draw.rect(surface, (30, 15, 20), (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h), border_radius=5)
            boss_ratio = max(0.0, min(1.0, self.active_boss.hp / max(1, self.active_boss.max_hp)))
            pygame.draw.rect(surface, COLOR_RED, (boss_bar_x, boss_bar_y, int(boss_bar_w * boss_ratio), boss_bar_h), border_radius=5)
            pygame.draw.rect(surface, COLOR_GOLD, (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h), width=2, border_radius=5)

            # Título do Chefe
            self.engine.asset_manager.render_text(
                surface,
                f"💀 {self.active_boss.name} — {self.active_boss.title}",
                (SCREEN_WIDTH // 2, boss_bar_y - 18),
                size=16,
                color=COLOR_RED,
                bold=True,
                align="center",
                shadow=True
            )
            # HP formatado sem decimais
            curr_hp_int = int(max(0, self.active_boss.hp))
            max_hp_int = int(self.active_boss.max_hp)
            hp_str = f"{curr_hp_int:,} / {max_hp_int:,} ({int(boss_ratio * 100)}%)".replace(",", ".")
            self.engine.asset_manager.render_text(
                surface,
                hp_str,
                (SCREEN_WIDTH // 2, boss_bar_y + boss_bar_h // 2),
                size=14,
                color=COLOR_TEXT_LIGHT,
                bold=True,
                align="center",
                shadow=True
            )

        # 6. Alerta de Chefe Entrando (Banner Central Flutuante)
        if self.boss_warning_timer > 0:
            pulse_alpha = int(180 + math.sin(self.player_anim_time * 12.0) * 75)
            warning_surf = pygame.Surface((SCREEN_WIDTH, 48), pygame.SRCALPHA)
            warning_surf.fill((220, 38, 38, max(50, pulse_alpha // 2)))
            surface.blit(warning_surf, (0, SCREEN_HEIGHT // 2 - 130))

            self.engine.asset_manager.render_text(
                surface,
                self.boss_warning_text,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 106),
                size=26,
                color=COLOR_GOLD,
                bold=True,
                align="center",
                shadow=True
            )

        # 7. Card do Poder Especial do Gato (Canto Inferior Esquerdo - Nível Superior)
        power_info = POWER_DEFINITIONS.get(self.cat_power, POWER_DEFINITIONS["none"])
        is_active_skill = (power_info["type"] == "active")
        is_ready = (self.ability_cooldown_timer <= 0.0)

        card_w = 260
        card_h = 30
        card_x = 20
        card_y = SCREEN_HEIGHT - 80

        card_bg = (24, 18, 38) if not is_ready else (18, 35, 42)
        card_border = power_info["color"] if is_ready else (65, 55, 85)

        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(surface, card_bg, card_rect, border_radius=6)
        pygame.draw.rect(surface, card_border, card_rect, width=2 if is_ready else 1, border_radius=6)

        if is_active_skill:
            if is_ready:
                status_text = "PRONTO [ESPAÇO]"
                status_color = COLOR_CYAN if self.cat_power == "mega_beam" else COLOR_PURPLE
            else:
                status_text = f"RECARGA: {self.ability_cooldown_timer:.1f}s"
                status_color = COLOR_TEXT_MUTED
        elif self.cat_power == "double_attack":
            status_text = "DISPARO DUPLO"
            status_color = COLOR_GOLD
        elif self.cat_power == "lifesteal":
            status_text = "+5% DANO EM HP"
            status_color = COLOR_GREEN
        elif self.cat_power == "ghost":
            lost_hp = max(0, self.player_max_hp - self.player_hp)
            status_text = f"CORPO (+{lost_hp * 2} DMG)"
            status_color = (192, 132, 252)
        elif self.cat_power == "brawler":
            status_text = "2x HP | 2x MELEE"
            status_color = (251, 146, 60)
        elif self.cat_power == "radioactive_aura":
            status_text = "AURA ATIVA (150px)"
            status_color = (74, 222, 128)
        else:
            status_text = "SEM PODER"
            status_color = COLOR_TEXT_MUTED

        self.engine.asset_manager.render_text(
            surface,
            f"{power_info['icon']} {power_info['name']}",
            (card_x + 8, card_y + 7),
            size=14,
            color=COLOR_TEXT_LIGHT,
            bold=True
        )
        self.engine.asset_manager.render_text(
            surface,
            status_text,
            (card_rect.right - 8, card_y + 7),
            size=13,
            color=status_color,
            bold=True,
            align="topright"
        )

        # 8. Barra de Vida do Jogador (Canto Inferior Esquerdo - Nível Inferior)
        hp_bar_w = 260
        hp_bar_h = 24
        hp_bar_x = 20
        hp_bar_y = SCREEN_HEIGHT - 44
        pygame.draw.rect(surface, (40, 20, 20), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=5)
        hp_fill = max(0, int(hp_bar_w * (self.player_hp / max(1, self.player_max_hp))))
        hp_color = COLOR_GREEN if (self.player_hp / self.player_max_hp) > 0.35 else COLOR_RED
        pygame.draw.rect(surface, hp_color, (hp_bar_x, hp_bar_y, hp_fill, hp_bar_h), border_radius=5)
        pygame.draw.rect(surface, (90, 80, 110), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), width=2, border_radius=5)

        # Texto do HP embutido no centro da barra de vida
        hp_pct = int(max(0, (self.player_hp / max(1, self.player_max_hp)) * 100))
        self.engine.asset_manager.render_text(
            surface,
            f"HP: {max(0, self.player_hp)} / {self.player_max_hp}  ({hp_pct}%)",
            (hp_bar_x + hp_bar_w // 2, hp_bar_y + hp_bar_h // 2),
            size=15,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=True
        )

        # 9. Badges de Upgrades Acumulados (Centro Inferior Limpo)
        upg_x = 300
        upg_y = SCREEN_HEIGHT - 38
        upgrades_list = [
            ("HP", self.upgrade_counts["hp"], COLOR_GREEN),
            ("DANO", self.upgrade_counts["damage"], COLOR_RED),
            ("ATK", self.upgrade_counts["attack_speed"], COLOR_GOLD),
            ("VEL", self.upgrade_counts["move_speed"], COLOR_CYAN),
            ("REGEN", self.upgrade_counts["hp_regen"], (34, 197, 94))
        ]

        curr_x = upg_x
        for label, count, col in upgrades_list:
            if count > 0:
                badge_text = f"{label} +{count}"
                badge_w = len(badge_text) * 8 + 14
                badge_rect = pygame.Rect(curr_x, upg_y, badge_w, 22)
                pygame.draw.rect(surface, (25, 20, 36), badge_rect, border_radius=4)
                pygame.draw.rect(surface, col, badge_rect, width=1, border_radius=4)
                self.engine.asset_manager.render_text(
                    surface,
                    badge_text,
                    (badge_rect.centerx, badge_rect.centery),
                    size=13,
                    color=col,
                    bold=True,
                    align="center"
                )
                curr_x += badge_w + 8

        # 10. Dica de Pausa (Canto Inferior Direito)
        self.engine.asset_manager.render_text(
            surface,
            "[ESC] Pausar",
            (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 32),
            size=16,
            color=COLOR_TEXT_MUTED,
            align="bottomright"
        )

        # --- MODAL DE LEVEL UP OVERLAY ---
        if self.is_leveling_up:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 6, 16, 215))
            surface.blit(overlay, (0, 0))

            self.engine.asset_manager.render_text(
                surface,
                f"✨ NOVO NÍVEL ALCANÇADO! (NÍVEL {self.player_level}) ✨",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200),
                size=36,
                color=COLOR_GOLD,
                bold=True,
                align="center",
                shadow=True
            )

            self.engine.asset_manager.render_text(
                surface,
                "Escolha 1 entre as 3 melhorias para fortalecer seu herói:",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 155),
                size=20,
                color=COLOR_TEXT_LIGHT,
                align="center"
            )

            for card in self.upgrade_cards:
                card.draw(surface, self.engine.asset_manager)

            self.engine.asset_manager.render_text(
                surface,
                "Dica: Clique com o mouse ou pressione as teclas [1], [2] ou [3] no teclado",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 225),
                size=17,
                color=COLOR_TEXT_MUTED,
                align="center"
            )

        # --- Menu de Pausa Overlay ---
        elif self.is_paused and not self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            self.pause_panel.draw(surface, self.engine.asset_manager)
            for btn in self.pause_buttons:
                btn.draw(surface, self.engine.asset_manager)

        # --- Tela de Game Over Overlay ---
        elif self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))

            self.gameover_panel.draw(surface, self.engine.asset_manager)

            score_formatted = f"{int(self.score):,}".replace(",", ".")
            lines = [
                ("Tempo Sobrevivido:", f"{mins:02d}:{secs:02d}"),
                ("Inimigos Eliminados:", f"{self.kills}"),
                ("Ouro Coletado:", f"{self.gold_earned} G"),
                ("Pontuação Final:", f"{score_formatted} pts"),
            ]

            start_y = self.gameover_panel.rect.y + 65
            for i, (label, val) in enumerate(lines):
                row_y = start_y + i * 36
                self.engine.asset_manager.render_text(
                    surface,
                    label,
                    (self.gameover_panel.rect.x + 35, row_y),
                    size=19,
                    color=COLOR_TEXT_LIGHT,
                    align="topleft"
                )
                self.engine.asset_manager.render_text(
                    surface,
                    val,
                    (self.gameover_panel.rect.right - 35, row_y),
                    size=19,
                    color=COLOR_GOLD,
                    bold=True,
                    align="topright"
                )

            for btn in self.gameover_buttons:
                btn.draw(surface, self.engine.asset_manager)
