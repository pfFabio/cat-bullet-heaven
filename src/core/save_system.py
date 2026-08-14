"""
Sistema de persistência local de configurações e progresso do jogador em formato JSON.
"""
import json
import logging
from typing import Any, Dict
from src.core.constants import (
    SAVES_DIR,
    SETTINGS_FILE,
    PROGRESS_FILE,
    DEFAULT_SETTINGS,
    DEFAULT_PROGRESS,
)

logger = logging.getLogger(__name__)


class SaveManager:
    """Gerencia leitura e escrita segura de arquivos de save e configurações."""

    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self.progress: Dict[str, Any] = {}
        self._ensure_saves_directory()
        self.load_all()

    def _ensure_saves_directory(self) -> None:
        """Cria o diretório de saves caso não exista."""
        SAVES_DIR.mkdir(parents=True, exist_ok=True)

    def _deep_merge(self, default: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Mescla dicionários garantindo que novas chaves padrão estejam presentes."""
        merged = default.copy()
        for key, value in current.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def load_settings(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo settings.json com fallback para valores padrão."""
        if not SETTINGS_FILE.exists():
            self.settings = DEFAULT_SETTINGS.copy()
            self.save_settings()
            return self.settings

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.settings = self._deep_merge(DEFAULT_SETTINGS, data)
        except Exception as e:
            logger.error(f"Erro ao carregar {SETTINGS_FILE}: {e}. Usando configurações padrão.")
            self.settings = DEFAULT_SETTINGS.copy()
            self.save_settings()

        return self.settings

    def save_settings(self) -> bool:
        """Salva as configurações atuais no disco."""
        try:
            self._ensure_saves_directory()
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar {SETTINGS_FILE}: {e}")
            return False

    def load_progress(self) -> Dict[str, Any]:
        """Carrega progresso do jogador do arquivo progress.json com fallback para padrão."""
        if not PROGRESS_FILE.exists():
            self.progress = DEFAULT_PROGRESS.copy()
            self.save_progress()
            return self.progress

        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.progress = self._deep_merge(DEFAULT_PROGRESS, data)
                # Garante chaves de skins mesmo para saves antigos
                if "unlocked_skins" not in self.progress or not isinstance(self.progress["unlocked_skins"], list):
                    self.progress["unlocked_skins"] = ["blue_0"]
                elif "blue_0" not in self.progress["unlocked_skins"]:
                    self.progress["unlocked_skins"].insert(0, "blue_0")

                if "selected_skin" not in self.progress or not self.progress["selected_skin"]:
                    self.progress["selected_skin"] = "blue_0"
        except Exception as e:
            logger.error(f"Erro ao carregar {PROGRESS_FILE}: {e}. Usando progresso padrão.")
            self.progress = DEFAULT_PROGRESS.copy()
            self.save_progress()

        return self.progress

    def save_progress(self) -> bool:
        """Salva o progresso do jogador no disco."""
        try:
            self._ensure_saves_directory()
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar {PROGRESS_FILE}: {e}")
            return False

    def load_all(self) -> None:
        """Carrega todos os arquivos."""
        self.load_settings()
        self.load_progress()

    def save_all(self) -> None:
        """Salva todos os dados no disco."""
        self.save_settings()
        self.save_progress()

    def update_setting(self, key: str, value: Any) -> None:
        """Atualiza uma configuração específica e persiste."""
        self.settings[key] = value
        self.save_settings()

    def add_gold(self, amount: int) -> int:
        """Adiciona ouro ao progresso do jogador e salva."""
        self.progress["total_gold"] = self.progress.get("total_gold", 0) + max(0, amount)
        self.save_progress()
        return self.progress["total_gold"]

    def spend_gold(self, amount: int) -> bool:
        """Debita ouro do jogador caso possua saldo suficiente."""
        if amount < 0:
            return False
        current_gold = self.progress.get("total_gold", 0)
        if current_gold >= amount:
            self.progress["total_gold"] = current_gold - amount
            self.save_progress()
            return True
        return False

    def get_unlocked_skins(self) -> list:
        """Retorna a lista de IDs de skins desbloqueadas."""
        unlocked = self.progress.get("unlocked_skins", ["blue_0"])
        if not isinstance(unlocked, list):
            unlocked = ["blue_0"]
        if "blue_0" not in unlocked:
            unlocked.append("blue_0")
        return unlocked

    def is_skin_unlocked(self, skin_id: str) -> bool:
        """Verifica se uma skin específica está desbloqueada."""
        if skin_id == "blue_0":
            return True
        return skin_id in self.get_unlocked_skins()

    def get_selected_skin(self) -> str:
        """Retorna o ID da skin felina atualmente equipada."""
        skin = self.progress.get("selected_skin", "blue_0")
        if not self.is_skin_unlocked(skin):
            skin = "blue_0"
            self.set_selected_skin("blue_0")
        return skin

    def set_selected_skin(self, skin_id: str) -> bool:
        """Define e salva a skin atualmente ativa pelo jogador."""
        if self.is_skin_unlocked(skin_id):
            self.progress["selected_skin"] = skin_id
            self.save_progress()
            return True
        return False

    def unlock_skin(self, skin_id: str, cost: int) -> bool:
        """Desbloqueia uma nova skin debitando o ouro e equipando-a."""
        if self.is_skin_unlocked(skin_id):
            return True

        if self.spend_gold(cost):
            unlocked = self.get_unlocked_skins()
            if skin_id not in unlocked:
                unlocked.append(skin_id)
            self.progress["unlocked_skins"] = unlocked
            self.progress["selected_skin"] = skin_id
            self.save_progress()
            return True
        return False

    def record_run_stats(self, score: int, kills: int, time_survived: float, gold_earned: int) -> None:
        """Registra as estatísticas de uma partida finalizada."""
        self.progress["games_played"] = self.progress.get("games_played", 0) + 1
        self.progress["total_kills"] = self.progress.get("total_kills", 0) + kills
        self.progress["total_gold"] = self.progress.get("total_gold", 0) + gold_earned

        if score > self.progress.get("high_score", 0):
            self.progress["high_score"] = score

        if time_survived > self.progress.get("time_survived_record_sec", 0):
            self.progress["time_survived_record_sec"] = time_survived

        self.save_progress()

    def reset_settings(self) -> None:
        """Restaura as configurações para os valores de fábrica."""
        self.settings = DEFAULT_SETTINGS.copy()
        self.save_settings()

    def reset_progress(self) -> None:
        """Restaura o progresso para os valores iniciais (zerar save)."""
        self.progress = DEFAULT_PROGRESS.copy()
        self.save_progress()

