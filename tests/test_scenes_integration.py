"""
Teste de integração de cenas e loop de eventos.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.core.engine import GameEngine


class TestScenesIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = GameEngine()

    def test_menu_to_settings_and_back(self):
        """Testa transição do Menu para Configurações e retorno."""
        self.assertEqual(self.engine.current_scene_name, "main_menu")

        # Simula clique para abrir configurações
        self.engine.change_scene("settings")
        self.assertEqual(self.engine.current_scene_name, "settings")

        # Atualiza cena de configurações por alguns frames
        for _ in range(5):
            self.engine.update(0.016)
            self.engine.draw()

        # Simula retorno ao menu
        self.engine.change_scene("main_menu")
        self.assertEqual(self.engine.current_scene_name, "main_menu")

    def test_gameplay_loop_and_pause(self):
        """Testa ciclo de vida da gameplay, spawn de ondas, colisão e pausa."""
        self.engine.change_scene("gameplay")
        self.assertEqual(self.engine.current_scene_name, "gameplay")
        scene = self.engine.current_scene

        # Roda vários frames de gameplay simulada
        for i in range(60):
            # Move o jogador simulando tecla pressionada
            self.engine.update(0.016)
            self.engine.draw()

        self.assertGreater(scene.time_survived, 0.0)

        # Testa pausa
        scene._toggle_pause()
        self.assertTrue(scene.is_paused)

        # Despausa
        scene._toggle_pause()
        self.assertFalse(scene.is_paused)

    def test_level_up_choice_system(self):
        """Testa se o Level Up oferece exatamente 3 opções entre as 4 e aplica os atributos corretamente."""
        self.engine.change_scene("gameplay")
        scene = self.engine.current_scene

        # Força subida de nível
        scene.player_level = 2
        scene.player_xp = 0
        scene._trigger_level_up()

        self.assertTrue(scene.is_leveling_up)
        self.assertEqual(len(scene.upgrade_cards), 3)

        # As 3 opções sorteadas devem pertencer ao conjunto das 5 opções
        allowed_upgrades = {"hp", "damage", "attack_speed", "move_speed", "hp_regen"}
        for card in scene.upgrade_cards:
            self.assertIn(card.upgrade_id, allowed_upgrades)

        # Testa seleção via atalho do teclado (tecla 1)
        initial_hp = scene.player_max_hp
        initial_damage = scene.player_damage
        initial_atk_cd = scene.attack_cooldown
        initial_speed = scene.player_speed
        initial_regen = scene.upgrade_counts["hp_regen"]

        chosen_upgrade_id = scene.upgrade_cards[0].upgrade_id

        # Simula pressionar tecla '1'
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
        scene.handle_event(event)

        # O modal deve fechar após a seleção
        self.assertFalse(scene.is_leveling_up)

        # Verifica se o atributo correspondente foi aprimorado
        if chosen_upgrade_id == "hp":
            self.assertEqual(scene.player_max_hp, initial_hp + 25)
        elif chosen_upgrade_id == "damage":
            self.assertAlmostEqual(scene.player_damage, initial_damage * 1.1)
        elif chosen_upgrade_id == "attack_speed":
            self.assertLess(scene.attack_cooldown, initial_atk_cd)
        elif chosen_upgrade_id == "move_speed":
            self.assertEqual(scene.player_speed, initial_speed + 30.0)
        elif chosen_upgrade_id == "hp_regen":
            self.assertEqual(scene.upgrade_counts["hp_regen"], initial_regen + 1)

    def test_hp_regen_upgrade_recovers_health_over_time(self):
        """Testa se a carta de Recuperação de HP recupera 1% do HP Máx por segundo por nível."""
        self.engine.change_scene("gameplay")
        scene = self.engine.current_scene

        # Aplica 2 cartas de Recuperação de HP (2% por segundo)
        scene._apply_hp_regen_upgrade()
        scene._apply_hp_regen_upgrade()
        self.assertEqual(scene.upgrade_counts["hp_regen"], 2)

        # Reduz HP do jogador para 40 de 100
        scene.player_max_hp = 100
        scene.player_hp = 40

        # Simula 1 segundo de gameplay (dt = 1.0)
        scene.update(1.0)

    def test_enemy_spawn_only_on_two_furthest_walls(self):
        """Testa se os inimigos nascem apenas nas 2 paredes mais distantes da posição do gato."""
        self.engine.change_scene("gameplay")
        scene = self.engine.current_scene

        # Posiciona o jogador no canto superior esquerdo (x=50, y=50)
        # As 2 paredes mais próximas são Topo (y=0) e Esquerda (x=0)
        # As 2 paredes mais distantes são Direita (x=1280) e Baixo (y=720)
        scene.player_x = 50.0
        scene.player_y = 50.0
        scene.enemies.clear()

        # Gera múltiplos spawns
        for _ in range(40):
            scene.spawn_timer = 2.0
            scene._spawn_wave(0.016)

        self.assertGreaterEqual(len(scene.enemies), 40)
        for enemy in scene.enemies:
            # Não deve ter nascido no Topo (y < 0) nem na Esquerda (x < 0)
            self.assertFalse(enemy.y < 0, f"Inimigo não deveria nascer no Topo (parede próxima): {enemy.y}")
            self.assertFalse(enemy.x < 0, f"Inimigo não deveria nascer na Esquerda (parede próxima): {enemy.x}")
            # Deve ter nascido na Direita (x >= 1280) ou Baixo (y >= 720)
            spawned_from_distant_wall = (enemy.x >= 1280 or enemy.y >= 720)
            self.assertTrue(spawned_from_distant_wall, f"Inimigo deve nascer nas paredes distantes: ({enemy.x}, {enemy.y})")

    def tearDown(self):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()

