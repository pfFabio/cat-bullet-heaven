"""
Ponto de entrada principal do Bullet Heaven.
"""
import os
import sys

# Garante que o diretório raiz esteja no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import GameEngine


def main():
    """Função principal de inicialização do jogo."""
    try:
        engine = GameEngine()
        engine.run()
    except KeyboardInterrupt:
        print("\nJogo encerrado pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    main()
