"""
Motor principal do jogo (GameEngine): gerencia a janela, loop de eventos a 60 FPS,
gerenciamento de estados de cena e persistência.
"""
import sys
import pygame
from typing import Dict, Optional
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TARGET_FPS,
    WINDOW_TITLE,
)
from src.core.save_system import SaveManager
from src.core.audio_manager import AudioManager
from src.core.asset_manager import AssetManager
from src.scenes.base_scene import BaseScene
from src.scenes.main_menu_scene import MainMenuScene
from src.scenes.settings_scene import SettingsScene
from src.scenes.gameplay_scene import GameplayScene


class GameEngine:
    """Núcleo da aplicação responsável pela janela, loop principal e transição de cenas."""

    def __init__(self):
        pygame.init()
        self.save_manager = SaveManager()
        settings = self.save_manager.settings

        self.audio_manager = AudioManager(
            master_vol=settings.get("master_volume", 0.8),
            music_vol=settings.get("music_volume", 0.7),
            sfx_vol=settings.get("sfx_volume", 0.9)
        )
        self.asset_manager = AssetManager()

        self.screen: Optional[pygame.Surface] = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.current_fps = 0.0

        self.apply_video_settings()

        # Registro de Cenas
        self.scenes: Dict[str, BaseScene] = {
            "main_menu": MainMenuScene(self),
            "settings": SettingsScene(self),
            "gameplay": GameplayScene(self),
        }
        self.current_scene_name = "main_menu"
        self.current_scene: BaseScene = self.scenes[self.current_scene_name]
        self.current_scene.on_enter()

    def apply_video_settings(self) -> None:
        """Aplica modo de janela/tela cheia e título."""
        pygame.display.set_caption(WINDOW_TITLE)
        settings = self.save_manager.settings
        fullscreen = settings.get("fullscreen", False)
        vsync = 1 if settings.get("vsync", True) else 0

        flags = pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN

        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=vsync)
        except Exception:
            # Fallback sem vsync caso não suportado pela GPU
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    def change_scene(self, scene_name: str) -> None:
        """Transiciona para uma nova cena."""
        if scene_name in self.scenes:
            if self.current_scene:
                self.current_scene.on_exit()
            self.current_scene_name = scene_name
            self.current_scene = self.scenes[scene_name]
            self.current_scene.on_enter()

    def handle_events(self) -> None:
        """Processa eventos globais e da cena ativa."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                return

            if self.current_scene:
                self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        """Atualiza a lógica da cena ativa."""
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self) -> None:
        """Renderiza a cena ativa e informações de debug (como FPS se ativado)."""
        if not self.screen:
            return

        if self.current_scene:
            self.current_scene.draw(self.screen)

        # Exibição opcional de FPS
        if self.save_manager.settings.get("show_fps", True):
            fps_text = f"FPS: {int(self.current_fps)}"
            self.asset_manager.render_text(
                self.screen,
                fps_text,
                (SCREEN_WIDTH - 15, 15),
                size=16,
                color=(150, 150, 150),
                align="topright",
                shadow=True
            )

        pygame.display.flip()

    def run(self) -> None:
        """Inicia o loop principal do jogo."""
        self.running = True
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            # Previne delta time excessivo se a janela for movida/congelada
            dt = min(0.1, dt)
            self.current_fps = self.clock.get_fps()

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit(0)

    def quit(self) -> None:
        """Encerra a execução de forma limpa."""
        self.save_manager.save_all() if hasattr(self.save_manager, "save_all") else None
        self.running = False
