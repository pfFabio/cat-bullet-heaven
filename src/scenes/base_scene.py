"""
Classe base abstrata para todas as cenas do jogo (Menu, Configurações, Gameplay).
"""
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.engine import GameEngine


class BaseScene:
    """Interface padrão para gerenciar ciclo de vida e eventos de cada cena."""

    def __init__(self, engine: "GameEngine"):
        self.engine = engine

    def on_enter(self) -> None:
        """Chamado quando a cena se torna ativa."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos do Pygame."""
        pass

    def update(self, dt: float) -> None:
        """Atualiza a lógica da cena a cada frame."""
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza a cena na superfície alvo."""
        pass

    def on_exit(self) -> None:
        """Chamado quando a cena deixa de ser ativa."""
        pass
