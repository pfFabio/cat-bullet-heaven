"""
Cena de Gameplay do Bullet Heaven (Survivors) com personagens e inimigos representados por cubos coloridos,
sistema de disparo automático, ondas de inimigos, coleta de XP/ouro, menu de pausa,
sistema de LEVEL UP com escolha entre 3 de 4 melhorias e tela de Game Over com persistência.
"""
import math
import random
import pygame
from typing import List, Tuple, Dict, Any, TYPE_CHECKING
from src.scenes.base_scene import BaseScene
from src.ui.components import Button, Panel, UpgradeCard
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG_DARK,
    COLOR_PLAYER_CUBE,
    COLOR_ENEMY_BASIC,
    COLOR_ENEMY_FAST,
    COLOR_ENEMY_TANK,
    COLOR_PROJECTILE,
    COLOR_XP_GEM,
    COLOR_GOLD_COIN,
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
    """Texto flutuante com valor de dano ou ouro obtido."""

    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 0.8
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.y -= 30 * dt
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface, asset_mgr) -> None:
        asset_mgr.render_text(
            surface,
            self.text,
            (int(self.x), int(self.y)),
            size=18,
            color=self.color,
            bold=True,
            align="center",
            shadow=True
        )


class Projectile:
    """Projétil disparado pelo jogador em direção aos inimigos."""

    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: int = 25, speed: float = 450.0):
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

    def draw(self, surface: pygame.Surface, asset_mgr) -> None:
        rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)
        asset_mgr.draw_styled_cube(surface, rect, COLOR_PROJECTILE, glow=True)


class Enemy:
    """Inimigo com animação de sprites (Minifantasy) e perseguição ao jogador."""

    def __init__(self, x: float, y: float, enemy_type: str = "basic"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.anim_time = random.uniform(0.0, 1.0)
        self.facing_left = False

        if enemy_type == "fast":
            self.size = 20
            self.max_hp = 30
            self.speed = 175.0
            self.color = COLOR_ENEMY_FAST
            self.xp_value = 15
            self.damage = 8
            self.sprite_scale = (36, 36)
        elif enemy_type == "tank":
            self.size = 36
            self.max_hp = 140
            self.speed = 70.0
            self.color = COLOR_ENEMY_TANK
            self.xp_value = 40
            self.damage = 25
            self.sprite_scale = (52, 52)
        else:  # basic (Lobo)
            self.size = 32
            self.max_hp = 50
            self.speed = 110.0
            self.color = COLOR_ENEMY_BASIC
            self.xp_value = 20
            self.damage = 12
            self.sprite_scale = (100, 100)

        self.hp = self.max_hp

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)

    def update(self, dt: float, player_x: float, player_y: float) -> None:
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

    def draw(self, surface: pygame.Surface, asset_mgr) -> None:
        frames = asset_mgr.get_enemy_frames(self.enemy_type, action="walk", scale=self.sprite_scale)
        if frames:
            fps = 8.0 if self.enemy_type != "fast" else 10.0
            frame_idx = int(self.anim_time * fps) % len(frames)
            frame = frames[frame_idx]
            if self.facing_left:
                frame = pygame.transform.flip(frame, True, False)
            rect = frame.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(frame, rect)
        else:
            asset_mgr.draw_styled_cube(surface, self.rect, self.color, glow=False)

        # Barra de vida se sofreu dano
        if self.hp < self.max_hp:
            bar_w = max(self.size, 28)
            bar_h = 4
            bar_x = int(self.x - bar_w // 2)
            bar_y = int(self.y - self.sprite_scale[1] // 2 - 4)
            pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            hp_w = max(0, int(bar_w * (self.hp / self.max_hp)))
            pygame.draw.rect(surface, COLOR_RED, (bar_x, bar_y, hp_w, bar_h), border_radius=2)



class DropItem:
    """Itens coletáveis caídos (Gemas de XP e Ouro)."""

    def __init__(self, x: float, y: float, item_type: str = "xp", value: int = 10):
        self.x = x
        self.y = y
        self.item_type = item_type  # 'xp' ou 'gold'
        self.value = value
        self.size = 12
        self.color = COLOR_XP_GEM if item_type == "xp" else COLOR_GOLD_COIN

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)

    def attract_towards(self, target_x: float, target_y: float, speed: float, dt: float) -> None:
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(0.001, math.hypot(dx, dy))
        self.x += (dx / dist) * speed * dt
        self.y += (dy / dist) * speed * dt

    def draw(self, surface: pygame.Surface, asset_mgr) -> None:
        asset_mgr.draw_styled_cube(surface, self.rect, self.color, glow=True)


class GameplayScene(BaseScene):
    """Cena principal de combate e sobrevivência com sistema de Level Up interativo."""

    def __init__(self, engine: "GameEngine"):
        super().__init__(engine)
        self.is_paused = False
        self.game_over = False
        self.is_leveling_up = False

        # Estado do Jogador
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_size = 28
        self.player_speed = 220.0
        self.player_max_hp = 100
        self.player_hp = 100
        self.player_damage = 25
        self.player_level = 1
        self.player_xp = 0
        self.player_xp_to_next = 50
        self.pickup_radius = 120.0

        # Animação e Sprite do Protagonista (Gatinho Azul)
        self.cat_name = "blue_0"
        self.player_facing_dir = "down"
        self.player_action = "sit"
        self.player_anim_time = 0.0
        self.player_idle_switch_timer = 0.0
        self.player_is_moving = False
        self.player_sprite_scale = (44, 44)

        # Contadores de Melhorias
        self.upgrade_counts = {
            "hp": 0,
            "damage": 0,
            "attack_speed": 0,
            "move_speed": 0
        }

        # Estatísticas da Partida
        self.time_survived = 0.0
        self.score = 0
        self.kills = 0
        self.gold_earned = 0

        # Entidades
        self.projectiles: List[Projectile] = []
        self.enemies: List[Enemy] = []
        self.drops: List[DropItem] = []
        self.damage_numbers: List[DamageNumber] = []
        self.upgrade_cards: List[UpgradeCard] = []

        # Timers de Combate e Spawn
        self.attack_cooldown = 0.45  # Dispara a cada 0.45s
        self.attack_timer = 0.0
        self.spawn_timer = 0.0
        self.invulnerable_timer = 0.0

        self._init_ui_overlays()

    def on_enter(self) -> None:
        """Reinicia os dados ao entrar na partida."""
        self.__init__(self.engine)

    def _init_ui_overlays(self) -> None:
        """Inicializa os menus de pausa e game over."""
        # Menu de Pausa
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
        self.engine.change_scene("main_menu")

    def _trigger_game_over(self) -> None:
        """Processa a derrota e grava estatísticas no savegame."""
        self.game_over = True
        self.engine.save_manager.record_run_stats(
            score=self.score,
            kills=self.kills,
            time_survived=self.time_survived,
            gold_earned=self.gold_earned
        )
        self.engine.audio_manager.play_sfx("hit")

    # --- Sistema de Level Up e Escolhas ---

    def _get_all_upgrade_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Retorna o dicionário com as 4 opções de melhorias disponíveis."""
        return {
            "hp": {
                "title": "Aumentar HP",
                "desc": "+25 HP Máximo\n",
                "preview": f"HP Máx Atual: {self.player_max_hp}",
                "color": COLOR_GREEN,
                "accent": COLOR_GREEN,
                "apply": self._apply_hp_upgrade
            },
            "damage": {
                "title": "Aumentar Dano",
                "desc": "+10% Dano por Disparo\n",
                "preview": f"Dano Atual: {self.player_damage}",
                "color": COLOR_RED,
                "accent": COLOR_RED,
                "apply": self._apply_damage_upgrade
            },
            "attack_speed": {
                "title": "Velocidade de Ataque",
                "desc": "-5% Tempo de Recarga\nDisparos mais velozes",
                "preview": f"Recarga Atual: {self.attack_cooldown:.2f}s",
                "color": COLOR_GOLD,
                "accent": COLOR_GOLD,
                "apply": self._apply_attack_speed_upgrade
            },
            "move_speed": {
                "title": "Velocidade de Movimento",
                "desc": "+30 Velocidade de Corrida\n",
                "preview": f"Velocidade: {int(self.player_speed)}",
                "color": COLOR_CYAN,
                "accent": COLOR_CYAN,
                "apply": self._apply_move_speed_upgrade
            }
        }

    def _apply_hp_upgrade(self) -> None:
        """Aplica melhoria de HP."""
        self.player_max_hp += 25
        self.player_hp = min(self.player_max_hp, self.player_hp + 25)
        self.upgrade_counts["hp"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+25 MAX HP!", COLOR_GREEN))

    def _apply_damage_upgrade(self) -> None:
        """Aplica melhoria de dano."""
        self.player_damage += self.player_damage * 0.1
        self.upgrade_counts["damage"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+10% DANO!", COLOR_RED))

    def _apply_attack_speed_upgrade(self) -> None:
        """Aplica melhoria de velocidade de ataque."""
        self.attack_cooldown = max(0.08, self.attack_cooldown * 0.95)
        self.upgrade_counts["attack_speed"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+ATK SPEED!", COLOR_GOLD))

    def _apply_move_speed_upgrade(self) -> None:
        """Aplica melhoria de velocidade de movimento."""
        self.player_speed += 30.0
        self.upgrade_counts["move_speed"] += 1
        self.damage_numbers.append(DamageNumber(self.player_x, self.player_y - 30, "+VELOCIDADE!", COLOR_CYAN))

    def _trigger_level_up(self) -> None:
        """Inicia a tela de seleção de Level Up sorteando 3 das 4 opções."""
        self.is_leveling_up = True
        self.engine.audio_manager.play_sfx("levelup")

        all_upgrades = self._get_all_upgrade_definitions()
        # Sorteia exatamente 3 opções distintas entre as 4 existentes
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

        # Se ainda sobrou XP suficiente para mais um nível acumulado
        if self.player_xp >= self.player_xp_to_next:
            self.player_level += 1
            self.player_xp -= self.player_xp_to_next
            self.player_xp_to_next = int(self.player_xp_to_next * 1.35)
            self._trigger_level_up()
        else:
            self.is_leveling_up = False
            self.upgrade_cards.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        # Se estiver na tela de escolha de Level Up
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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._toggle_pause()
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

    def _spawn_wave(self, dt: float) -> None:
        """Gera ondas de inimigos ao redor da tela com taxa crescente."""
        self.spawn_timer += dt
        spawn_interval = max(0.4, 1.8 - (self.time_survived / 90.0))

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0

            # Escolhe borda aleatória fora da tela
            side = random.randint(0, 3)
            margin = 40
            if side == 0:  # Topo
                sx = random.uniform(0, SCREEN_WIDTH)
                sy = -margin
            elif side == 1:  # Direita
                sx = SCREEN_WIDTH + margin
                sy = random.uniform(0, SCREEN_HEIGHT)
            elif side == 2:  # Baixo
                sx = random.uniform(0, SCREEN_WIDTH)
                sy = SCREEN_HEIGHT + margin
            else:  # Esquerda
                sx = -margin
                sy = random.uniform(0, SCREEN_HEIGHT)

            # Probabilidade do tipo de inimigo com base no tempo
            r = random.random()
            if self.time_survived > 45 and r < 0.25:
                etype = "tank"
            elif self.time_survived > 20 and r < 0.50:
                etype = "fast"
            else:
                etype = "basic"

            self.enemies.append(Enemy(sx, sy, enemy_type=etype))

    def _auto_attack(self, dt: float) -> None:
        """Dispara automaticamente no inimigo mais próximo usando o dano do jogador."""
        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            if not self.enemies:
                return

            # Encontra inimigo mais próximo
            closest_enemy = min(
                self.enemies,
                key=lambda e: math.hypot(e.x - self.player_x, e.y - self.player_y)
            )

            dist = math.hypot(closest_enemy.x - self.player_x, closest_enemy.y - self.player_y)
            if dist < 650:
                self.projectiles.append(
                    Projectile(
                        self.player_x,
                        self.player_y,
                        closest_enemy.x,
                        closest_enemy.y,
                        damage=self.player_damage
                    )
                )
                self.engine.audio_manager.play_sfx("shoot")
                self.attack_timer = 0.0

    def update(self, dt: float) -> None:
        # Se estiver escolhendo Level Up, apenas atualiza animações dos cards e pausa a gameplay
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

            # Mapeamento 8-direcional do gatinho
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
            # Alterna periodicamente entre sentar e olhar em volta
            if self.player_idle_switch_timer > 4.5:
                self.player_action = "look"
                if self.player_idle_switch_timer > 7.5:
                    self.player_idle_switch_timer = 0.0
            else:
                self.player_action = "sit"

        self.player_anim_time += dt

        # Limita dentro da tela
        half_p = self.player_size // 2
        self.player_x = max(half_p, min(SCREEN_WIDTH - half_p, self.player_x))
        self.player_y = max(half_p + 30, min(SCREEN_HEIGHT - half_p, self.player_y))

        # Disparo automático e Spawn de inimigos
        self._auto_attack(dt)
        self._spawn_wave(dt)

        # Atualiza projéteis
        self.projectiles = [p for p in self.projectiles if p.update(dt)]

        # Atualiza inimigos e colisão com projéteis
        player_rect = pygame.Rect(
            int(self.player_x - half_p),
            int(self.player_y - half_p),
            self.player_size,
            self.player_size
        )

        for enemy in self.enemies:
            enemy.update(dt, self.player_x, self.player_y)

            # Dano no jogador
            if self.invulnerable_timer <= 0 and player_rect.colliderect(enemy.rect):
                self.player_hp -= enemy.damage
                self.invulnerable_timer = 0.5
                self.engine.audio_manager.play_sfx("hit")
                self.damage_numbers.append(
                    DamageNumber(self.player_x, self.player_y - 20, f"-{enemy.damage}", COLOR_RED)
                )
                if self.player_hp <= 0:
                    self._trigger_game_over()
                    return

            # Colisão Projétil x Inimigo
            for proj in self.projectiles[:]:
                p_rect = pygame.Rect(int(proj.x - 6), int(proj.y - 6), 12, 12)
                if enemy.rect.colliderect(p_rect):
                    enemy.hp -= proj.damage
                    dmg_display = f"{proj.damage:.1f}" if isinstance(proj.damage, float) and not proj.damage.is_integer() else str(int(proj.damage))
                    self.damage_numbers.append(
                        DamageNumber(enemy.x, enemy.y - 12, dmg_display, COLOR_GOLD)
                    )
                    self.score += proj.damage
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    self.engine.audio_manager.play_sfx("hit")

        # Inimigos derrotados -> Drops de XP e Ouro
        alive_enemies = []
        for enemy in self.enemies:
            if enemy.hp <= 0:
                self.kills += 1
                self.score += enemy.xp_value * 2
                # Drop XP
                self.drops.append(DropItem(enemy.x, enemy.y, "xp", value=enemy.xp_value))
                # Chance de Gold Coin
                if random.random() < 0.35:
                    self.drops.append(DropItem(enemy.x + random.uniform(-10, 10), enemy.y, "gold", value=random.randint(1, 5)))
            else:
                alive_enemies.append(enemy)
        self.enemies = alive_enemies

        # Atração e Coleta de Itens Caídos
        remaining_drops = []
        for drop in self.drops:
            dist = math.hypot(drop.x - self.player_x, drop.y - self.player_y)
            if dist < self.pickup_radius:
                drop.attract_towards(self.player_x, self.player_y, speed=360.0, dt=dt)

            if dist < self.player_size:
                if drop.item_type == "xp":
                    self.player_xp += drop.value
                    self.engine.audio_manager.play_sfx("gem")
                    # Disparo de Level Up
                    if self.player_xp >= self.player_xp_to_next:
                        self.player_level += 1
                        self.player_xp -= self.player_xp_to_next
                        self.player_xp_to_next = int(self.player_xp_to_next * 1.35)
                        self._trigger_level_up()
                        return
                elif drop.item_type == "gold":
                    self.gold_earned += drop.value
                    self.engine.audio_manager.play_sfx("gem")
                    self.damage_numbers.append(
                        DamageNumber(self.player_x, self.player_y - 25, f"+{drop.value} G", COLOR_GOLD)
                    )
            else:
                remaining_drops.append(drop)
        self.drops = remaining_drops

        # Atualiza números de dano
        self.damage_numbers = [d for d in self.damage_numbers if d.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        # Plano de fundo do jogo (BG.jpg) com fallback para fundo escuro
        bg = self.engine.asset_manager.get_background((SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg:
            surface.blit(bg, (0, 0))
        else:
            surface.fill(COLOR_BG_DARK)
            # Grade sutil de arena como fallback
            grid_size = 64
            for x in range(0, SCREEN_WIDTH, grid_size):
                pygame.draw.line(surface, (18, 16, 28), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, grid_size):
                pygame.draw.line(surface, (18, 16, 28), (0, y), (SCREEN_WIDTH, y))

        # Renderiza Itens de Drop
        for drop in self.drops:
            drop.draw(surface, self.engine.asset_manager)

        # Renderiza Projéteis
        for proj in self.projectiles:
            proj.draw(surface, self.engine.asset_manager)

        # Renderiza Inimigos
        for enemy in self.enemies:
            enemy.draw(surface, self.engine.asset_manager)

        # Renderiza Jogador (Gatinho Azul com sombra e animação 8-direcional)
        if not self.game_over:
            # Sombra suave sob o gato
            self.engine.asset_manager.draw_shadow(
                surface,
                int(self.player_x),
                int(self.player_y + 12),
                radius_x=16,
                radius_y=7,
                alpha=85
            )

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
                    rect = frame.get_rect(center=(int(self.player_x), int(self.player_y)))
                    surface.blit(frame, rect)
                else:
                    p_rect = pygame.Rect(
                        int(self.player_x - self.player_size // 2),
                        int(self.player_y - self.player_size // 2),
                        self.player_size,
                        self.player_size
                    )
                    self.engine.asset_manager.draw_styled_cube(
                        surface,
                        p_rect,
                        COLOR_PLAYER_CUBE,
                        glow=True
                    )

        # Renderiza Números de Dano
        for d in self.damage_numbers:
            d.draw(surface, self.engine.asset_manager)

        # --- HUD Superior ---
        # Barra de Experiência no topo
        xp_ratio = min(1.0, self.player_xp / max(1, self.player_xp_to_next))
        pygame.draw.rect(surface, (25, 20, 40), (0, 0, SCREEN_WIDTH, 14))
        pygame.draw.rect(surface, COLOR_CYAN, (0, 0, int(SCREEN_WIDTH * xp_ratio), 14))

        # Informações de Nível e Tempo
        mins = int(self.time_survived // 60)
        secs = int(self.time_survived % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        self.engine.asset_manager.render_text(
            surface,
            f"LV {self.player_level}",
            (16, 24),
            size=22,
            color=COLOR_CYAN,
            bold=True
        )

        self.engine.asset_manager.render_text(
            surface,
            f"TEMPO: {time_str}",
            (SCREEN_WIDTH // 2, 24),
            size=22,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="midtop"
        )

        self.engine.asset_manager.render_text(
            surface,
            f"Kills: {self.kills}  |  Ouro: {self.gold_earned}  |  Pontos: {self.score}",
            (SCREEN_WIDTH - 16, 24),
            size=20,
            color=COLOR_GOLD,
            bold=True,
            align="topright"
        )

        # Barra de Vida do Jogador (Canto inferior esquerdo)
        hp_bar_w = 220
        hp_bar_h = 16
        hp_bar_x = 20
        hp_bar_y = SCREEN_HEIGHT - 40
        pygame.draw.rect(surface, (40, 20, 20), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=4)
        hp_fill = max(0, int(hp_bar_w * (self.player_hp / max(1, self.player_max_hp))))
        pygame.draw.rect(surface, COLOR_GREEN if self.player_hp > 30 else COLOR_RED, (hp_bar_x, hp_bar_y, hp_fill, hp_bar_h), border_radius=4)
        pygame.draw.rect(surface, (80, 70, 100), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), width=2, border_radius=4)

        self.engine.asset_manager.render_text(
            surface,
            f"HP: {max(0, self.player_hp)} / {self.player_max_hp}",
            (hp_bar_x + hp_bar_w + 10, hp_bar_y - 2),
            size=18,
            color=COLOR_TEXT_LIGHT,
            bold=True
        )

        # Status / Upgrades acumulados no canto inferior
        upgrades_hud = f"HP Lv.{self.upgrade_counts['hp']} | Dano Lv.{self.upgrade_counts['damage']} | Atk.Spd Lv.{self.upgrade_counts['attack_speed']} | Vel Lv.{self.upgrade_counts['move_speed']}"
        self.engine.asset_manager.render_text(
            surface,
            upgrades_hud,
            (20, SCREEN_HEIGHT - 18),
            size=15,
            color=COLOR_TEXT_MUTED,
            align="bottomleft"
        )

        # Dica de Pausa
        self.engine.asset_manager.render_text(
            surface,
            "[ESC] Pausar",
            (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20),
            size=18,
            color=COLOR_TEXT_MUTED,
            align="bottomright"
        )

        # --- MODAL DE LEVEL UP OVERLAY ---
        if self.is_leveling_up:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 6, 16, 210))
            surface.blit(overlay, (0, 0))

            # Cabeçalho do Level Up
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

            # Renderiza os 3 cards de upgrade sorteados
            for card in self.upgrade_cards:
                card.draw(surface, self.engine.asset_manager)

            # Dica de teclado no rodapé
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

            lines = [
                ("Tempo Sobrevivido:", f"{mins:02d}:{secs:02d}"),
                ("Inimigos Eliminados:", f"{self.kills}"),
                ("Ouro Coletado:", f"{self.gold_earned} G"),
                ("Pontuação Final:", f"{self.score} pts"),
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
