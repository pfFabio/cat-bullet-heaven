"""
Testes automatizados para o sistema de skins, catálogo de gatinhos e cena CatShopScene.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.core.save_system import SaveManager
from src.core.skin_catalog import (
    CAT_SKINS,
    get_skin,
    get_all_skins,
    get_skins_by_category,
)
from src.core.engine import GameEngine


class TestCatShopSystem(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1280, 720))
        self.save_mgr = SaveManager()

    def test_skin_catalog_integrity(self):
        """Valida que todas as 50 skins estão cadastradas com propriedades válidas."""
        skins = get_all_skins()
        self.assertEqual(len(skins), 50, "Deve haver exatamente 50 skins cadastradas no catálogo.")

        # Valida que o gatinho inicial blue_0 é gratuito
        default_skin = get_skin("blue_0")
        self.assertEqual(default_skin.cost, 0)
        self.assertEqual(default_skin.id, "blue_0")

        # Valida categorização
        basic_skins = get_skins_by_category("basic")
        self.assertGreater(len(basic_skins), 0)

        special_skins = get_skins_by_category("special")
        self.assertGreater(len(special_skins), 0)

        mythic_skins = get_skins_by_category("mythic")
        self.assertGreater(len(mythic_skins), 0)

    def test_save_manager_skin_unlock_and_selection(self):
        """Testa compra de skin, débito de ouro, e troca de skin ativa."""
        # Garante estado com ouro suficiente
        self.save_mgr.progress["total_gold"] = 1000
        self.save_mgr.progress["unlocked_skins"] = ["blue_0"]
        self.save_mgr.progress["selected_skin"] = "blue_0"
        self.save_mgr.save_progress()

        # Compra skin calico_0 (custo 320)
        calico = get_skin("calico_0")
        success = self.save_mgr.unlock_skin(calico.id, calico.cost)
        self.assertTrue(success, "Deve permitir desbloquear skin quando houver ouro suficiente.")
        self.assertEqual(self.save_mgr.progress["total_gold"], 1000 - 320)
        self.assertIn("calico_0", self.save_mgr.get_unlocked_skins())
        self.assertEqual(self.save_mgr.get_selected_skin(), "calico_0")

        # Tenta comprar skin sem saldo suficiente
        gold_cat = get_skin("gold_0")  # custo 1200
        fail_success = self.save_mgr.unlock_skin(gold_cat.id, gold_cat.cost)
        self.assertFalse(fail_success, "Não deve permitir desbloquear quando faltar ouro.")
        self.assertNotIn("gold_0", self.save_mgr.get_unlocked_skins())

        # Seleciona gatinho inicial novamente
        self.save_mgr.set_selected_skin("blue_0")
        self.assertEqual(self.save_mgr.get_selected_skin(), "blue_0")

    def test_cat_shop_scene_navigation_and_pagination(self):
        """Valida inicialização, paginação, filtros e eventos na CatShopScene."""
        engine = GameEngine()
        engine.change_scene("cat_shop")
        self.assertEqual(engine.current_scene_name, "cat_shop")

        scene = engine.current_scene
        self.assertEqual(scene.current_page, 0)
        self.assertGreater(len(scene.cards), 0)

        # Testa paginação para a frente
        scene._next_page()
        self.assertEqual(scene.current_page, 1)

        # Testa paginação para trás
        scene._prev_page()
        self.assertEqual(scene.current_page, 0)

        # Testa troca de abas
        scene._set_category("mythic")
        self.assertEqual(scene.current_category, "mythic")
        self.assertEqual(scene.current_page, 0)
        self.assertGreater(len(scene.cards), 0)

        # Roda ciclo de update e draw
        for _ in range(10):
            engine.update(0.016)
            engine.draw()

        # Testa tecla ESC para retornar ao menu
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        scene.handle_event(esc_event)
        self.assertEqual(engine.current_scene_name, "main_menu")

    def test_gameplay_uses_selected_skin(self):
        """Valida que a GameplayScene carrega e utiliza a skin selecionada no save."""
        engine = GameEngine()
        engine.save_manager.progress["unlocked_skins"] = ["blue_0", "black_0", "gold_0"]
        engine.save_manager.set_selected_skin("black_0")

        engine.change_scene("gameplay")
        self.assertEqual(engine.current_scene.cat_name, "black_0")

        # Altera para gold_0 e entra na gameplay novamente
        engine.save_manager.set_selected_skin("gold_0")
        engine.change_scene("gameplay")
        self.assertEqual(engine.current_scene.cat_name, "gold_0")

    def test_quit_to_menu_saves_accumulated_gold(self):
        """Valida que o ouro coletado durante a run é persistido ao sair pelo menu de pausa."""
        engine = GameEngine()
        initial_gold = engine.save_manager.progress.get("total_gold", 0)

        engine.change_scene("gameplay")
        scene = engine.current_scene
        scene.gold_earned = 75
        scene.kills = 12
        scene.score = 350
        scene.time_survived = 25.0

        # Simula saída pelo menu de pausa
        scene._quit_to_menu()
        self.assertEqual(engine.current_scene_name, "main_menu")
        self.assertEqual(engine.save_manager.progress.get("total_gold", 0), initial_gold + 75)

    def test_all_category_filters(self):
        """Valida que todos os filtros de categoria geram cards válidos sem erro."""
        engine = GameEngine()
        engine.change_scene("cat_shop")
        scene = engine.current_scene

        categories = ["all", "basic", "colorful", "special", "mythic", "unlocked"]
        for cat in categories:
            scene._set_category(cat)
            self.assertEqual(scene.current_category, cat)
            self.assertEqual(scene.current_page, 0)
            self.assertGreater(len(scene.cards), 0, f"Categoria {cat} deve ter gatinhos.")

    def test_main_menu_cats_button_transition(self):
        """Testa transição do Menu Principal para o Santuário dos Gatos via botão."""
        engine = GameEngine()
        self.assertEqual(engine.current_scene_name, "main_menu")

        menu = engine.current_scene
        menu._on_cats_clicked()
        self.assertEqual(engine.current_scene_name, "cat_shop")

    def test_action_key_shortcut(self):
        """Testa atalho de teclado RETURN/SPACE para selecionar/desbloquear gatinho."""
        engine = GameEngine()
        engine.save_manager.progress["total_gold"] = 1500
        engine.save_manager.progress["unlocked_skins"] = ["blue_0"]
        engine.save_manager.set_selected_skin("blue_0")

        engine.change_scene("cat_shop")
        scene = engine.current_scene

        # Seleciona skin black_0 e pressiona ENTER
        scene.selected_skin_id = "black_0"
        return_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        scene.handle_event(return_event)

        # black_0 deve ter sido desbloqueado e equipado
        self.assertTrue(engine.save_manager.is_skin_unlocked("black_0"))
        self.assertEqual(engine.save_manager.get_selected_skin(), "black_0")

    def tearDown(self):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
