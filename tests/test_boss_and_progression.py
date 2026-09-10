"""
Testes automatizados para o sistema de Chefes de Fase,
Progressão Dinâmica (Tempo + Nível), Separação Física e Baús Lendários.
"""
import os
import sys
import unittest
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.core.engine import GameEngine
from src.scenes.gameplay_scene import Enemy, BossEnemy, DropItem, BossProjectile, Projectile


class TestBossAndProgression(unittest.TestCase):

    def setUp(self):
        self.engine = GameEngine()
        self.engine.change_scene("gameplay")
        self.scene = self.engine.current_scene

    def test_progression_scaling_formula(self):
        """Valida que o escalonamento cresce com o tempo e com o nível do personagem."""
        self.scene.time_survived = 0.0
        self.scene.player_level = 1
        scale_start = self.scene.get_progression_scaling()
        self.assertAlmostEqual(scale_start, 1.0, places=2)

        # 2 minutos de jogo + nível 5
        self.scene.time_survived = 120.0
        self.scene.player_level = 5
        scale_mid = self.scene.get_progression_scaling()
        # 1.0 + (120/120)*0.85 + (5-1)*0.08 = 1.0 + 0.85 + 0.32 = 2.17
        self.assertGreater(scale_mid, 2.0)

        # 5 minutos de jogo + nível 15
        self.scene.time_survived = 300.0
        self.scene.player_level = 15
        scale_high = self.scene.get_progression_scaling()
        self.assertGreater(scale_high, scale_mid)

    def test_enemy_scaling_attributes(self):
        """Valida que inimigos gerados com scaling possuem mais HP, dano e XP."""
        enemy_normal = Enemy(100, 100, enemy_type="basic", scaling=1.0)
        enemy_buffed = Enemy(100, 100, enemy_type="basic", scaling=2.0)

        self.assertGreater(enemy_buffed.max_hp, enemy_normal.max_hp)
        self.assertGreater(enemy_buffed.damage, enemy_normal.damage)
        self.assertGreater(enemy_buffed.xp_value, enemy_normal.xp_value)

    def test_boss_spawning_at_time_milestone(self):
        """Valida que o Minotauro Furioso surge ao atingir 120s de partida."""
        self.scene.time_survived = 121.0
        self.scene._check_boss_milestones()

        self.assertIn("boss_minotaur", self.scene.boss_milestones_triggered)
        self.assertIsNotNone(self.scene.active_boss)
        self.assertEqual(self.scene.active_boss.boss_type, "boss_minotaur")
        self.assertTrue(self.scene.active_boss.is_boss)
        self.assertGreater(self.scene.boss_warning_timer, 0.0)

    def test_boss_spawning_at_level_milestone(self):
        """Valida que o Minotauro Furioso surge se o jogador atingir Nível 10 mesmo antes dos 2m."""
        self.scene.time_survived = 30.0
        self.scene.player_level = 10
        self.scene._check_boss_milestones()

        self.assertIn("boss_minotaur", self.scene.boss_milestones_triggered)
        self.assertIsNotNone(self.scene.active_boss)

    def test_cyclop_boss_spawning_and_attacks(self):
        """Valida que o Ciclope Colossal surge aos 300s e dispara projéteis radiais."""
        self.scene.time_survived = 305.0
        self.scene._check_boss_milestones()

        self.assertIn("boss_cyclop", self.scene.boss_milestones_triggered)
        cyclop = [e for e in self.scene.enemies if isinstance(e, BossEnemy) and e.boss_type == "boss_cyclop"][0]

        # Força o timer de ataque do Ciclope
        cyclop.attack_timer = 5.0
        self.scene.update(0.016)

        # O Ciclope deve ter disparado projéteis de chefe
        self.assertGreater(len(self.scene.boss_projectiles), 0)

    def test_no_new_monsters_spawn_while_boss_is_alive(self):
        """Valida que nenhum outro monstro comum é gerado enquanto o chefe de fase estiver vivo."""
        boss = BossEnemy(200, 200, boss_type="boss_minotaur", scaling=1.0)
        self.scene.enemies = [boss]
        self.scene.active_boss = boss

        # Tenta disparar múltiplos spawns de onda
        for _ in range(20):
            self.scene.spawn_timer = 5.0
            self.scene._spawn_wave(0.016)

        # A lista de inimigos deve conter estritamente apenas o chefe (tamanho 1)
        self.assertEqual(len(self.scene.enemies), 1)
        self.assertEqual(self.scene.enemies[0], boss)

    def test_minotaur_charge_and_stomp_mechanics(self):
        """Valida mecânica de investida e pisotão sísmico do Minotauro sem invocar monstros."""
        boss = BossEnemy(200, 200, boss_type="boss_minotaur", scaling=1.5)
        self.scene.enemies = [boss]
        self.scene.active_boss = boss

        # Força pisotão sísmico
        boss.summon_timer = boss.summon_cooldown + 1.0
        initial_count = len(self.scene.enemies)
        self.scene.update(0.016)

        # Não deve invocar monstros extras
        self.assertEqual(len(self.scene.enemies), initial_count)

    def test_boss_defeat_drops_chest(self):
        """Valida que derrotar um chefe gera um Baú Lendário de Ouro/XP."""
        boss = BossEnemy(300, 300, boss_type="boss_minotaur", scaling=1.0)
        self.scene.enemies.append(boss)
        self.scene.active_boss = boss

        # Aplica dano letal
        boss.hp = 0
        self.scene.update(0.016)

        # Chefe deve ter sido removido dos inimigos vivos
        self.assertNotIn(boss, self.scene.enemies)
        self.assertIsNone(self.scene.active_boss)

        # Deve existir um DropItem do tipo 'chest'
        chests = [d for d in self.scene.drops if d.item_type == "chest"]
        self.assertEqual(len(chests), 1)
        self.assertGreaterEqual(chests[0].value, 150)

    def test_slime_mother_splits_on_death(self):
        """Valida que a Slime Mãe se divide em 2 mini-slimes ao morrer."""
        mother = Enemy(400, 400, enemy_type="slime_mother", scaling=1.0)
        self.scene.enemies.append(mother)

        mother.hp = 0
        self.scene.update(0.016)

        # Deve conter mini-slimes gerados
        baby_slimes = [e for e in self.scene.enemies if e.enemy_type == "slime"]
        self.assertEqual(len(baby_slimes), 2)

    def test_enemy_soft_separation_prevents_stacking(self):
        """Valida que inimigos sobrepostos sofrem repulsão física suave."""
        e1 = Enemy(200.0, 200.0, enemy_type="basic")
        e2 = Enemy(200.5, 200.5, enemy_type="basic")
        self.scene.enemies = [e1, e2]

        initial_dist = math.hypot(e1.x - e2.x, e1.y - e2.y)
        self.scene._apply_enemy_separation()
        final_dist = math.hypot(e1.x - e2.x, e1.y - e2.y)

        self.assertGreater(final_dist, initial_dist)

    def test_chest_collection_rewards(self):
        """Valida que coletar um Baú Lendário concede ouro e abre o modal de Level Up."""
        initial_gold = self.scene.gold_earned
        chest = DropItem(self.scene.player_x, self.scene.player_y, item_type="chest", value=150)
        self.scene.drops.append(chest)

        self.scene.update(0.016)

        self.assertEqual(self.scene.gold_earned, initial_gold + 150)
        self.assertTrue(self.scene.is_leveling_up)
        self.assertNotIn(chest, self.scene.drops)


if __name__ == "__main__":
    unittest.main()
