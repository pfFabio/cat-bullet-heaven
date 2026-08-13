"""
Testes de carregamento, fatiamento e renderização de sprites dos Gatos e Criaturas.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.core.asset_manager import AssetManager
from src.core.engine import GameEngine


class TestSpriteSystem(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.asset_mgr = AssetManager()

    def test_cat_sprite_directions_and_actions(self):
        """Valida que todas as 8 direções e ações do gato azul são carregadas e redimensionadas."""
        directions = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
        actions = ["sit", "look", "lay", "walk", "run", "run_fast", "beg"]

        for d in directions:
            for a in actions:
                frames = self.asset_mgr.get_cat_frames(cat_name="blue_0", action=a, direction=d, scale=(48, 48))
                self.assertGreater(len(frames), 0, f"Falha ao carregar frames para dir={d}, action={a}")
                self.assertEqual(frames[0].get_size(), (48, 48))

    def test_enemy_sprite_types(self):
        """Valida carregamento de frames para os tipos de inimigos (basic, fast, tank)."""
        enemy_types = ["basic", "fast", "tank"]
        for et in enemy_types:
            frames = self.asset_mgr.get_enemy_frames(enemy_type=et, action="walk", scale=(36, 36))
            self.assertGreater(len(frames), 0, f"Falha ao carregar frames de inimigo para {et}")
            self.assertEqual(frames[0].get_size(), (36, 36))

    def test_shadow_drawing(self):
        """Valida desenho de sombras elípticas sob os personagens."""
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.asset_mgr.draw_shadow(surf, 50, 50, radius_x=20, radius_y=10, alpha=80)
        # O pixel central deve ter alpha > 0
        self.assertGreater(surf.get_at((50, 50)).a, 0)

    def test_gameplay_scene_with_cat_and_enemies(self):
        """Valida ciclo de vida completo da GameplayScene usando os novos sprites."""
        engine = GameEngine()
        engine.change_scene("gameplay")
        scene = engine.current_scene

        # Verifica atributos do gato azul
        self.assertEqual(scene.cat_name, "blue_0")
        self.assertEqual(scene.player_facing_dir, "down")

        # Roda múltiplos frames simulados de gameplay
        for _ in range(30):
            engine.update(0.016)
            engine.draw()

        # Garante que o desenho não lançou exceção
        self.assertGreater(scene.time_survived, 0.0)

    def test_background_loading(self):
        """Valida que o plano de fundo BG.jpg é carregado e redimensionado corretamente."""
        bg = self.asset_mgr.get_background((1280, 720))
        self.assertIsNotNone(bg, "BG.jpg deve ser carregado com sucesso.")
        self.assertEqual(bg.get_size(), (1280, 720))

    def tearDown(self):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
