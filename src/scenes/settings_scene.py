"""
Cena de Configurações completa com abas para Áudio, Vídeo e Controles, e persistência em saves/settings.json.
"""
import pygame
from typing import TYPE_CHECKING
from src.scenes.base_scene import BaseScene
from src.ui.components import Button, Slider, ToggleSwitch, Panel
from src.ui.particle import AmbientParticleSystem
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_GOLD,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_PURPLE,
    COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_PLAYER_CUBE,
)

if TYPE_CHECKING:
    from src.core.engine import GameEngine


class SettingsScene(BaseScene):
    """Tela de configurações com ajuste de volumes, vídeo e guia de controles."""

    def __init__(self, engine: "GameEngine"):
        super().__init__(engine)
        self.particles = AmbientParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT, max_particles=30)
        self.current_tab = "audio"  # 'audio', 'video', 'controls'
        self.save_feedback_timer = 0.0

        # Carrega cópia de trabalho das configurações
        self.temp_settings = dict(self.engine.save_manager.settings)

        self._init_layout()

    def _init_layout(self) -> None:
        """Inicializa abas, controles de áudio, vídeo e botões de ação."""
        panel_w = 780
        panel_h = 470
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 130
        self.main_panel = Panel(pygame.Rect(panel_x, panel_y, panel_w, panel_h))

        # Botões de Abas
        tab_w = 230
        tab_h = 42
        tab_start_x = panel_x + 25
        tab_y = panel_y - tab_h - 10

        self.tab_audio = Button(
            pygame.Rect(tab_start_x, tab_y, tab_w, tab_h),
            "ÁUDIO",
            on_click=lambda: self._set_tab("audio"),
            accent_color=COLOR_CYAN,
            font_size=20,
            sound_manager=self.engine.audio_manager
        )

        self.tab_video = Button(
            pygame.Rect(tab_start_x + tab_w + 15, tab_y, tab_w, tab_h),
            "VÍDEO",
            on_click=lambda: self._set_tab("video"),
            accent_color=COLOR_GOLD,
            font_size=20,
            sound_manager=self.engine.audio_manager
        )

        self.tab_controls = Button(
            pygame.Rect(tab_start_x + (tab_w + 15) * 2, tab_y, tab_w, tab_h),
            "CONTROLES",
            on_click=lambda: self._set_tab("controls"),
            accent_color=COLOR_PURPLE,
            font_size=20,
            sound_manager=self.engine.audio_manager
        )

        self.tab_buttons = [self.tab_audio, self.tab_video, self.tab_controls]

        # --- Controles da Aba Áudio ---
        slider_x = panel_x + 40
        slider_w = panel_w - 80
        start_ctrl_y = panel_y + 40
        spacing = 70

        self.slider_master = Slider(
            pygame.Rect(slider_x, start_ctrl_y, slider_w, 40),
            "Volume Geral:",
            value=self.temp_settings.get("master_volume", 0.8),
            on_change=self._on_master_vol_changed,
            sound_manager=self.engine.audio_manager
        )

        self.slider_music = Slider(
            pygame.Rect(slider_x, start_ctrl_y + spacing, slider_w, 40),
            "Música de Fundo:",
            value=self.temp_settings.get("music_volume", 0.7),
            on_change=self._on_music_vol_changed,
            sound_manager=self.engine.audio_manager
        )

        self.slider_sfx = Slider(
            pygame.Rect(slider_x, start_ctrl_y + spacing * 2, slider_w, 40),
            "Efeitos Sonoros (SFX):",
            value=self.temp_settings.get("sfx_volume", 0.9),
            on_change=self._on_sfx_vol_changed,
            sound_manager=self.engine.audio_manager
        )

        self.btn_test_sfx = Button(
            pygame.Rect(slider_x, start_ctrl_y + spacing * 3 + 10, 220, 42),
            "Testar Som",
            on_click=lambda: self.engine.audio_manager.play_sfx("levelup"),
            accent_color=COLOR_CYAN,
            font_size=18,
            sound_manager=self.engine.audio_manager
        )

        # --- Controles da Aba Vídeo ---
        toggle_spacing = 60
        self.toggle_fullscreen = ToggleSwitch(
            pygame.Rect(slider_x, start_ctrl_y, slider_w, 40),
            "Modo Tela Cheia:",
            value=self.temp_settings.get("fullscreen", False),
            on_toggle=lambda v: self._update_temp("fullscreen", v),
            sound_manager=self.engine.audio_manager
        )

        self.toggle_vsync = ToggleSwitch(
            pygame.Rect(slider_x, start_ctrl_y + toggle_spacing, slider_w, 40),
            "Sincronização Vertical (V-Sync):",
            value=self.temp_settings.get("vsync", True),
            on_toggle=lambda v: self._update_temp("vsync", v),
            sound_manager=self.engine.audio_manager
        )

        self.toggle_shake = ToggleSwitch(
            pygame.Rect(slider_x, start_ctrl_y + toggle_spacing * 2, slider_w, 40),
            "Tremor de Tela ao Sofrer Dano:",
            value=self.temp_settings.get("screen_shake", True),
            on_toggle=lambda v: self._update_temp("screen_shake", v),
            sound_manager=self.engine.audio_manager
        )

        self.toggle_fps = ToggleSwitch(
            pygame.Rect(slider_x, start_ctrl_y + toggle_spacing * 3, slider_w, 40),
            "Exibir Contador de FPS:",
            value=self.temp_settings.get("show_fps", True),
            on_toggle=lambda v: self._update_temp("show_fps", v),
            sound_manager=self.engine.audio_manager
        )

        # --- Botões Inferiores ---
        btn_action_y = panel_y + panel_h + 20
        btn_action_w = 220
        btn_action_h = 48

        self.btn_save = Button(
            pygame.Rect(panel_x, btn_action_y, btn_action_w, btn_action_h),
            "SALVAR CONFIGURAÇÕES",
            on_click=self._save_settings,
            accent_color=COLOR_GREEN,
            sound_manager=self.engine.audio_manager
        )

        self.btn_reset = Button(
            pygame.Rect(panel_x + btn_action_w + 30, btn_action_y, btn_action_w, btn_action_h),
            "RESTAURAR PADRÃO",
            on_click=self._reset_defaults,
            accent_color=COLOR_PURPLE,
            sound_manager=self.engine.audio_manager
        )

        self.btn_back = Button(
            pygame.Rect(panel_x + panel_w - btn_action_w, btn_action_y, btn_action_w, btn_action_h),
            "VOLTAR AO MENU",
            on_click=self._go_back,
            accent_color=COLOR_GOLD,
            sound_manager=self.engine.audio_manager
        )

    def _set_tab(self, tab_name: str) -> None:
        """Alterna a aba ativa."""
        self.current_tab = tab_name

    def _update_temp(self, key: str, value) -> None:
        """Atualiza valor temporário."""
        self.temp_settings[key] = value

    def _on_master_vol_changed(self, val: float) -> None:
        self.temp_settings["master_volume"] = val
        self.engine.audio_manager.set_master_volume(val)

    def _on_music_vol_changed(self, val: float) -> None:
        self.temp_settings["music_volume"] = val
        self.engine.audio_manager.set_music_volume(val)

    def _on_sfx_vol_changed(self, val: float) -> None:
        self.temp_settings["sfx_volume"] = val
        self.engine.audio_manager.set_sfx_volume(val)

    def _save_settings(self) -> None:
        """Persiste as configurações no disco e aplica alterações de vídeo se necessário."""
        self.engine.save_manager.settings = dict(self.temp_settings)
        self.engine.save_manager.save_settings()
        self.engine.apply_video_settings()
        self.engine.audio_manager.play_sfx("ui_select")
        self.save_feedback_timer = 2.0

    def _reset_defaults(self) -> None:
        """Restaura valores padrão."""
        self.engine.save_manager.reset_settings()
        self.temp_settings = dict(self.engine.save_manager.settings)
        self.slider_master.value = self.temp_settings["master_volume"]
        self.slider_music.value = self.temp_settings["music_volume"]
        self.slider_sfx.value = self.temp_settings["sfx_volume"]
        self.toggle_fullscreen.value = self.temp_settings["fullscreen"]
        self.toggle_vsync.value = self.temp_settings["vsync"]
        self.toggle_shake.value = self.temp_settings["screen_shake"]
        self.toggle_fps.value = self.temp_settings["show_fps"]
        self.engine.audio_manager.set_master_volume(self.temp_settings["master_volume"])
        self.engine.audio_manager.set_music_volume(self.temp_settings["music_volume"])
        self.engine.audio_manager.set_sfx_volume(self.temp_settings["sfx_volume"])
        self.engine.audio_manager.play_sfx("ui_select")
        self.save_feedback_timer = 2.0

    def _go_back(self) -> None:
        """Retorna ao Menu Principal."""
        self.engine.change_scene("main_menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos de teclado e botões."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_back()
            return

        # Abas
        for tab_btn in self.tab_buttons:
            if tab_btn.handle_event(event):
                return

        # Controles da aba ativa
        if self.current_tab == "audio":
            self.slider_master.handle_event(event)
            self.slider_music.handle_event(event)
            self.slider_sfx.handle_event(event)
            self.btn_test_sfx.handle_event(event)

        elif self.current_tab == "video":
            self.toggle_fullscreen.handle_event(event)
            self.toggle_vsync.handle_event(event)
            self.toggle_shake.handle_event(event)
            self.toggle_fps.handle_event(event)

        # Botões de Ação
        self.btn_save.handle_event(event)
        self.btn_reset.handle_event(event)
        self.btn_back.handle_event(event)

    def update(self, dt: float) -> None:
        """Atualiza animações e timers."""
        self.particles.update(dt)

        for tab_btn in self.tab_buttons:
            tab_btn.update(dt)

        if self.current_tab == "audio":
            self.btn_test_sfx.update(dt)
        elif self.current_tab == "video":
            self.toggle_fullscreen.update(dt)
            self.toggle_vsync.update(dt)
            self.toggle_shake.update(dt)
            self.toggle_fps.update(dt)

        self.btn_save.update(dt)
        self.btn_reset.update(dt)
        self.btn_back.update(dt)

        if self.save_feedback_timer > 0:
            self.save_feedback_timer = max(0.0, self.save_feedback_timer - dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza a tela de configurações."""
        # Plano de fundo com imagem BG.jpg e overlay escuro translúcido
        bg = self.engine.asset_manager.get_background((SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg:
            surface.blit(bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((12, 10, 20, 150))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill(COLOR_BG)
        self.particles.draw(surface)

        # Cabeçalho da tela
        self.engine.asset_manager.render_text(
            surface,
            "CONFIGURAÇÕES",
            (SCREEN_WIDTH // 2, 45),
            size=40,
            color=COLOR_TEXT_LIGHT,
            bold=True,
            align="center",
            shadow=True
        )

        # Renderiza Abas
        for tab_btn in self.tab_buttons:
            tab_btn.draw(surface, self.engine.asset_manager)

        # Painel de Conteúdo
        self.main_panel.draw(surface, self.engine.asset_manager)

        # Conteúdo da Aba Áudio
        if self.current_tab == "audio":
            self.slider_master.draw(surface, self.engine.asset_manager)
            self.slider_music.draw(surface, self.engine.asset_manager)
            self.slider_sfx.draw(surface, self.engine.asset_manager)
            self.btn_test_sfx.draw(surface, self.engine.asset_manager)

        # Conteúdo da Aba Vídeo
        elif self.current_tab == "video":
            self.toggle_fullscreen.draw(surface, self.engine.asset_manager)
            self.toggle_vsync.draw(surface, self.engine.asset_manager)
            self.toggle_shake.draw(surface, self.engine.asset_manager)
            self.toggle_fps.draw(surface, self.engine.asset_manager)

        # Conteúdo da Aba Controles
        elif self.current_tab == "controls":
            ctrl_x = self.main_panel.rect.x + 40
            ctrl_y = self.main_panel.rect.y + 40

            controls_list = [
                ("Mover Personagem:", "Teclas [W, A, S, D] ou [Setas do Teclado]"),
                ("Disparo de Projéteis:", "Automático nos inimigos mais próximos"),
                ("Menu de Pausa / Voltar:", "Tecla [ESC]"),
                ("Coleta de Experiência / Ouro:", "Aproxime-se dos cubos e gemas caídos"),
                ("Objetivo:", "Sobreviva ao máximo de ondas e acumule ouro!")
            ]

            for i, (action, desc) in enumerate(controls_list):
                row_y = ctrl_y + i * 54
                # Ícone em cubo decorativo
                cube_rect = pygame.Rect(ctrl_x, row_y + 4, 16, 16)
                self.engine.asset_manager.draw_styled_cube(
                    surface,
                    cube_rect,
                    COLOR_PLAYER_CUBE if i == 0 else COLOR_GOLD,
                    glow=False
                )

                self.engine.asset_manager.render_text(
                    surface,
                    action,
                    (ctrl_x + 30, row_y),
                    size=20,
                    color=COLOR_GOLD,
                    bold=True,
                    align="topleft"
                )
                self.engine.asset_manager.render_text(
                    surface,
                    desc,
                    (ctrl_x + 30, row_y + 24),
                    size=18,
                    color=COLOR_TEXT_LIGHT,
                    align="topleft"
                )

        # Botões de Ação no Rodapé
        self.btn_save.draw(surface, self.engine.asset_manager)
        self.btn_reset.draw(surface, self.engine.asset_manager)
        self.btn_back.draw(surface, self.engine.asset_manager)

        # Notificação de Confirmação de Salvamento
        if self.save_feedback_timer > 0:
            alpha = int(255 * min(1.0, self.save_feedback_timer))
            notif_surf = pygame.Surface((320, 36), pygame.SRCALPHA)
            pygame.draw.rect(notif_surf, (34, 197, 94, int(alpha * 0.8)), notif_surf.get_rect(), border_radius=6)
            surface.blit(notif_surf, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 50))
            self.engine.asset_manager.render_text(
                surface,
                "✓ Configurações salvas no disco!",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 32),
                size=18,
                color=COLOR_TEXT_LIGHT,
                bold=True,
                align="center",
                shadow=False
            )
