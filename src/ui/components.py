"""
Componentes visuais reutilizáveis para interface do usuário (Botões, Sliders, Toggles e Painéis).
"""
import pygame
from typing import Callable, Optional, Tuple, Any
from src.core.constants import (
    COLOR_BTN_DEFAULT,
    COLOR_BTN_HOVER,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
    COLOR_BTN_BORDER_HOVER,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_GOLD,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_BG_CARD,
    COLOR_BG_CARD_BORDER,
    COLOR_BG_DARK,
)
from src.core.asset_manager import AssetManager


class Button:
    """Botão interativo com estados de hover, clique, animação suave e suporte a áudio."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        on_click: Optional[Callable[[], None]] = None,
        font_size: int = 24,
        accent_color: Tuple[int, int, int] = COLOR_GOLD,
        icon_cube_color: Optional[Tuple[int, int, int]] = None,
        sound_manager: Optional[Any] = None,
        disabled: bool = False
    ):
        self.rect = rect
        self.text = text
        self.on_click = on_click
        self.font_size = font_size
        self.accent_color = accent_color
        self.icon_cube_color = icon_cube_color
        self.sound_manager = sound_manager
        self.disabled = disabled

        self.is_hovered = False
        self.is_pressed = False
        self.hover_progress = 0.0  # Para interpolação de cor/brilho

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa eventos de mouse e teclado para o botão."""
        if self.disabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered and not was_hovered and self.sound_manager:
                self.sound_manager.play_sfx("ui_hover")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.sound_manager:
                    self.sound_manager.play_sfx("ui_click")
                if self.on_click:
                    self.on_click()
                return True
            self.is_pressed = False

        return False

    def update(self, dt: float) -> None:
        """Atualiza animações de transição de hover."""
        target = 1.0 if (self.is_hovered and not self.disabled) else 0.0
        speed = 10.0
        if self.hover_progress < target:
            self.hover_progress = min(target, self.hover_progress + speed * dt)
        elif self.hover_progress > target:
            self.hover_progress = max(target, self.hover_progress - speed * dt)

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager) -> None:
        """Renderiza o botão com gradiente de hover e borda destacada."""
        # Cor de fundo interpolada
        if self.disabled:
            bg_color = (25, 22, 35)
            border_color = (45, 40, 60)
            text_color = COLOR_TEXT_MUTED
        else:
            r = int(COLOR_BTN_DEFAULT[0] + (COLOR_BTN_HOVER[0] - COLOR_BTN_DEFAULT[0]) * self.hover_progress)
            g = int(COLOR_BTN_DEFAULT[1] + (COLOR_BTN_HOVER[1] - COLOR_BTN_DEFAULT[1]) * self.hover_progress)
            b = int(COLOR_BTN_DEFAULT[2] + (COLOR_BTN_HOVER[2] - COLOR_BTN_DEFAULT[2]) * self.hover_progress)
            bg_color = (r, g, b)

            # Borda
            if self.hover_progress > 0.1:
                border_color = self.accent_color
            else:
                border_color = COLOR_BTN_BORDER
            text_color = COLOR_TEXT_LIGHT

        # Efeito de deslocamento sutil se pressionado
        draw_rect = self.rect.copy()
        if self.is_pressed and not self.disabled:
            draw_rect.y += 2

        # Brilho de hover sutil
        if self.hover_progress > 0.05 and not self.disabled:
            glow_surf = pygame.Surface((draw_rect.width + 10, draw_rect.height + 10), pygame.SRCALPHA)
            glow_alpha = int(40 * self.hover_progress)
            pygame.draw.rect(glow_surf, (*self.accent_color[:3], glow_alpha), glow_surf.get_rect(), border_radius=8)
            surface.blit(glow_surf, (draw_rect.x - 5, draw_rect.y - 5))

        # Corpo do botão
        pygame.draw.rect(surface, bg_color, draw_rect, border_radius=6)
        pygame.draw.rect(surface, border_color, draw_rect, width=2, border_radius=6)

        # Se houver ícone de cubo colorido decorativo
        text_offset_x = 0
        if self.icon_cube_color:
            cube_size = 18
            cube_rect = pygame.Rect(
                draw_rect.x + 16,
                draw_rect.centery - cube_size // 2,
                cube_size,
                cube_size
            )
            asset_mgr.draw_styled_cube(surface, cube_rect, self.icon_cube_color, glow=self.is_hovered)
            text_offset_x = 14

        # Texto do botão
        asset_mgr.render_text(
            surface,
            self.text,
            (draw_rect.centerx + text_offset_x, draw_rect.centery),
            size=self.font_size,
            color=text_color,
            bold=self.is_hovered,
            align="center",
            shadow=True
        )


class Slider:
    """Controle deslizante interativo para ajuste contínuo de valores (ex: volume 0 a 100%)."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        value: float = 0.8,
        on_change: Optional[Callable[[float], None]] = None,
        sound_manager: Optional[Any] = None
    ):
        self.rect = rect
        self.label = label
        self.value = max(0.0, min(1.0, value))
        self.on_change = on_change
        self.sound_manager = sound_manager
        self.is_dragging = False
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa cliques e arrastes no slider."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_dragging:
                self._update_value_from_pos(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_value_from_pos(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                if self.sound_manager:
                    self.sound_manager.play_sfx("ui_click")
                return True

        return False

    def _update_value_from_pos(self, mouse_x: int) -> None:
        """Converte a posição X do mouse para a proporção 0.0 - 1.0."""
        track_x = self.rect.x + 180
        track_w = self.rect.width - 260
        rel_x = mouse_x - track_x
        new_val = max(0.0, min(1.0, rel_x / max(1, track_w)))
        if abs(new_val - self.value) > 0.01:
            self.value = round(new_val, 2)
            if self.on_change:
                self.on_change(self.value)

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager) -> None:
        """Renderiza o label, a barra de progresso preenchida e o manipulador (knob)."""
        # Label do slider
        asset_mgr.render_text(
            surface,
            self.label,
            (self.rect.x, self.rect.centery),
            size=22,
            color=COLOR_TEXT_LIGHT,
            align="midleft"
        )

        track_x = self.rect.x + 180
        track_w = self.rect.width - 260
        track_y = self.rect.centery - 4
        track_h = 8

        # Barra de fundo (trilho)
        pygame.draw.rect(surface, (45, 40, 65), (track_x, track_y, track_w, track_h), border_radius=4)

        # Barra preenchida
        filled_w = int(track_w * self.value)
        if filled_w > 0:
            pygame.draw.rect(surface, COLOR_GOLD, (track_x, track_y, filled_w, track_h), border_radius=4)

        # Knob / Indicador em cubo
        knob_x = track_x + filled_w
        knob_size = 18
        knob_rect = pygame.Rect(knob_x - knob_size // 2, self.rect.centery - knob_size // 2, knob_size, knob_size)
        asset_mgr.draw_styled_cube(surface, knob_rect, COLOR_GOLD if not self.is_dragging else COLOR_CYAN, glow=True)

        # Texto do valor (ex: 80%)
        percent_str = f"{int(self.value * 100)}%"
        asset_mgr.render_text(
            surface,
            percent_str,
            (self.rect.right - 10, self.rect.centery),
            size=20,
            color=COLOR_CYAN if self.is_hovered or self.is_dragging else COLOR_TEXT_MUTED,
            bold=True,
            align="midright"
        )


class ToggleSwitch:
    """Chave de alternância ON/OFF (ex: Tela Cheia, V-Sync, Screen Shake)."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        value: bool = False,
        on_toggle: Optional[Callable[[bool], None]] = None,
        sound_manager: Optional[Any] = None
    ):
        self.rect = rect
        self.label = label
        self.value = value
        self.on_toggle = on_toggle
        self.sound_manager = sound_manager
        self.is_hovered = False
        self.anim_progress = 1.0 if value else 0.0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Trata clique para alternar estado."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value
                if self.sound_manager:
                    self.sound_manager.play_sfx("ui_click")
                if self.on_toggle:
                    self.on_toggle(self.value)
                return True

        return False

    def update(self, dt: float) -> None:
        """Anima a transição da chave."""
        target = 1.0 if self.value else 0.0
        speed = 12.0
        if self.anim_progress < target:
            self.anim_progress = min(target, self.anim_progress + speed * dt)
        elif self.anim_progress > target:
            self.anim_progress = max(target, self.anim_progress - speed * dt)

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager) -> None:
        """Renderiza label e a chave deslizante animada."""
        asset_mgr.render_text(
            surface,
            self.label,
            (self.rect.x, self.rect.centery),
            size=22,
            color=COLOR_TEXT_LIGHT,
            align="midleft"
        )

        switch_w = 64
        switch_h = 32
        switch_x = self.rect.right - switch_w - 10
        switch_y = self.rect.centery - switch_h // 2
        switch_rect = pygame.Rect(switch_x, switch_y, switch_w, switch_h)

        # Cor do fundo da chave
        r = int(45 + (COLOR_GREEN[0] - 45) * self.anim_progress * 0.7)
        g = int(40 + (COLOR_GREEN[1] - 40) * self.anim_progress * 0.7)
        b = int(65 + (COLOR_GREEN[2] - 65) * self.anim_progress * 0.7)
        pygame.draw.rect(surface, (r, g, b), switch_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_BTN_BORDER if not self.is_hovered else COLOR_GOLD, switch_rect, width=2, border_radius=16)

        # Botão deslizante (pílula/cubo)
        knob_size = 24
        knob_min_x = switch_x + 4
        knob_max_x = switch_x + switch_w - knob_size - 4
        knob_curr_x = int(knob_min_x + (knob_max_x - knob_min_x) * self.anim_progress)
        knob_y = switch_y + 4
        knob_rect = pygame.Rect(knob_curr_x, knob_y, knob_size, knob_size)

        knob_color = (250, 250, 250) if not self.value else COLOR_GREEN
        asset_mgr.draw_styled_cube(surface, knob_rect, knob_color, glow=self.value)


class Panel:
    """Container para agrupar elementos visuais com fundo estilizado."""

    def __init__(self, rect: pygame.Rect, title: Optional[str] = None):
        self.rect = rect
        self.title = title

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager) -> None:
        """Renderiza o painel com sombra suave e borda decorada."""
        # Fundo do painel
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*COLOR_BG_CARD[:3], 230), panel_surf.get_rect(), border_radius=12)
        surface.blit(panel_surf, self.rect.topleft)

        # Borda
        pygame.draw.rect(surface, COLOR_BG_CARD_BORDER, self.rect, width=2, border_radius=12)

        # Título opcional no topo do painel
        if self.title:
            title_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 12, self.rect.width - 40, 36)
            asset_mgr.render_text(
                surface,
                self.title,
                (title_rect.left, title_rect.centery),
                size=22,
                color=COLOR_GOLD,
                bold=True,
                align="midleft"
            )
            # Linha divisória sutil
            pygame.draw.line(
                surface,
                (60, 52, 90),
                (self.rect.x + 20, self.rect.y + 48),
                (self.rect.right - 20, self.rect.y + 48),
                width=1
            )


class UpgradeCard:
    """Card interativo exibido no modal de Level Up com ícone de cubo, descrição e atalho."""

    def __init__(
        self,
        rect: pygame.Rect,
        shortcut_num: int,
        upgrade_id: str,
        title: str,
        description: str,
        stat_preview: str,
        icon_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int] = COLOR_GOLD,
        on_click: Optional[Callable[[], None]] = None,
        sound_manager: Optional[Any] = None
    ):
        self.rect = rect
        self.shortcut_num = shortcut_num
        self.upgrade_id = upgrade_id
        self.title = title
        self.description = description
        self.stat_preview = stat_preview
        self.icon_color = icon_color
        self.accent_color = accent_color
        self.on_click = on_click
        self.sound_manager = sound_manager

        self.is_hovered = False
        self.is_pressed = False
        self.hover_progress = 0.0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Processa eventos de mouse e clique no card."""
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered and not was_hovered and self.sound_manager:
                self.sound_manager.play_sfx("ui_hover")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.sound_manager:
                    self.sound_manager.play_sfx("levelup")
                if self.on_click:
                    self.on_click()
                return True
            self.is_pressed = False

        return False

    def update(self, dt: float) -> None:
        """Anima elevação e brilho no hover."""
        target = 1.0 if self.is_hovered else 0.0
        speed = 10.0
        if self.hover_progress < target:
            self.hover_progress = min(target, self.hover_progress + speed * dt)
        elif self.hover_progress > target:
            self.hover_progress = max(target, self.hover_progress - speed * dt)

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager) -> None:
        """Renderiza o card de upgrade estilizado."""
        # Deslocamento vertical suave no hover
        offset_y = int(self.hover_progress * 6)
        draw_rect = pygame.Rect(self.rect.x, self.rect.y - offset_y, self.rect.width, self.rect.height)

        # Brilho de fundo no hover
        if self.hover_progress > 0.05:
            glow_surf = pygame.Surface((draw_rect.width + 16, draw_rect.height + 16), pygame.SRCALPHA)
            glow_alpha = int(45 * self.hover_progress)
            pygame.draw.rect(glow_surf, (*self.accent_color[:3], glow_alpha), glow_surf.get_rect(), border_radius=14)
            surface.blit(glow_surf, (draw_rect.x - 8, draw_rect.y - 8))

        # Fundo do Card
        card_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        bg_r = int(COLOR_BG_CARD[0] + (COLOR_BTN_HOVER[0] - COLOR_BG_CARD[0]) * self.hover_progress * 0.5)
        bg_g = int(COLOR_BG_CARD[1] + (COLOR_BTN_HOVER[1] - COLOR_BG_CARD[1]) * self.hover_progress * 0.5)
        bg_b = int(COLOR_BG_CARD[2] + (COLOR_BTN_HOVER[2] - COLOR_BG_CARD[2]) * self.hover_progress * 0.5)
        pygame.draw.rect(card_surf, (bg_r, bg_g, bg_b, 240), card_surf.get_rect(), border_radius=10)
        surface.blit(card_surf, draw_rect.topleft)

        # Borda
        border_color = self.accent_color if self.hover_progress > 0.1 else COLOR_BG_CARD_BORDER
        border_w = 3 if self.hover_progress > 0.1 else 2
        pygame.draw.rect(surface, border_color, draw_rect, width=border_w, border_radius=10)

        # Badge de atalho [1], [2], [3]
        badge_w, badge_h = 32, 26
        badge_rect = pygame.Rect(draw_rect.right - badge_w - 12, draw_rect.y + 12, badge_w, badge_h)
        pygame.draw.rect(surface, (45, 40, 65), badge_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD if self.is_hovered else COLOR_BTN_BORDER, badge_rect, width=1, border_radius=4)
        asset_mgr.render_text(
            surface,
            f"[{self.shortcut_num}]",
            (badge_rect.centerx, badge_rect.centery),
            size=16,
            color=COLOR_GOLD if self.is_hovered else COLOR_TEXT_MUTED,
            bold=True,
            align="center",
            shadow=False
        )

        # Ícone de Cubo Estilizado
        cube_size = 40
        cube_rect = pygame.Rect(
            draw_rect.centerx - cube_size // 2,
            draw_rect.y + 26,
            cube_size,
            cube_size
        )
        asset_mgr.draw_styled_cube(surface, cube_rect, self.icon_color, glow=True)

        # Título da Melhoria
        asset_mgr.render_text(
            surface,
            self.title,
            (draw_rect.centerx, draw_rect.y + 76),
            size=20,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=True
        )

        # Divisor sutil
        pygame.draw.line(
            surface,
            (60, 52, 90),
            (draw_rect.x + 18, draw_rect.y + 102),
            (draw_rect.right - 18, draw_rect.y + 102),
            width=1
        )

        # Descrição da Melhoria (com quebra de linha limpa sem linhas vazias)
        desc_lines = [line.strip() for line in self.description.split("\n") if line.strip()]
        start_desc_y = draw_rect.y + 114
        for i, line in enumerate(desc_lines):
            asset_mgr.render_text(
                surface,
                line,
                (draw_rect.centerx, start_desc_y + i * 22),
                size=16,
                color=COLOR_GOLD,
                bold=True,
                align="center"
            )

        # Status Atual / Preview em mini-painel
        preview_box = pygame.Rect(draw_rect.x + 20, draw_rect.y + 195, draw_rect.width - 40, 28)
        pygame.draw.rect(surface, (20, 16, 32), preview_box, border_radius=6)
        pygame.draw.rect(surface, (50, 42, 70), preview_box, width=1, border_radius=6)
        asset_mgr.render_text(
            surface,
            self.stat_preview,
            (preview_box.centerx, preview_box.centery),
            size=14,
            color=COLOR_CYAN,
            bold=True,
            align="center"
        )

        # Botão de Escolha no rodapé do Card
        btn_box = pygame.Rect(draw_rect.x + 20, draw_rect.bottom - 46, draw_rect.width - 40, 32)
        btn_bg = self.accent_color if self.is_hovered else (45, 40, 65)
        pygame.draw.rect(surface, btn_bg, btn_box, border_radius=6)
        asset_mgr.render_text(
            surface,
            "ESCOLHER" if not self.is_hovered else "SELECIONAR",
            (btn_box.centerx, btn_box.centery),
            size=15,
            color=COLOR_BG_DARK if self.is_hovered else COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=not self.is_hovered
        )

