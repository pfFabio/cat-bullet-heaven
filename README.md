# 🐱 Purr Survivors: Cats vs Dogs (Bullet Heaven 2D)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame-CE](https://img.shields.io/badge/Pygame--CE-2.5%2B-orange.svg)](https://pyga.me/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

Protótipo de jogo estilo **Bullet Heaven / Roguelite de Sobrevivência** desenvolvido em **Python 3** com **Pygame-CE (Community Edition)**. Apresenta arquitetura modular de cenas orientada a objetos, spritesheets animados em 8 direções, sistema de combate com mira e disparo automáticos, ondas dinâmicas de inimigos, seleção de melhorias por cartas (*Level Up*), persistência local em JSON e suporte a execução containerizada com **Docker**.

---

## ✨ Funcionalidades Principais

- **🐾 Protagonista Felino Animado**:
  - Animação completa 8-direcional (correr, sentar, olhar em volta e repouso) com sombras suaves dinâmicas.
  - Sistema de fallback automático para cubos geométricos neon em caso de ausência de assets.
- **🐺 Inimigos com IA e Comportamentos Distintos**:
  - **Lobo (Básico)**: Perseguição equilibrada e resistente.
  - **Morcego (Rápido)**: Deslocamento ágil que força manobras de esquiva.
  - **Troll (Tanque)**: Alta vitalidade e grande impacto, atuando como mini-boss.
- **⚔️ Combate e Progressão**:
  - Disparo automático com busca por proximidade no raio de visão.
  - Sistema de XP e moedas de ouro dropadas ao derrotar inimigos, com atração magnética.
  - Modal de **Level Up** que pausa a partida e sorteia 3 entre 4 cartas de melhoria (*Max HP, Dano, Cadência de Disparo, Velocidade de Movimento*).
  - Feedback visual e sonoro com números de dano flutuantes (*Damage Numbers*) e efeitos procedurais.
- **🎵 Áudio Procedural PCM**:
  - Sintetizador procedural em memória via ondas senoidais para efeitos sonoros (tiro, dano, coleta de gemas, level up e cliques de menu), sem dependência obrigatória de arquivos de áudio externos.
  - Controle de canais e sliders independentes de volume (*Master*, *BGM*, *SFX*).
- **⚙️ Menu e Configurações Completas**:
  - Menu principal com partículas de poeira cósmica flutuantes e botões interativos.
  - Tela de Configurações em abas (*Áudio*, *Vídeo*, *Controles*), com suporte a Fullscreen, V-Sync, Screen Shake e Contador de FPS.
  - Modal de **Estatísticas da Carreira** (recorde de tempo, score máximo, ouro acumulado e total de abates).
  - Persistência imediata e segura em JSON (`saves/settings.json` e `saves/progress.json`).

---

## 🕹️ Controles do Jogo

| Entrada | Ação |
| :--- | :--- |
| **`W`, `A`, `S`, `D` ou `Setas`** | Movimentar o personagem nas 8 direções |
| **Mira / Ataque** | **Automático** (trava no inimigo mais próximo) |
| **`ESC`** | Pausar a partida / Retornar |
| **Teclas `1`, `2`, `3`** | Seleção rápida de cartas de *Level Up* |
| **Mouse (Clique Esquerdo)** | Interação com menus, botões e seleção de upgrades |

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10 ou superior instalado.

### Opção 1: Execução Local com Python (Recomendado)

1. Clone o repositório e acesse a pasta:
   ```bash
   git clone https://github.com/pfFabio/cat-bullet-heaven.git
   cd cat-bullet-heaven
   ```

2. Crie e ative um ambiente virtual (opcional, porém recomendado):
   ```bash
   python -m venv .venv
   # No Windows:
   .venv\Scripts\activate
   # No Linux/macOS:
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o jogo:
   ```bash
   python src/main.py
   ```

---

### Opção 2: Execução com Docker & Docker Compose

O projeto conta com `Dockerfile` e `docker-compose.yml` pré-configurados com suporte a SDL2/X11 e persistência da pasta `saves/`.

#### No Linux / WSL2 (com WSLg ou X11):
```bash
xhost +local:docker
docker compose up --build
```

#### No Windows (com Docker Desktop + VcXsrv ou WSLg):
```bash
docker compose up --build
```

---

## 📂 Estrutura do Projeto

```
bullet-heaven/
├── Dockerfile                  # Imagem container com suporte a SDL2/X11
├── docker-compose.yml          # Orquestração do container e montagem de volumes
├── requirements.txt            # Dependência principal: pygame-ce
├── .gitignore                  # Filtro de arquivos para versionamento
├── README.md                   # Documentação e guia do projeto
├── BG.jpg                      # Imagem de fundo do cenário de batalha
├── Cats Download/              # Spritesheets animados dos protagonistas felinos
├── Minifantasy_Creatures_.../  # Spritesheets das criaturas e inimigos
├── saves/                      # Diretório de persistência local
│   ├── settings.json           # Configurações de áudio e vídeo
│   └── progress.json           # Estatísticas de carreira e ouro do jogador
├── tests/                      # Bateria de testes unitários e de integração
│   ├── test_save_and_engine.py
│   └── test_scenes_integration.py
└── src/
    ├── main.py                 # Ponto de entrada da aplicação
    ├── core/
    │   ├── constants.py        # Constantes de resolução, cores e balanceamento
    │   ├── engine.py           # GameEngine (Loop a 60 FPS e gerenciador de cenas)
    │   ├── save_system.py      # Gerenciador de save/load JSON com deep merge
    │   ├── audio_manager.py    # Mixer de áudio e sintetizador procedural PCM
    │   └── asset_manager.py    # Gerenciador de fontes, spritesheets e sombras
    ├── ui/
    │   ├── components.py       # Botões, Sliders, Toggles, Painéis e Cartas de Upgrade
    │   └── particle.py         # Sistema de partículas de ambiente flutuantes
    └── scenes/
        ├── base_scene.py       # Interface base abstrata para cenas
        ├── main_menu_scene.py  # Menu Principal animado e modal de estatísticas
        ├── settings_scene.py   # Tela de Configurações dividida em abas
        └── gameplay_scene.py   # Loop principal do jogo de sobrevivência
```

---

## 🧪 Executando os Testes Automatizados

Para executar a suíte completa de testes unitários e de integração:

```bash
python -m unittest discover tests
```

---

## 👤 Autor

- **Fábio Figueiredo** - *Matrícula:* 202413741
