"""
Sistema de partículas de ambiente para planos de fundo animados e efeitos de combate.
"""
import random
import pygame
from typing import List, Tuple
from src.core.constants import COLOR_PURPLE, COLOR_CYAN, COLOR_GOLD, COLOR_RED


class Particle:
    """Representa uma partícula individual com posição, velocidade, vida e cor."""

    def __init__(self, x: float, y: float, vx: float, vy: float, size: float, color: Tuple[int, int, int], lifetime: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float) -> bool:
        """Atualiza a posição e idade da partícula. Retorna False se expirou."""
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza a partícula com fade out gradual."""
        progress = max(0.0, min(1.0, self.age / self.lifetime))
        alpha = int(255 * (1.0 - progress) * 0.7)
        if alpha <= 0:
            return

        current_size = max(1, int(self.size * (1.0 - progress * 0.4)))
        part_surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        pygame.draw.rect(
            part_surf,
            (*self.color[:3], alpha),
            (0, 0, current_size * 2, current_size * 2),
            border_radius=2
        )
        surface.blit(part_surf, (int(self.x - current_size), int(self.y - current_size)))


class AmbientParticleSystem:
    """Gera e atualiza partículas flutuantes no fundo de telas e menus."""

    def __init__(self, width: int, height: int, max_particles: int = 50):
        self.width = width
        self.height = height
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.colors = [COLOR_PURPLE, COLOR_CYAN, COLOR_GOLD, (120, 80, 200)]
        self._seed_initial_particles()

    def _seed_initial_particles(self) -> None:
        """Cria partículas distribuídas inicialmente na tela."""
        for _ in range(self.max_particles // 2):
            p = self._create_random_particle(random_y=True)
            p.age = random.uniform(0, p.lifetime * 0.8)
            self.particles.append(p)

    def _create_random_particle(self, random_y: bool = False) -> Particle:
        """Cria uma nova partícula flutuante."""
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height) if random_y else self.height + random.uniform(5, 20)
        vx = random.uniform(-15, 15)
        vy = random.uniform(-40, -15)
        size = random.uniform(2, 5)
        color = random.choice(self.colors)
        lifetime = random.uniform(5.0, 10.0)
        return Particle(x, y, vx, vy, size, color, lifetime)

    def update(self, dt: float) -> None:
        """Atualiza todas as partículas e repõe as expiradas."""
        self.particles = [p for p in self.particles if p.update(dt)]
        while len(self.particles) < self.max_particles:
            self.particles.append(self._create_random_particle(random_y=False))

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha todas as partículas na superfície fornecida."""
        for p in self.particles:
            p.draw(surface)
