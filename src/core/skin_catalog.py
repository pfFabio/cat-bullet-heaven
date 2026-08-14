"""
Catálogo completo de skins de gatinhos disponíveis para desbloqueio com ouro e poderes especiais únicos.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from src.core.constants import (
    COLOR_RARITY_COMMON,
    COLOR_RARITY_UNCOMMON,
    COLOR_RARITY_RARE,
    COLOR_RARITY_EPIC,
    COLOR_RARITY_LEGENDARY,
)


@dataclass
class CatSkin:
    """Representa as propriedades de uma skin de gatinho no catálogo."""
    id: str
    name: str
    rarity: str
    cost: int
    category: str
    description: str
    rarity_color: Tuple[int, int, int]
    power_id: str
    power_name: str
    power_desc: str
    power_icon: str


# Definições centrais dos 4 poderes e do estado inicial
POWER_DEFINITIONS: Dict[str, Dict[str, any]] = {
    "none": {
        "name": "Sem Poder Especial",
        "icon": "⭐",
        "desc": "O herói felino inicial confia puramente em suas garras e agilidade.",
        "type": "passive",
        "color": (148, 163, 184),
        "cooldown": 0.0,
    },
    "double_attack": {
        "name": "Ataque Duplo",
        "icon": "⚔️",
        "desc": "Dispara 2 projéteis simultâneos contra as hordas a cada ataque.",
        "type": "passive",
        "color": (249, 115, 22),
        "cooldown": 0.0,
    },
    "teleport": {
        "name": "Teleporte Sombra",
        "icon": "⚡",
        "desc": "Pressione ESPAÇO ou SHIFT para teleportar na direção do olhar (recarga: 2.5s).",
        "type": "active",
        "color": (168, 85, 247),
        "cooldown": 2.5,
    },
    "lifesteal": {
        "name": "Roubo de Vida",
        "icon": "❤️",
        "desc": "Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        "type": "passive",
        "color": (239, 68, 68),
        "cooldown": 0.0,
    },
    "mega_beam": {
        "name": "Tiro Perfurante Gigante",
        "icon": "☄️",
        "desc": "Pressione ESPAÇO ou SHIFT para disparar um tiro colossal perfurante (recarga: 4.0s).",
        "type": "active",
        "color": (0, 235, 235),
        "cooldown": 4.0,
    },
}


# Catálogo completo com as 50 skins e seus respectivos poderes
CAT_SKINS: Dict[str, CatSkin] = {
    # --- Gatinho Inicial (Sem Poder Especial) ---
    "blue_0": CatSkin(
        id="blue_0",
        name="Gato Azul Clássico",
        rarity="Comum",
        cost=0,
        category="basic",
        description="O herói felino original! Corajoso, leal e veloz.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="none",
        power_name="Sem Poder Especial",
        power_desc="O herói clássico confia puramente em suas garras e reflexos naturais.",
        power_icon="⭐"
    ),

    # --- Básicos com Poderes ---
    "blue_1": CatSkin(
        id="blue_1",
        name="Gato Azul Listrado",
        rarity="Comum",
        cost=80,
        category="basic",
        description="Gatinho azul com listras suaves de tigre do oceano.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "blue_2": CatSkin(
        id="blue_2",
        name="Gato Azul Safira",
        rarity="Incomum",
        cost=120,
        category="basic",
        description="Pelagem azulada com reflexos cristalinos encantados.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "blue_3": CatSkin(
        id="blue_3",
        name="Gato Azul Meia-Noite",
        rarity="Incomum",
        cost=150,
        category="basic",
        description="Tons azuis escuros para caçadas noturnas precisas.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),

    "black_0": CatSkin(
        id="black_0",
        name="Gato Preto da Sorte",
        rarity="Comum",
        cost=100,
        category="basic",
        description="Dizem que dá sorte para quem joga Bullet Heaven!",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "black_1": CatSkin(
        id="black_1",
        name="Gato Preto de Meias",
        rarity="Comum",
        cost=110,
        category="basic",
        description="Pelagem preta fosca com patinhas brancas charmosas.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "black_2": CatSkin(
        id="black_2",
        name="Pantera Doméstica",
        rarity="Incomum",
        cost=130,
        category="basic",
        description="Furtivo como uma pequena pantera das florestas.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "black_3": CatSkin(
        id="black_3",
        name="Gato Sombra de Ébano",
        rarity="Incomum",
        cost=150,
        category="basic",
        description="Move-se suavemente entre os disparos inimigos.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "black_4": CatSkin(
        id="black_4",
        name="Gato Tuxedo Elegante",
        rarity="Incomum",
        cost=160,
        category="basic",
        description="Vestido a rigor para derrotar monstros com classe.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),

    "orange_0": CatSkin(
        id="orange_0",
        name="Gato Laranja Trapalhão",
        rarity="Comum",
        cost=100,
        category="basic",
        description="Dono de um único neurônio dourado e muita bravura.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "orange_1": CatSkin(
        id="orange_1",
        name="Gato Laranja Tigrado",
        rarity="Comum",
        cost=120,
        category="basic",
        description="Listras quentes que lembram chamas acolhedoras.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "orange_2": CatSkin(
        id="orange_2",
        name="Gato Caramelo",
        rarity="Incomum",
        cost=140,
        category="basic",
        description="Doce como caramelo, feroz contra ondas de monstros.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "orange_3": CatSkin(
        id="orange_3",
        name="Gato Pôr do Sol",
        rarity="Incomum",
        cost=160,
        category="basic",
        description="Cores radiantes inspiradas no entardecer dos sobreviventes.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),

    "white_0": CatSkin(
        id="white_0",
        name="Gato Floco de Neve",
        rarity="Comum",
        cost=110,
        category="basic",
        description="Pelagem branca imaculada e olhos penetrantes.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "white_grey_0": CatSkin(
        id="white_grey_0",
        name="Gato Névoa Prateada",
        rarity="Incomum",
        cost=130,
        category="basic",
        description="Mescla perfeita entre branco invernal e cinza suave.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "white_grey_1": CatSkin(
        id="white_grey_1",
        name="Gato Tempestade Suave",
        rarity="Incomum",
        cost=140,
        category="basic",
        description="Cores que lembram nuvens de tempestade passageira.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),

    "grey_0": CatSkin(
        id="grey_0",
        name="Gato Cinzento Aveludado",
        rarity="Comum",
        cost=90,
        category="basic",
        description="Pelagem macia cinzenta, mestre dos cochilos rápidos.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "grey_1": CatSkin(
        id="grey_1",
        name="Gato Cinza Chumbo",
        rarity="Incomum",
        cost=120,
        category="basic",
        description="Tons metálicos que combinam com projéteis velozes.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "grey_2": CatSkin(
        id="grey_2",
        name="Gato Fumaça Mágica",
        rarity="Incomum",
        cost=140,
        category="basic",
        description="Desliza pelo campo de batalha como fumaça etérea.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),

    "brown_0": CatSkin(
        id="brown_0",
        name="Gato Castanho Café",
        rarity="Comum",
        cost=90,
        category="basic",
        description="Energia de uma xícara de café puro logo pela manhã.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "brown_1": CatSkin(
        id="brown_1",
        name="Gato Chocolate ao Leite",
        rarity="Comum",
        cost=100,
        category="basic",
        description="Marrom aveludado e passos silenciosos.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "brown_2": CatSkin(
        id="brown_2",
        name="Gato Canela Picante",
        rarity="Comum",
        cost=110,
        category="basic",
        description="Um toque de canela e determinação em cada salto.",
        rarity_color=COLOR_RARITY_COMMON,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "brown_3": CatSkin(
        id="brown_3",
        name="Gato Terra Fértil",
        rarity="Incomum",
        cost=120,
        category="basic",
        description="Firme como as raízes dos carvalhos ancestrais.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "brown_4": CatSkin(
        id="brown_4",
        name="Gato Avelã Nobre",
        rarity="Incomum",
        cost=130,
        category="basic",
        description="Elegância rústica com olhar compenetrado.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "brown_5": CatSkin(
        id="brown_5",
        name="Gato Mogno Imperial",
        rarity="Incomum",
        cost=140,
        category="basic",
        description="Tons amadeirados ricos de pura realeza felina.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "brown_6": CatSkin(
        id="brown_6",
        name="Gato Espresso Intenso",
        rarity="Incomum",
        cost=150,
        category="basic",
        description="Reações rápidas e foco inabalável nos inimigos.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "brown_7": CatSkin(
        id="brown_7",
        name="Gato Castanha Real",
        rarity="Incomum",
        cost=160,
        category="basic",
        description="Gatinho com porte aristocrático e miado refinado.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "brown_8": CatSkin(
        id="brown_8",
        name="Gato Cacau Puro",
        rarity="Incomum",
        cost=170,
        category="basic",
        description="Tom marrom escuro com energia pura e revigorante.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),

    # --- Coloridos Vibrantes ---
    "red_0": CatSkin(
        id="red_0",
        name="Gato Rubi Ardente",
        rarity="Raro",
        cost=240,
        category="colorful",
        description="Brilha com a chama ardente da vitória.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "red_1": CatSkin(
        id="red_1",
        name="Gato Carmesim Furioso",
        rarity="Raro",
        cost=260,
        category="colorful",
        description="Intensidade escarlate que intimida os monstros.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),
    "pink_0": CatSkin(
        id="pink_0",
        name="Gatinho Rosa Sakura",
        rarity="Raro",
        cost=250,
        category="colorful",
        description="Suavidade e charme das flores de cerejeira em combate.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "yellow_0": CatSkin(
        id="yellow_0",
        name="Gato Raio de Sol",
        rarity="Raro",
        cost=220,
        category="colorful",
        description="Ilumina as arenas mais escuras com seu brilho solar.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "teal_0": CatSkin(
        id="teal_0",
        name="Gato Turquesa Astral",
        rarity="Raro",
        cost=260,
        category="colorful",
        description="Vibrações marinhas de cor turquesa e equilíbrio puro.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "indigo_0": CatSkin(
        id="indigo_0",
        name="Gato Índigo Crepúsculo",
        rarity="Raro",
        cost=280,
        category="colorful",
        description="A união mística entre o azul profundo e o violeta.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "peach_0": CatSkin(
        id="peach_0",
        name="Gato Pêssego Doce",
        rarity="Raro",
        cost=210,
        category="colorful",
        description="Cores pastéis aveludadas para gatinhos carinhosos.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "creme_0": CatSkin(
        id="creme_0",
        name="Gato Creme Chantilly",
        rarity="Incomum",
        cost=150,
        category="colorful",
        description="Maciez e leveza que flutuam pelo mapa.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "creme_1": CatSkin(
        id="creme_1",
        name="Gato Baunilha Suave",
        rarity="Incomum",
        cost=170,
        category="colorful",
        description="Aroma de doçura e precisão nos disparos mágicos.",
        rarity_color=COLOR_RARITY_UNCOMMON,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),

    # --- Especiais & Encantados ---
    "calico_0": CatSkin(
        id="calico_0",
        name="Gato Calico da Prosperidade",
        rarity="Raro",
        cost=320,
        category="special",
        description="O lendário Maneki-Neko tricolor que atrai riquezas!",
        rarity_color=COLOR_RARITY_RARE,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "seal_point_0": CatSkin(
        id="seal_point_0",
        name="Gato Siamês Seal Point",
        rarity="Raro",
        cost=340,
        category="special",
        description="Focinho escuro e olhos azuis penetrantes de pura sabedoria.",
        rarity_color=COLOR_RARITY_RARE,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "cotton_candy_blue_0": CatSkin(
        id="cotton_candy_blue_0",
        name="Gato Algodão Doce Celeste",
        rarity="Épico",
        cost=480,
        category="special",
        description="Nascido nas nuvens de açúcar do reino das guloseimas.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "cotton_candy_pink_0": CatSkin(
        id="cotton_candy_pink_0",
        name="Gato Algodão Doce Rosado",
        rarity="Épico",
        cost=480,
        category="special",
        description="Fofura infinita envolta em pó mágico de fada.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="lifesteal",
        power_name="Roubo de Vida",
        power_desc="Cura 5% do dano causado (mínimo 1 HP) ao atingir qualquer inimigo.",
        power_icon="❤️"
    ),
    "hairless_0": CatSkin(
        id="hairless_0",
        name="Gato Sphynx Místico",
        rarity="Épico",
        cost=420,
        category="special",
        description="Antigo guardião das pirâmides com sentidos aguçados.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "hairless_1": CatSkin(
        id="hairless_1",
        name="Gato Sphynx Sombrio",
        rarity="Épico",
        cost=440,
        category="special",
        description="Gato sem pelos imbuído de runas ancestrais protetoras.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="double_attack",
        power_name="Ataque Duplo",
        power_desc="Dispara 2 projéteis simultâneos em cada rajada automática.",
        power_icon="⚔️"
    ),

    # --- Místicos & Lendários ---
    "dark_0": CatSkin(
        id="dark_0",
        name="Gato do Abismo Negro",
        rarity="Épico",
        cost=550,
        category="mythic",
        description="Forjado na escuridão estelar para absorver todo o perigo.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "game_boy_0": CatSkin(
        id="game_boy_0",
        name="Gato Retrô 8-Bit Clássico",
        rarity="Épico",
        cost=600,
        category="mythic",
        description="Pixel art nostálgico em 4 tons de verde monocromático.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "game_boy_1": CatSkin(
        id="game_boy_1",
        name="Gato Retrô Pocketscreen",
        rarity="Épico",
        cost=620,
        category="mythic",
        description="Estética portátil dos clássicos dos anos 90.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "game_boy_2": CatSkin(
        id="game_boy_2",
        name="Gato Retrô Arcade Neon",
        rarity="Épico",
        cost=650,
        category="mythic",
        description="Lembranças das saudosas máquinas de fliperama.",
        rarity_color=COLOR_RARITY_EPIC,
        power_id="teleport",
        power_name="Teleporte Sombra",
        power_desc="Pressione [ESPAÇO/SHIFT] para saltar pelo espaço na direção que estiver olhando.",
        power_icon="⚡"
    ),
    "ghost_0": CatSkin(
        id="ghost_0",
        name="Gato Fantasma Espectral",
        rarity="Lendário",
        cost=850,
        category="mythic",
        description="Transita entre os mundos, assustando os próprios monstros.",
        rarity_color=COLOR_RARITY_LEGENDARY,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "radioactive_0": CatSkin(
        id="radioactive_0",
        name="Gato Radioativo Gama",
        rarity="Lendário",
        cost=950,
        category="mythic",
        description="Energia nuclear cintilante que brilha na escuridão total.",
        rarity_color=COLOR_RARITY_LEGENDARY,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
    "gold_0": CatSkin(
        id="gold_0",
        name="Gato Dourado Lendário",
        rarity="Lendário",
        cost=1200,
        category="mythic",
        description="A obra-prima felina esculpida em ouro puro de 24 quilates!",
        rarity_color=COLOR_RARITY_LEGENDARY,
        power_id="mega_beam",
        power_name="Tiro Perfurante Gigante",
        power_desc="Ativa [ESPAÇO/SHIFT] um feixe colossal que perfura todos os monstros.",
        power_icon="☄️"
    ),
}

# Categorias amigáveis para interface
CAT_CATEGORIES = [
    ("all", "TODOS"),
    ("basic", "BÁSICOS"),
    ("colorful", "COLORIDOS"),
    ("special", "ESPECIAIS"),
    ("mythic", "MÍSTICOS"),
    ("unlocked", "DESBLOQUEADOS"),
]


def get_skin(skin_id: str) -> CatSkin:
    """Retorna os metadados da skin especificada ou fallback para a skin inicial."""
    return CAT_SKINS.get(skin_id, CAT_SKINS["blue_0"])


def get_all_skins() -> List[CatSkin]:
    """Retorna a lista completa de skins ordenadas por custo."""
    return sorted(list(CAT_SKINS.values()), key=lambda s: (s.cost, s.name))


def get_skins_by_category(category: str, unlocked_ids: Optional[List[str]] = None) -> List[CatSkin]:
    """Filtra as skins de acordo com a categoria selecionada."""
    all_skins = get_all_skins()
    if category == "all":
        return all_skins
    if category == "unlocked":
        unlocked_set = set(unlocked_ids or ["blue_0"])
        return [s for s in all_skins if s.id in unlocked_set]
    return [s for s in all_skins if s.category == category]
