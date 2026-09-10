"""
Constantes globais e configurações de estética visual e dados padrão.
"""
from pathlib import Path

# Configurações de Janela e Performance
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_RESOLUTION = (SCREEN_WIDTH, SCREEN_HEIGHT)
TARGET_FPS = 60
WINDOW_TITLE = "Bullet Heaven - Survivors"

# Diretórios e Arquivos de Persistência
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SAVES_DIR = PROJECT_ROOT / "saves"
SETTINGS_FILE = SAVES_DIR / "settings.json"
PROGRESS_FILE = SAVES_DIR / "progress.json"

# Paleta de Cores - Tema Dark Fantasy / Cubos Neon
COLOR_BG = (15, 13, 24)
COLOR_BG_DARK = (8, 7, 14)
COLOR_BG_CARD = (25, 22, 38)
COLOR_BG_CARD_BORDER = (60, 52, 90)

# Cores de Destaque
COLOR_GOLD = (255, 204, 0)
COLOR_CYAN = (0, 235, 235)
COLOR_PURPLE = (168, 85, 247)
COLOR_RED = (239, 68, 68)
COLOR_GREEN = (34, 197, 94)
COLOR_BLUE = (59, 130, 246)
COLOR_ORANGE = (249, 115, 22)

# Textos
COLOR_TEXT_LIGHT = (248, 250, 252)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_TEXT_DARK = (30, 27, 46)

# Cores de UI (Botões e Controles)
COLOR_BTN_DEFAULT = (38, 33, 58)
COLOR_BTN_HOVER = (62, 54, 94)
COLOR_BTN_ACTIVE = (88, 76, 134)
COLOR_BTN_BORDER = (90, 80, 130)
COLOR_BTN_BORDER_HOVER = (255, 204, 0)

# Cores dos Elementos de Gameplay (Cubos Coloridos)
COLOR_PLAYER_CUBE = (0, 220, 255)       # Cubo Herói Azul Neon
COLOR_PLAYER_GLOW = (0, 140, 255)
COLOR_ENEMY_BASIC = (239, 68, 68)       # Cubo Inimigo Vermelho
COLOR_ENEMY_FAST = (249, 115, 22)       # Cubo Inimigo Laranja
COLOR_ENEMY_TANK = (168, 85, 247)       # Cubo Inimigo Roxo
COLOR_ENEMY_SLIME = (74, 222, 128)      # Cubo Inimigo Slime Verde
COLOR_ENEMY_BOSS = (220, 38, 38)        # Cubo Chefe Carmesim
COLOR_PROJECTILE = (254, 240, 138)      # Projétil Amarelo
COLOR_BOSS_PROJECTILE = (239, 68, 68)   # Projétil Vermelho de Chefe
COLOR_XP_GEM = (56, 189, 248)           # Gema XP Ciano
COLOR_GOLD_COIN = (250, 204, 21)        # Moeda de Ouro
COLOR_CHEST = (251, 191, 36)            # Baú Lendário de Chefe
COLOR_WARNING = (251, 146, 60)          # Alerta de Chefe

# Cores de Raridade de Skins / Colecionáveis
COLOR_RARITY_COMMON = (148, 163, 184)      # Cinza Claro
COLOR_RARITY_UNCOMMON = (34, 197, 94)      # Verde Esmeralda
COLOR_RARITY_RARE = (59, 130, 246)         # Azul Safira
COLOR_RARITY_EPIC = (168, 85, 247)         # Roxo Místico
COLOR_RARITY_LEGENDARY = (255, 204, 0)     # Ouro Lendário

# Configurações Padrão de Settings
DEFAULT_SETTINGS = {
    "master_volume": 0.8,
    "music_volume": 0.7,
    "sfx_volume": 0.9,
    "fullscreen": False,
    "vsync": True,
    "screen_shake": True,
    "show_fps": True,
    "resolution": [1280, 720]
}

# Progresso Padrão do Jogador
DEFAULT_PROGRESS = {
    "total_gold": 0,
    "high_score": 0,
    "games_played": 0,
    "total_kills": 0,
    "time_survived_record_sec": 0,
    "unlocked_heroes": ["cubo_azul"],
    "unlocked_skins": ["blue_0"],
    "selected_skin": "blue_0",
    "upgrades": {
        "max_hp": 0,
        "damage": 0,
        "speed": 0,
        "pickup_range": 0,
        "attack_speed": 0
    }
}

