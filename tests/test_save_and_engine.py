"""
Testes automatizados para validação do SaveManager, AudioManager e ciclo de vida das Cenas.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ajusta path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Executa Pygame em modo headless para testes
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.core.save_system import SaveManager
from src.core.audio_manager import AudioManager
from src.core.asset_manager import AssetManager
from src.core.constants import DEFAULT_SETTINGS, DEFAULT_PROGRESS


class TestBulletHeavenCore(unittest.TestCase):

    def setUp(self):
        pygame.init()
        # Mock do display para testes de superfícies
        pygame.display.set_mode((1280, 720))

    def test_save_manager_persistence(self):
        """Testa gravação e leitura de settings e progresso no save local."""
        sm = SaveManager()
        self.assertIsNotNone(sm.settings)
        self.assertIsNotNone(sm.progress)

        # Modifica configuração
        sm.update_setting("master_volume", 0.42)
        sm.load_settings()
        self.assertEqual(sm.settings.get("master_volume"), 0.42)

        # Modifica ouro e estatísticas
        sm.add_gold(150)
        sm.record_run_stats(score=2500, kills=80, time_survived=120.5, gold_earned=50)

        sm.load_progress()
        self.assertGreaterEqual(sm.progress.get("total_gold", 0), 150)
        self.assertGreaterEqual(sm.progress.get("high_score", 0), 2500)
        self.assertGreaterEqual(sm.progress.get("total_kills", 0), 80)

    def test_audio_manager_synth(self):
        """Valida que o gerador procedural de áudio inicializou os sons sintéticos essenciais."""
        am = AudioManager()
        self.assertIn("ui_hover", am.sounds)
        self.assertIn("ui_click", am.sounds)
        self.assertIn("ui_select", am.sounds)
        self.assertIn("shoot", am.sounds)
        self.assertIn("hit", am.sounds)
        self.assertIn("gem", am.sounds)
        self.assertIn("levelup", am.sounds)

    def test_asset_manager_cube_draw(self):
        """Valida renderização do cubo estilizado."""
        asset_mgr = AssetManager()
        surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        rect = pygame.Rect(20, 20, 40, 40)
        # Não deve lançar exceção
        asset_mgr.draw_styled_cube(surf, rect, (0, 200, 255), glow=True)
        # Verifica se renderizou pixels no centro do rect
        color_at_pixel = surf.get_at((40, 40))
        self.assertGreater(color_at_pixel.a, 0)

    def tearDown(self):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
