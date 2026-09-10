"""
Testes automatizados para os poderes especiais dos gatinhos:
- Gatinho inicial sem poderes
- Ataque duplo (Twin Shot)
- Teleporte sombra (Blink)
- Roubo de vida (Lifesteal de 5%)
- Tiro gigante perfurante (Mega Beam)
"""
import os
import sys
import unittest
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.core.skin_catalog import get_skin, get_all_skins, POWER_DEFINITIONS
from src.core.engine import GameEngine
from src.scenes.gameplay_scene import Enemy, Projectile, MegaBeamProjectile


class TestCatPowers(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    def test_starter_cat_has_no_powers(self):
        """Valida que o gatinho inicial blue_0 não possui poder especial."""
        starter = get_skin("blue_0")
        self.assertEqual(starter.power_id, "none")
        self.assertEqual(starter.power_name, "Sem Poder Especial")

    def test_all_other_cats_have_assigned_powers(self):
        """Valida que todas as outras 49 skins possuem um dos poderes especiais definidos."""
        valid_powers = {"double_attack", "teleport", "lifesteal", "mega_beam", "ghost", "brawler", "radioactive_aura"}
        all_skins = get_all_skins()

        power_counts = {p: 0 for p in valid_powers}
        power_counts["none"] = 0

        for skin in all_skins:
            if skin.id == "blue_0":
                self.assertEqual(skin.power_id, "none")
                power_counts["none"] += 1
            else:
                self.assertIn(skin.power_id, valid_powers, f"Skin {skin.id} deve possuir um poder especial válido.")
                power_counts[skin.power_id] += 1

        self.assertEqual(power_counts["none"], 1)
        self.assertGreaterEqual(power_counts["ghost"], 1)
        self.assertGreaterEqual(power_counts["brawler"], 3)
        self.assertGreaterEqual(power_counts["radioactive_aura"], 1)

    def test_double_attack_power_mechanic(self):
        """Valida que gatinhos com Ataque Duplo geram 2 projéteis por disparo automático."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "orange_0"]
        engine.save_manager.set_selected_skin("orange_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "double_attack")

        # Spawna 1 inimigo próximo
        scene.enemies.append(Enemy(scene.player_x + 100, scene.player_y, enemy_type="basic"))

        # Força timer de ataque
        scene.attack_timer = scene.attack_cooldown + 0.1
        scene._auto_attack(0.016)

        self.assertEqual(len(scene.projectiles), 2, "Ataque duplo deve disparar exatamente 2 projéteis.")

    def test_teleport_power_execution_and_cooldown(self):
        """Valida teleporte na direção que o gato está olhando, com cooldown e invulnerabilidade."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "black_0"]
        engine.save_manager.set_selected_skin("black_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "teleport")

        initial_x = scene.player_x
        initial_y = scene.player_y
        scene.player_facing_dir = "right"

        # Simula pressionar tecla ESPAÇO
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        scene.handle_event(event)

        # Deve ter se movido ~150px para a direita
        self.assertAlmostEqual(scene.player_x, initial_x + 150.0, delta=2.0)
        self.assertEqual(scene.player_y, initial_y)
        self.assertGreater(scene.invulnerable_timer, 0.0)
        self.assertAlmostEqual(scene.ability_cooldown_timer, 2.5, delta=0.1)

        # Tentativa imediata de teleporte não deve funcionar devido ao cooldown
        next_x = scene.player_x
        scene.handle_event(event)
        self.assertEqual(scene.player_x, next_x)

    def test_lifesteal_power_heals_player(self):
        """Valida que o Roubo de Vida cura 5% do dano causado (mínimo 1 HP)."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "calico_0"]
        engine.save_manager.set_selected_skin("calico_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "lifesteal")

        # Reduz HP do jogador para permitir cura
        scene.player_hp = 50
        scene.player_max_hp = 100

        # Cria inimigo e projétil colidindo
        enemy = Enemy(scene.player_x, scene.player_y + 100, enemy_type="basic")
        scene.enemies.append(enemy)

        proj = Projectile(enemy.x, enemy.y, enemy.x, enemy.y, damage=40)
        scene.projectiles.append(proj)

        # Roda um ciclo de update para colisão
        scene.update(0.016)

        # 5% de 40 de dano = 2 de cura
        expected_heal = max(1, math.ceil(40 * 0.05))
        self.assertEqual(scene.player_hp, 50 + expected_heal)

    def test_mega_beam_power_pierces_multiple_enemies(self):
        """Valida disparo de Tiro Perfurante Gigante que atravessa múltiplos inimigos."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "gold_0"]
        engine.save_manager.set_selected_skin("gold_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "mega_beam")

        scene.player_facing_dir = "right"
        scene.player_x = 100
        scene.player_y = 300

        # Cria 3 inimigos alinhados horizontalmente
        e1 = Enemy(200, 300, enemy_type="basic")
        e2 = Enemy(350, 300, enemy_type="basic")
        e3 = Enemy(500, 300, enemy_type="basic")
        scene.enemies = [e1, e2, e3]

        # Simula disparo do Mega Beam com tecla SHIFT
        shift_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LSHIFT)
        scene.handle_event(shift_event)

        self.assertEqual(len(scene.mega_beams), 1)
        self.assertAlmostEqual(scene.ability_cooldown_timer, 4.0, delta=0.1)

        beam = scene.mega_beams[0]
        initial_hp_e1 = e1.hp
        initial_hp_e2 = e2.hp
        initial_hp_e3 = e3.hp

        # Atualiza múltiplos frames para o raio atravessar todos os inimigos
        for _ in range(40):
            scene.update(0.016)

        # Todos os 3 inimigos devem ter sofrido dano e o feixe continuou existindo
        self.assertLess(e1.hp, initial_hp_e1)
        self.assertLess(e2.hp, initial_hp_e2)
        self.assertLess(e3.hp, initial_hp_e3)

    def test_ghost_cat_power_mechanics(self):
        """Valida mecânicas do Gato Fantasma: não atira, recebe 30% de dano e causa dano melee por PV perdido."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "ghost_0"]
        engine.save_manager.set_selected_skin("ghost_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "ghost")

        # 1. Valida que NÃO atira projéteis
        enemy = Enemy(scene.player_x + 50, scene.player_y, enemy_type="basic")
        scene.enemies = [enemy]
        scene.attack_timer = scene.attack_cooldown + 1.0
        scene._auto_attack(0.016)
        self.assertEqual(len(scene.projectiles), 0, "Gato fantasma não deve disparar nenhum projétil.")

        # 2. Valida que recebe apenas 30% de dano do inimigo (dano básico = 14 -> sofre 5)
        enemy.x = scene.player_x
        enemy.y = scene.player_y
        initial_hp = scene.player_hp
        scene.invulnerable_timer = 0.0

        scene.update(0.016)
        damage_taken = initial_hp - scene.player_hp
        self.assertEqual(damage_taken, max(1, math.ceil(enemy.damage * 0.30)))

        # 3. Valida que causa dano corpo-a-corpo escalado com PV perdido no inimigo
        enemy2 = Enemy(scene.player_x, scene.player_y, enemy_type="tank")
        scene.enemies = [enemy2]
        scene.player_hp = 30  # Perdeu 70 de HP
        scene.player_max_hp = 100

        initial_enemy_hp = enemy2.hp
        scene.update(0.016)

        # Dano esperado: max(15, int(player_damage + lost_hp * 2.0)) = 25 + 70 * 2 = 165
        expected_melee_dmg = int(scene.player_damage + (100 - 30) * 2.0)
        self.assertEqual(enemy2.hp, initial_enemy_hp - expected_melee_dmg)

    def test_brawler_cat_power_mechanics(self):
        """Valida mecânicas do Colosso Brawler: dobro de HP, metade do dano de tiro e dobro de dano corpo-a-corpo."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "dark_0"]
        engine.save_manager.set_selected_skin("dark_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "brawler")

        # 1. Dobro de HP (200)
        self.assertEqual(scene.player_max_hp, 200)
        self.assertEqual(scene.player_hp, 200)

        # 2. Metade do dano com tiros (25 / 2 = 12.5)
        enemy = Enemy(scene.player_x + 100, scene.player_y, enemy_type="basic")
        scene.enemies = [enemy]
        scene.attack_timer = scene.attack_cooldown + 0.1
        scene._auto_attack(0.016)

        self.assertEqual(len(scene.projectiles), 1)
        self.assertEqual(scene.projectiles[0].damage, scene.player_damage * 0.5)

        # 3. Dobro de dano corpo-a-corpo (25 * 2 = 50)
        scene.projectiles.clear()
        enemy_contact = Enemy(scene.player_x, scene.player_y, enemy_type="tank")
        scene.enemies = [enemy_contact]
        initial_tank_hp = enemy_contact.hp

        scene.update(0.016)
        self.assertEqual(enemy_contact.hp, initial_tank_hp - (scene.player_damage * 2.0))

    def test_radioactive_cat_aura_mechanic(self):
        """Valida que o Gato Radioativo não atira projéteis e causa dano contínuo em área apenas aos inimigos no raio de alcance."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "radioactive_0"]
        engine.save_manager.set_selected_skin("radioactive_0")

        engine.change_scene("gameplay")
        scene = engine.current_scene
        self.assertEqual(scene.cat_power, "radioactive_aura")

        # 1. Não deve disparar projéteis em _auto_attack
        enemy_near = Enemy(scene.player_x + 60, scene.player_y, enemy_type="basic")
        enemy_far = Enemy(scene.player_x + 350, scene.player_y, enemy_type="basic")
        scene.enemies = [enemy_near, enemy_far]

        scene.attack_timer = scene.attack_cooldown + 0.1
        scene._auto_attack(0.016)
        self.assertEqual(len(scene.projectiles), 0, "Gato radioativo não deve disparar projéteis.")

        # 2. Ao passar tempo de tick (>= 0.15s), deve causar dano de aura no inimigo próximo
        initial_hp_near = enemy_near.hp
        initial_hp_far = enemy_far.hp

        # Simula 0.20s de atualização
        scene.update(0.20)

        # Inimigo próximo deve ter sofrido dano de radiação
        self.assertLess(enemy_near.hp, initial_hp_near)
        # Inimigo distante (fora do raio de 150px) deve permanecer ileso
        self.assertEqual(enemy_far.hp, initial_hp_far)

    def tearDown(self):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
