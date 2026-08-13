"""
Cena do Menu Principal com estética Neon/Dark, animação de título, partículas e navegação para jogo e configurações.
"""
import math
import pygame
from typing import TYPE_CHECKING
from src.scenes.base_scene import BaseScene
from src.ui.components import Button, Panel
from src.ui.particle import AmbientParticleSystem
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_GOLD,
    COLOR_CYAN,
    COLOR_PURPLE,
    COLOR_RED,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_PLAYER_CUBE,
)

if TYPE_CHECKING:
    from src.core.engine import GameEngine


class MainMenuScene(BaseScene):
    """Menu Principal interativo do jogo."""

    def __init__(self, engine: "GameEngine"):
        super().__init__(engine)
        self.particles = AmbientParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, max_particles=45)
        self.buttons = []
        self.show_stats_modal = False
        self.anim_time = 0.0
        self._init_buttons()

    def _init_buttons(self) -> None:
        """Inicializa os botões do menu."""
        btn_w = 340
        btn_h = 56
        center_x = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 280
        spacing = 68

        self.btn_play = Button(
            pygame.Rect(center_x, start_y, btn_w, btn_h),
            "JOGAR",
            on_click=self._on_play_clicked,
            accent_color=COLOR_CYAN,
            icon_cube_color=COLOR_PLAYER_CUBE,
            sound_manager=self.engine.audio_manager
        )

        self.btn_settings = Button(
            pygame.Rect(center_x, start_y + spacing, btn_w, btn_h),
            "CONFIGURAÇÕES",
            on_click=self._on_settings_clicked,
            accent_color=COLOR_GOLD,
            icon_cube_color=COLOR_GOLD,
            sound_manager=self.engine.audio_manager
        )

        self.btn_stats = Button(
            pygame.Rect(center_x, start_y + spacing * 2, btn_w, btn_h),
            "ESTATÍSTICAS",
            on_click=self._toggle_stats,
            accent_color=COLOR_PURPLE,
            icon_cube_color=COLOR_PURPLE,
            sound_manager=self.engine.audio_manager
        )

        self.btn_quit = Button(
            pygame.Rect(center_x, start_y + spacing * 3, btn_w, btn_h),
            "SAIR DO JOGO",
            on_click=self._on_quit_clicked,
            accent_color=COLOR_RED,
            icon_cube_color=COLOR_RED,
            sound_manager=self.engine.audio_manager
        )

        self.buttons = [self.btn_play, self.btn_settings, self.btn_stats, self.btn_quit]

        # Botão fechar modal de estatísticas
        modal_w, modal_h = 500, 380
        modal_x = SCREEN_WIDTH // 2 - modal_w // 2
        modal_y = SCREEN_HEIGHT // 2 - modal_h // 2
        self.stats_panel = Panel(pygame.Rect(modal_x, modal_y, modal_w, modal_h), title="ESTATÍSTICAS DA CONTA")
        self.btn_close_stats = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 90, modal_y + modal_h - 60, 180, 42),
            "FECHAR",
            on_click=self._toggle_stats,
            accent_color=COLOR_GOLD,
            sound_manager=self.engine.audio_manager
        )

    def _on_play_clicked(self) -> None:
        """Inicia a cena de jogo."""
        self.engine.change_scene("gameplay")

    def _on_settings_clicked(self) -> None:
        """Abre a cena de configurações."""
        self.engine.change_scene("settings")

    def _toggle_stats(self) -> None:
        """Abre/fecha o painel de estatísticas."""
        self.show_stats_modal = not self.show_stats_modal

    def _on_quit_clicked(self) -> None:
        """Encerra o jogo."""
        self.engine.quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Repassa eventos para botões ou fecha modal com ESC."""
        if self.show_stats_modal:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_stats_modal = False
                return
            self.btn_close_stats.handle_event(event)
            return

        for btn in self.buttons:
            if btn.handle_event(event):
                break

    def update(self, dt: float) -> None:
        """Atualiza animações de tempo, partículas e botões."""
        self.anim_time += dt
        self.particles.update(dt)

        if self.show_stats_modal:
            self.btn_close_stats.update(dt)
        else:
            for btn in self.buttons:
                btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza o Menu Principal."""
        # Plano de fundo com imagem BG.jpg e overlay translúcido para contraste
        bg = self.engine.asset_manager.get_background((SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg:
            surface.blit(bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((12, 10, 20, 130))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill(COLOR_BG)

        # Partículas de fundo
        self.particles.draw(surface)

        # Título animado com pulso suave e brilho
        pulse = math.sin(self.anim_time * 2.5) * 4
        title_y = 90 + int(pulse)

        # Cubo decorativo girando/pulsando no cabeçalho
        # Gatinho protagonista animado acima do título
        cat_frames = self.engine.asset_manager.get_cat_frames("blue_0", action="sit", direction="down", scale=(54, 54))
        if cat_frames:
            self.engine.asset_manager.draw_shadow(
                surface,
                SCREEN_WIDTH // 2,
                title_y - 20,
                radius_x=20,
                radius_y=8,
                alpha=85
            )
            frame_idx = int(self.anim_time * 3.5) % len(cat_frames)
            frame = cat_frames[frame_idx]
            c_rect = frame.get_rect(center=(SCREEN_WIDTH // 2, title_y - 45))
            surface.blit(frame, c_rect)
        else:
            hero_cube_size = 32
            hero_cube_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - hero_cube_size // 2,
                title_y - 45,
                hero_cube_size,
                hero_cube_size
            )
            self.engine.asset_manager.draw_styled_cube(
                surface,
                hero_cube_rect,
                COLOR_PLAYER_CUBE,
                glow=True
            )

        self.engine.asset_manager.render_text(
            surface,
            "BULLET HEAVEN",
            (SCREEN_WIDTH // 2, title_y),
            size=56,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=True,
            shadow_offset=(3, 4)
        )

        self.engine.asset_manager.render_text(
            surface,
            "SURVIVORS PROTOTYPE",
            (SCREEN_WIDTH // 2, title_y + 48),
            size=20,
            color=COLOR_GOLD,
            bold=True,
            align="center",
            shadow=True
        )

        # Renderiza os botões principais
        for btn in self.buttons:
            btn.draw(surface, self.engine.asset_manager)

        # Rodapé com status de progresso e atalhos
        progress = self.engine.save_manager.progress
        gold = progress.get("total_gold", 0)
        kills = progress.get("total_kills", 0)
        high_score = progress.get("high_score", 0)

        footer_text = f"Ouro Acumulado: {gold}  |  Inimigos Derrotados: {kills}  |  Recorde de Pontos: {high_score}"
        self.engine.asset_manager.render_text(
            surface,
            footer_text,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 32),
            size=18,
            color=COLOR_TEXT_MUTED,
            align="center",
            shadow=True
        )

        # Modal de estatísticas detalhadas se estiver ativo
        if self.show_stats_modal:
            # Overlay escuro transparente
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            # Painel central
            self.stats_panel.draw(surface, self.engine.asset_manager)

            stats_lines = [
                ("Partidas Jogadas:", f"{progress.get('games_played', 0)}"),
                ("Recorde de Pontuação:", f"{high_score} pts"),
                ("Total de Eliminações:", f"{kills} monstros"),
                ("Tempo Recorde Sobrevivido:", f"{int(progress.get('time_survived_record_sec', 0))} seg"),
                ("Total de Ouro:", f"{gold} G"),
                ("Localização do Save:", "saves/progress.json"),
            ]

            start_text_y = self.stats_panel.rect.y + 70
            for i, (label, val) in enumerate(stats_lines):
                row_y = start_text_y + i * 36
                self.engine.asset_manager.render_text(
                    surface,
                    label,
                    (self.stats_panel.rect.x + 35, row_y),
                    size=19,
                    color=COLOR_TEXT_LIGHT,
                    align="topleft"
                )
                self.engine.asset_manager.render_text(
                    surface,
                    val,
                    (self.stats_panel.rect.right - 35, row_y),
                    size=19,
                    color=COLOR_GOLD,
                    bold=True,
                    align="topright"
                )

            self.btn_close_stats.draw(surface, self.engine.asset_manager)
