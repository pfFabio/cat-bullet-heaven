"""
Testes de validação dos sprites e mecânicas dos Cães (Dog Mega Pack) e Feras Caninas (Wolf e Warg).
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
from src.scenes.gameplay_scene import Enemy, GameplayScene


class TestDogSpritesAndEnemies(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.asset_mgr = AssetManager()

    def test_dog_mega_pack_breeds_loaded(self):
        """Valida que todas as raças de cães do Dog Mega Pack são fatiadas e carregadas corretamente."""
        dog_types = [
            "fast", "dog_husky", "dog_greyhound",
            "tank", "dog_rottweiler", "dog_mastiff",
            "slime_mother", "dog_golden", "dog_retriever",
            "slime", "dog_pup", "dog_hound", "dog_shepherd"
        ]
        for dt in dog_types:
            frames = self.asset_mgr.get_enemy_frames(enemy_type=dt, scale=(48, 48))
            self.assertGreater(len(frames), 0, f"Falha ao carregar frames do cão para {dt}")
            self.assertEqual(frames[0].get_size(), (48, 48))

    def test_minifantasy_wolf_and_warg_preserved(self):
        """Valida que o Lobo (wolf/basic) e o Warg antigos do Minifantasy foram preservados."""
        canine_beasts = ["basic", "wolf", "warg", "beast_warg"]
        for beast in canine_beasts:
            frames = self.asset_mgr.get_enemy_frames(enemy_type=beast, scale=(40, 40))
            self.assertGreater(len(frames), 0, f"Falha ao carregar fera canina {beast}")
            self.assertEqual(frames[0].get_size(), (40, 40))

    def test_dog_items_loaded(self):
        """Valida que os itens caninos (osso, coleira, tigela, bola) são carregados do DogItems.png."""
        items = ["bone", "big_bone", "bed", "collar", "ball", "bowl"]
        for item in items:
            surf = self.asset_mgr.get_dog_item(item, scale=(24, 24))
            self.assertIsNotNone(surf, f"Item {item} não encontrado no DogItems.png")
            self.assertEqual(surf.get_size(), (24, 24))

    def test_enemy_initialization_with_new_dog_types(self):
        """Valida atributos e escalas dos novos tipos de inimigos em Enemy."""
        e_husky = Enemy(100, 100, enemy_type="fast")
        self.assertEqual(e_husky.sprite_scale, (48, 48))
        self.assertGreater(e_husky.speed, 150)

        e_rottweiler = Enemy(100, 100, enemy_type="tank")
        self.assertEqual(e_rottweiler.sprite_scale, (56, 56))
        self.assertGreater(e_rottweiler.max_hp, 150)

        e_warg = Enemy(100, 100, enemy_type="warg")
        self.assertEqual(e_warg.sprite_scale, (60, 60))
        self.assertGreater(e_warg.max_hp, 200)

        e_golden = Enemy(100, 100, enemy_type="slime_mother")
        self.assertEqual(e_golden.sprite_scale, (52, 52))

        e_pup = Enemy(100, 100, enemy_type="slime")
        self.assertEqual(e_pup.sprite_scale, (34, 34))

        e_wolf = Enemy(100, 100, enemy_type="basic")
        self.assertEqual(e_wolf.sprite_scale, (54, 54))

    def test_gameplay_wave_spawns_dog_horde(self):
        """Valida que o gameplay gera a horda canina ao longo do tempo."""
        engine = GameEngine()
        engine.change_scene("gameplay")
        scene: GameplayScene = engine.current_scene

        # Configura marcos de chefe como já acionados para testar a horda mista livremente
        scene.boss_milestones_triggered.add("boss_minotaur")
        scene.boss_milestones_triggered.add("boss_cyclop")
        scene.active_boss = None
        scene.time_survived = 150.0
        scene.player_level = 12
        for _ in range(50):
            scene.spawn_timer = 2.0
            scene._spawn_wave(0.016)

        enemy_types_present = {e.enemy_type for e in scene.enemies}
        # Deve conter ao menos 2 tipos caninos distintos gerados na horda
        self.assertGreater(len(enemy_types_present), 1)

    def tearDown(self):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
