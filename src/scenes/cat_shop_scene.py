"""
Cena de Desbloqueio e Seleção de Gatinhos (Cat Shop).
Permite visualizar, desbloquear com ouro e equipar até 50 skins de gatinhos.
"""
import math
import pygame
from typing import TYPE_CHECKING, List, Optional, Tuple
from src.scenes.base_scene import BaseScene
from src.ui.components import Button, Panel
from src.ui.particle import AmbientParticleSystem
from src.core.skin_catalog import (
    CatSkin,
    CAT_CATEGORIES,
    get_skin,
    get_skins_by_category,
)
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_BG_CARD,
    COLOR_BG_CARD_BORDER,
    COLOR_GOLD,
    COLOR_CYAN,
    COLOR_PURPLE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_BTN_DEFAULT,
    COLOR_BTN_HOVER,
    COLOR_BTN_ACTIVE,
    COLOR_BTN_BORDER,
)

if TYPE_CHECKING:
    from src.core.engine import GameEngine


class CatCard:
    """Card individual de gatinho no grid com mini-animação, status e detecção de hover/clique."""

    def __init__(self, rect: pygame.Rect, skin: CatSkin):
        self.rect = rect
        self.skin = skin
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(
        self,
        surface: pygame.Surface,
        engine: "GameEngine",
        is_selected: bool,
        is_unlocked: bool,
        is_equipped: bool,
        anim_time: float
    ) -> None:
        asset_mgr = engine.asset_manager
        current_gold = engine.save_manager.progress.get("total_gold", 0)

        # Fundo do card
        if is_equipped:
            bg_color = (28, 42, 38)
            border_color = COLOR_GREEN
            border_width = 3
        elif is_selected:
            bg_color = (36, 32, 58)
            border_color = COLOR_CYAN
            border_width = 3
        elif self.is_hovered:
            bg_color = COLOR_BTN_HOVER
            border_color = COLOR_GOLD
            border_width = 2
        else:
            bg_color = COLOR_BG_CARD
            border_color = COLOR_BG_CARD_BORDER
            border_width = 1

        # Glow se selecionado ou equipado
        if is_selected or is_equipped or self.is_hovered:
            glow_color = COLOR_GREEN if is_equipped else (COLOR_CYAN if is_selected else COLOR_GOLD)
            glow_surf = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*glow_color[:3], 35), glow_surf.get_rect(), border_radius=10)
            surface.blit(glow_surf, (self.rect.x - 4, self.rect.y - 4))

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=8)

        # Tag de Raridade
        rarity_badge_rect = pygame.Rect(self.rect.x + 6, self.rect.y + 6, len(self.skin.rarity) * 7 + 10, 16)
        pygame.draw.rect(surface, (15, 12, 22), rarity_badge_rect, border_radius=4)
        asset_mgr.render_text(
            surface,
            self.skin.rarity.upper(),
            (rarity_badge_rect.centerx, rarity_badge_rect.centery),
            size=11,
            color=self.skin.rarity_color,
            bold=True,
            align="center",
            shadow=False
        )

        # Animação do Sprite do Gato
        cat_action = "run" if self.is_hovered else "sit"
        frames = asset_mgr.get_cat_frames(self.skin.id, action=cat_action, direction="down", scale=(42, 42))
        cat_center_x = self.rect.centerx
        cat_center_y = self.rect.y + 54

        # Sombra sob o gatinho
        asset_mgr.draw_shadow(surface, cat_center_x, cat_center_y + 16, radius_x=16, radius_y=6, alpha=80)

        if frames:
            frame_idx = int(anim_time * 4) % len(frames)
            frame = frames[frame_idx]
            f_rect = frame.get_rect(center=(cat_center_x, cat_center_y))
            surface.blit(frame, f_rect)
        else:
            # Fallback
            cube_rect = pygame.Rect(cat_center_x - 14, cat_center_y - 14, 28, 28)
            asset_mgr.draw_styled_cube(surface, cube_rect, self.skin.rarity_color, glow=False)

        # Nome da Skin (cortado se necessário)
        name_display = self.skin.name
        if len(name_display) > 16:
            name_display = name_display[:15] + "…"

        asset_mgr.render_text(
            surface,
            name_display,
            (self.rect.centerx, self.rect.y + 84),
            size=13,
            color=COLOR_TEXT_LIGHT if (is_unlocked or current_gold >= self.skin.cost) else COLOR_TEXT_MUTED,
            bold=True,
            align="center",
            shadow=True
        )

        # Badge do Poder Especial
        power_badge_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 104, self.rect.width - 16, 18)
        pygame.draw.rect(surface, (18, 15, 26), power_badge_rect, border_radius=3)
        asset_mgr.render_text(
            surface,
            f"{self.skin.power_icon} {self.skin.power_name}",
            (power_badge_rect.centerx, power_badge_rect.centery),
            size=11,
            color=(210, 200, 235) if is_unlocked else (140, 135, 155),
            bold=True,
            align="center"
        )

        # Status / Preço na base do card
        pill_rect = pygame.Rect(self.rect.x + 8, self.rect.bottom - 24, self.rect.width - 16, 18)
        if is_equipped:
            pygame.draw.rect(surface, (18, 55, 30), pill_rect, border_radius=4)
            asset_mgr.render_text(
                surface,
                "EM USO",
                (pill_rect.centerx, pill_rect.centery),
                size=11,
                color=COLOR_GREEN,
                bold=True,
                align="center",
                shadow=False
            )
        elif is_unlocked:
            pygame.draw.rect(surface, (20, 45, 65), pill_rect, border_radius=4)
            asset_mgr.render_text(
                surface,
                "LIBERADO",
                (pill_rect.centerx, pill_rect.centery),
                size=11,
                color=COLOR_CYAN,
                bold=True,
                align="center",
                shadow=False
            )
        else:
            can_afford = current_gold >= self.skin.cost
            pill_bg = (50, 40, 20) if can_afford else (40, 20, 25)
            pill_text_color = COLOR_GOLD if can_afford else (230, 100, 100)
            pygame.draw.rect(surface, pill_bg, pill_rect, border_radius=4)
            asset_mgr.render_text(
                surface,
                f"🪙 {self.skin.cost} G",
                (pill_rect.centerx, pill_rect.centery),
                size=11,
                color=pill_text_color,
                bold=True,
                align="center",
                shadow=False
            )



class CatShopScene(BaseScene):
    """Cena do Santuário dos Gatos: loja e seleção de skins com ouro."""

    CARDS_PER_PAGE = 8  # 2 linhas x 4 colunas

    def __init__(self, engine: "GameEngine"):
        super().__init__(engine)
        self.particles = AmbientParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, max_particles=35)
        self.current_category = "all"
        self.current_page = 0
        self.selected_skin_id = "blue_0"
        self.anim_time = 0.0
        self.unlock_feedback_timer = 0.0
        self.unlock_feedback_text = ""
        self.preview_action = "sit"
        self.preview_action_timer = 0.0

        self.cards: List[CatCard] = []
        self.filtered_skins: List[CatSkin] = []

        self._init_layout()

    def on_enter(self) -> None:
        """Chamado sempre que a cena é aberta."""
        self.selected_skin_id = self.engine.save_manager.get_selected_skin()
        self._refresh_filtered_skins()

    def _init_layout(self) -> None:
        """Inicializa os botões de abas, paginação, inspeção e navegação."""
        # Botões de Abas de Categoria
        self.category_buttons: List[Button] = []
        tab_w = 115
        tab_h = 36
        start_x = 40
        start_y = 75
        spacing_x = tab_w + 8

        for i, (cat_key, cat_label) in enumerate(CAT_CATEGORIES):
            btn = Button(
                pygame.Rect(start_x + i * spacing_x, start_y, tab_w, tab_h),
                cat_label,
                on_click=lambda k=cat_key: self._set_category(k),
                font_size=14,
                accent_color=COLOR_CYAN if cat_key == "all" else COLOR_GOLD,
                sound_manager=self.engine.audio_manager
            )
            self.category_buttons.append(btn)

        # Painel de Inspeção à Direita
        self.inspect_rect = pygame.Rect(840, 125, 400, 500)
        self.inspect_panel = Panel(self.inspect_rect, title="DETALHES DO GATINHO")

        # Botão de Ação Principal (Desbloquear / Selecionar)
        self.btn_action = Button(
            pygame.Rect(self.inspect_rect.x + 35, self.inspect_rect.bottom - 75, self.inspect_rect.width - 70, 52),
            "SELECIONAR",
            on_click=self._on_action_clicked,
            font_size=20,
            accent_color=COLOR_CYAN,
            sound_manager=self.engine.audio_manager
        )

        # Botões de Paginação
        self.btn_prev_page = Button(
            pygame.Rect(40, 640, 140, 42),
            "◀ ANTERIOR",
            on_click=self._prev_page,
            font_size=16,
            accent_color=COLOR_PURPLE,
            sound_manager=self.engine.audio_manager
        )

        self.btn_next_page = Button(
            pygame.Rect(650, 640, 140, 42),
            "PRÓXIMO ▶",
            on_click=self._next_page,
            font_size=16,
            accent_color=COLOR_PURPLE,
            sound_manager=self.engine.audio_manager
        )

        # Botão Voltar ao Menu
        self.btn_back = Button(
            pygame.Rect(self.inspect_rect.x + 35, 640, self.inspect_rect.width - 70, 42),
            "← VOLTAR AO MENU",
            on_click=self._back_to_menu,
            font_size=16,
            accent_color=COLOR_GOLD,
            sound_manager=self.engine.audio_manager
        )

        self._refresh_filtered_skins()

    def _set_category(self, category: str) -> None:
        """Troca a categoria ativa e reseta a página."""
        self.current_category = category
        self.current_page = 0
        self._refresh_filtered_skins()

    def _refresh_filtered_skins(self) -> None:
        """Filtra as skins e reconstrói os cards da página atual."""
        unlocked = self.engine.save_manager.get_unlocked_skins()
        self.filtered_skins = get_skins_by_category(self.current_category, unlocked_ids=unlocked)

        # Garante página válida
        max_pages = max(1, math.ceil(len(self.filtered_skins) / self.CARDS_PER_PAGE))
        if self.current_page >= max_pages:
            self.current_page = max_pages - 1

        # Reconstrói os 8 cards da página
        self.cards.clear()
        start_idx = self.current_page * self.CARDS_PER_PAGE
        page_skins = self.filtered_skins[start_idx:start_idx + self.CARDS_PER_PAGE]

        grid_start_x = 40
        grid_start_y = 130
        card_w = 175
        card_h = 240
        gap_x = 18
        gap_y = 16

        for i, skin in enumerate(page_skins):
            col = i % 4
            row = i // 4
            x = grid_start_x + col * (card_w + gap_x)
            y = grid_start_y + row * (card_h + gap_y)
            self.cards.append(CatCard(pygame.Rect(x, y, card_w, card_h), skin))

    def _prev_page(self) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            self._refresh_filtered_skins()

    def _next_page(self) -> None:
        max_pages = max(1, math.ceil(len(self.filtered_skins) / self.CARDS_PER_PAGE))
        if self.current_page < max_pages - 1:
            self.current_page += 1
            self._refresh_filtered_skins()

    def _back_to_menu(self) -> None:
        self.engine.change_scene("main_menu")

    def _on_action_clicked(self) -> None:
        """Executa a ação contextual (desbloquear ou equipar)."""
        skin = get_skin(self.selected_skin_id)
        save_mgr = self.engine.save_manager
        is_unlocked = save_mgr.is_skin_unlocked(skin.id)
        equipped_id = save_mgr.get_selected_skin()

        if is_unlocked:
            if equipped_id != skin.id:
                save_mgr.set_selected_skin(skin.id)
                self.unlock_feedback_text = f"✨ {skin.name} equipado com sucesso!"
                self.unlock_feedback_timer = 2.5
                self.engine.audio_manager.play_sfx("ui_select")
        else:
            # Tenta desbloquear
            if save_mgr.unlock_skin(skin.id, skin.cost):
                self.unlock_feedback_text = f"🎉 Parabéns! {skin.name} desbloqueado e equipado!"
                self.unlock_feedback_timer = 3.5
                self.engine.audio_manager.play_sfx("levelup")
                self._refresh_filtered_skins()
            else:
                self.unlock_feedback_text = "❌ Ouro insuficiente para desbloquear!"
                self.unlock_feedback_timer = 2.0
                self.engine.audio_manager.play_sfx("hit")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Trata eventos de clique, teclado e navegação."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back_to_menu()
                return
            elif event.key == pygame.K_LEFT:
                self._prev_page()
                return
            elif event.key == pygame.K_RIGHT:
                self._next_page()
                return
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._on_action_clicked()
                return

        # Abas
        for btn in self.category_buttons:
            if btn.handle_event(event):
                return

        # Cards
        for card in self.cards:
            if card.handle_event(event):
                self.selected_skin_id = card.skin.id
                self.engine.audio_manager.play_sfx("ui_click")
                return

        # Botões de paginação e ação
        if self.btn_prev_page.handle_event(event):
            return
        if self.btn_next_page.handle_event(event):
            return
        if self.btn_action.handle_event(event):
            return
        if self.btn_back.handle_event(event):
            return

    def update(self, dt: float) -> None:
        """Atualiza animações de tempo e estados de botões."""
        self.anim_time += dt
        self.particles.update(dt)

        if self.unlock_feedback_timer > 0:
            self.unlock_feedback_timer -= dt

        # Alterna ações de animação do gatinho inspecionado (sit -> walk -> run -> beg)
        self.preview_action_timer += dt
        if self.preview_action_timer > 3.0:
            self.preview_action_timer = 0.0
            actions = ["sit", "walk", "run", "beg", "look"]
            current_idx = actions.index(self.preview_action) if self.preview_action in actions else 0
            self.preview_action = actions[(current_idx + 1) % len(actions)]

        # Atualiza botões
        for btn in self.category_buttons:
            btn.update(dt)

        max_pages = max(1, math.ceil(len(self.filtered_skins) / self.CARDS_PER_PAGE))
        self.btn_prev_page.disabled = (self.current_page == 0)
        self.btn_next_page.disabled = (self.current_page >= max_pages - 1)

        self.btn_prev_page.update(dt)
        self.btn_next_page.update(dt)
        self.btn_back.update(dt)
        self._update_action_button()
        self.btn_action.update(dt)

    def _update_action_button(self) -> None:
        """Atualiza o texto, cor e estado do botão de ação contextual."""
        skin = get_skin(self.selected_skin_id)
        save_mgr = self.engine.save_manager
        is_unlocked = save_mgr.is_skin_unlocked(skin.id)
        is_equipped = (save_mgr.get_selected_skin() == skin.id)
        current_gold = save_mgr.progress.get("total_gold", 0)

        if is_equipped:
            self.btn_action.text = "✓ GATINHO EM USO"
            self.btn_action.accent_color = COLOR_GREEN
            self.btn_action.disabled = True
        elif is_unlocked:
            self.btn_action.text = "EQUIPAR GATINHO"
            self.btn_action.accent_color = COLOR_CYAN
            self.btn_action.disabled = False
        else:
            if current_gold >= skin.cost:
                self.btn_action.text = f"DESBLOQUEAR (🪙 {skin.cost} G)"
                self.btn_action.accent_color = COLOR_GOLD
                self.btn_action.disabled = False
            else:
                self.btn_action.text = f"FALTA OURO (🪙 {skin.cost} G)"
                self.btn_action.accent_color = COLOR_RED
                self.btn_action.disabled = True

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza a interface completa do Santuário dos Gatos."""
        asset_mgr = engine_mgr = self.engine.asset_manager

        # Plano de fundo com imagem BG.jpg e overlay escuro
        bg = asset_mgr.get_background((SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg:
            surface.blit(bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 8, 18, 175))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill(COLOR_BG)

        # Partículas
        self.particles.draw(surface)

        # Cabeçalho Principal
        asset_mgr.render_text(
            surface,
            "SANTUÁRIO DOS GATINHOS",
            (40, 22),
            size=36,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            shadow=True
        )

        asset_mgr.render_text(
            surface,
            "Desbloqueie novas skins com seu ouro e escolha seu herói felino para as partidas",
            (40, 56),
            size=14,
            color=COLOR_TEXT_MUTED,
            shadow=True
        )

        # Badge de Ouro no Topo Direito
        current_gold = self.engine.save_manager.progress.get("total_gold", 0)
        gold_badge_rect = pygame.Rect(SCREEN_WIDTH - 280, 20, 240, 44)
        pygame.draw.rect(surface, (28, 22, 12), gold_badge_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, gold_badge_rect, width=2, border_radius=8)

        # Moeda decorativa com brilho
        coin_pulse = math.sin(self.anim_time * 4.0) * 2
        coin_rect = pygame.Rect(gold_badge_rect.x + 14, gold_badge_rect.centery - 10 + int(coin_pulse), 20, 20)
        asset_mgr.draw_styled_cube(surface, coin_rect, COLOR_GOLD, glow=True)

        asset_mgr.render_text(
            surface,
            f"{current_gold:,} OURO".replace(",", "."),
            (gold_badge_rect.centerx + 12, gold_badge_rect.centery),
            size=18,
            color=COLOR_GOLD,
            bold=True,
            align="center",
            shadow=True
        )

        # Renderiza Abas de Categoria
        for i, btn in enumerate(self.category_buttons):
            cat_key = CAT_CATEGORIES[i][0]
            if cat_key == self.current_category:
                btn.accent_color = COLOR_GOLD
                btn.draw(surface, asset_mgr)
            else:
                btn.accent_color = (70, 65, 90)
                btn.draw(surface, asset_mgr)

        # Renderiza Grid de Cards
        save_mgr = self.engine.save_manager
        equipped_id = save_mgr.get_selected_skin()
        unlocked_skins = save_mgr.get_unlocked_skins()

        for card in self.cards:
            is_selected = (card.skin.id == self.selected_skin_id)
            is_unlocked = (card.skin.id in unlocked_skins)
            is_equipped = (card.skin.id == equipped_id)
            card.draw(surface, self.engine, is_selected, is_unlocked, is_equipped, self.anim_time)

        # Mensagem se categoria vazia
        if not self.cards:
            asset_mgr.render_text(
                surface,
                "Nenhum gatinho encontrado nesta categoria.",
                (400, 360),
                size=20,
                color=COLOR_TEXT_MUTED,
                align="center"
            )

        # Paginação
        max_pages = max(1, math.ceil(len(self.filtered_skins) / self.CARDS_PER_PAGE))
        page_info = f"Página {self.current_page + 1} de {max_pages} ({len(self.filtered_skins)} Gatinhos)"
        asset_mgr.render_text(
            surface,
            page_info,
            (415, 660),
            size=16,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=True
        )

        self.btn_prev_page.draw(surface, asset_mgr)
        self.btn_next_page.draw(surface, asset_mgr)

        # Renderiza Painel de Inspeção do Gatinho Selecionado
        self._draw_inspector_panel(surface)

        # Botão Voltar
        self.btn_back.draw(surface, asset_mgr)

        # Feedback Toast Flutuante (ex: "Desbloqueado com sucesso!")
        if self.unlock_feedback_timer > 0:
            toast_w = 480
            toast_h = 44
            toast_rect = pygame.Rect(SCREEN_WIDTH // 2 - toast_w // 2, SCREEN_HEIGHT - 65, toast_w, toast_h)
            pygame.draw.rect(surface, (18, 14, 30), toast_rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_GOLD, toast_rect, width=2, border_radius=8)
            asset_mgr.render_text(
                surface,
                self.unlock_feedback_text,
                (toast_rect.centerx, toast_rect.centery),
                size=16,
                color=COLOR_TEXT_LIGHT,
                bold=True,
                align="center",
                shadow=True
            )

    def _draw_inspector_panel(self, surface: pygame.Surface) -> None:
        """Renderiza os detalhes ampliados do gatinho selecionado à direita."""
        asset_mgr = self.engine.asset_manager
        save_mgr = self.engine.save_manager
        skin = get_skin(self.selected_skin_id)
        is_unlocked = save_mgr.is_skin_unlocked(skin.id)
        is_equipped = (save_mgr.get_selected_skin() == skin.id)

        self.inspect_panel.draw(surface, asset_mgr)

        p_x = self.inspect_rect.x
        p_y = self.inspect_rect.y

        # Exibição Grande do Sprite Animado
        preview_scale = (68, 68)
        preview_center_x = self.inspect_rect.centerx
        preview_center_y = p_y + 82

        # Sombra sob o gato grande
        asset_mgr.draw_shadow(surface, preview_center_x, preview_center_y + 30, radius_x=26, radius_y=9, alpha=90)

        # Animação
        frames = asset_mgr.get_cat_frames(skin.id, action=self.preview_action, direction="down", scale=preview_scale)
        if frames:
            frame_idx = int(self.anim_time * 4) % len(frames)
            frame = frames[frame_idx]
            f_rect = frame.get_rect(center=(preview_center_x, preview_center_y))
            surface.blit(frame, f_rect)
        else:
            cube_rect = pygame.Rect(preview_center_x - 24, preview_center_y - 24, 48, 48)
            asset_mgr.draw_styled_cube(surface, cube_rect, skin.rarity_color, glow=True)

        # Tag de Raridade
        rarity_text = f"★ RARIDADE: {skin.rarity.upper()} ★"
        asset_mgr.render_text(
            surface,
            rarity_text,
            (self.inspect_rect.centerx, p_y + 130),
            size=13,
            color=skin.rarity_color,
            bold=True,
            align="center",
            shadow=True
        )

        # Nome da Skin
        asset_mgr.render_text(
            surface,
            skin.name,
            (self.inspect_rect.centerx, p_y + 154),
            size=20,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=True
        )

        # Divisor
        pygame.draw.line(
            surface,
            COLOR_BG_CARD_BORDER,
            (p_x + 25, p_y + 178),
            (p_x + self.inspect_rect.width - 25, p_y + 178),
            1
        )

        # Descrição / Lore (Quebra de linha simples)
        words = skin.description.split()
        lines: List[str] = []
        cur_line = ""
        for w in words:
            if len(cur_line + " " + w) <= 32:
                cur_line = (cur_line + " " + w).strip()
            else:
                lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)

        desc_y = p_y + 188
        for line in lines:
            asset_mgr.render_text(
                surface,
                line,
                (self.inspect_rect.centerx, desc_y),
                size=13,
                color=COLOR_TEXT_MUTED,
                align="center",
                shadow=False
            )
            desc_y += 18

        # --- Caixa de Poder Especial ---
        power_box_rect = pygame.Rect(p_x + 25, p_y + 236, self.inspect_rect.width - 50, 78)
        pygame.draw.rect(surface, (22, 18, 34), power_box_rect, border_radius=6)
        pygame.draw.rect(surface, (90, 75, 125), power_box_rect, width=1, border_radius=6)

        asset_mgr.render_text(
            surface,
            f"{skin.power_icon} PODER: {skin.power_name.upper()}",
            (power_box_rect.x + 12, power_box_rect.y + 8),
            size=14,
            color=COLOR_GOLD if skin.power_id != "none" else COLOR_TEXT_MUTED,
            bold=True
        )

        # Quebra de linha da descrição do poder
        p_words = skin.power_desc.split()
        p_lines: List[str] = []
        p_cur = ""
        for w in p_words:
            if len(p_cur + " " + w) <= 36:
                p_cur = (p_cur + " " + w).strip()
            else:
                p_lines.append(p_cur)
                p_cur = w
        if p_cur:
            p_lines.append(p_cur)

        p_desc_y = power_box_rect.y + 28
        for p_line in p_lines:
            asset_mgr.render_text(
                surface,
                p_line,
                (power_box_rect.x + 12, p_desc_y),
                size=12,
                color=COLOR_TEXT_LIGHT if skin.power_id != "none" else COLOR_TEXT_MUTED,
                shadow=False
            )
            p_desc_y += 16

        # Caixa de Status / Custo
        status_box = pygame.Rect(p_x + 25, p_y + 326, self.inspect_rect.width - 50, 56)
        pygame.draw.rect(surface, (20, 17, 30), status_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_BG_CARD_BORDER, status_box, width=1, border_radius=6)

        if is_equipped:
            asset_mgr.render_text(
                surface,
                "STATUS: EQUIPADO ATUALMENTE",
                (status_box.centerx, status_box.y + 14),
                size=13,
                color=COLOR_GREEN,
                bold=True,
                align="center"
            )
            asset_mgr.render_text(
                surface,
                "Este gatinho liderará a próxima batalha!",
                (status_box.centerx, status_box.y + 32),
                size=12,
                color=COLOR_TEXT_MUTED,
                align="center"
            )
        elif is_unlocked:
            asset_mgr.render_text(
                surface,
                "STATUS: DESBLOQUEADO",
                (status_box.centerx, status_box.y + 14),
                size=13,
                color=COLOR_CYAN,
                bold=True,
                align="center"
            )
            asset_mgr.render_text(
                surface,
                "Pronto para ser equipado a qualquer momento.",
                (status_box.centerx, status_box.y + 32),
                size=12,
                color=COLOR_TEXT_MUTED,
                align="center"
            )
        else:
            asset_mgr.render_text(
                surface,
                f"PREÇO: 🪙 {skin.cost} OURO",
                (status_box.centerx, status_box.y + 14),
                size=14,
                color=COLOR_GOLD,
                bold=True,
                align="center"
            )
            asset_mgr.render_text(
                surface,
                "Colete ouro derrotando monstros nas partidas!",
                (status_box.centerx, status_box.y + 32),
                size=12,
                color=COLOR_TEXT_MUTED,
                align="center"
            )

        # Botão de Ação
        self.btn_action.draw(surface, asset_mgr)

