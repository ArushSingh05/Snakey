"""
Power-ups system
Two types:
  - speed_boost : player moves faster for 5 seconds
  - growth_burst: snake grows +7 tiles immediately, then shrinks back after 5 seconds
"""

import pygame
import random

POWERUP_TYPES = {
    "speed_boost": {
        "name": "Speed Boost",
        "color": (0, 220, 255),
        "duration": 5000,
        "effect": "increase_speed"
    },
    "growth_burst": {
        "name": "Growth Burst",
        "color": (255, 80, 200),
        "duration": 5000,
        "effect": "temporary_growth"
    },
}

GROWTH_BURST_TILES = 7
GROWTH_BURST_PTS = GROWTH_BURST_TILES * 14


class PowerUp:
    def __init__(self, x, y, powerup_type, screen):
        if powerup_type not in POWERUP_TYPES:
            raise ValueError(f"Invalid power-up type: {powerup_type}")
        self.x = max(20, min(x, screen.get_width() - 20))
        self.y = max(20, min(y, screen.get_height() - 20))
        self.powerup_type = powerup_type
        self.radius = 10
        self.spawn_time = pygame.time.get_ticks()
        self.active = True
        self.collected = False

    def draw(self, screen):
        if not self.active or self.collected:
            return
        elapsed = pygame.time.get_ticks() - self.spawn_time
        pulse = abs((elapsed % 500) - 250) / 250
        animated_radius = int(self.radius + pulse * 5)
        color = POWERUP_TYPES[self.powerup_type]["color"]
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), animated_radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), animated_radius, 2)
        try:
            label_font = pygame.font.SysFont(None, 18)
            label = label_font.render(POWERUP_TYPES[self.powerup_type]["name"], True, (255, 255, 255))
            screen.blit(label, (int(self.x) - label.get_width() // 2, int(self.y) - animated_radius - 16))
        except Exception:
            pass

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > 12000


class ActivePowerUp:
    """Tracks an active power-up applied to a snake and reverses it on expiry."""

    def __init__(self, powerup_type, snake):
        if powerup_type not in POWERUP_TYPES:
            raise ValueError(f"Invalid power-up type: {powerup_type}")
        self.powerup_type = powerup_type
        self.duration = POWERUP_TYPES[powerup_type]["duration"]
        self.start_time = pygame.time.get_ticks()
        self.active = True
        self.snake = snake
        self._applied = False
        self._original_max_speed = getattr(snake, 'max_speed', 7.0)
        self._extra_length = 0

        if powerup_type == "speed_boost":
            snake.max_speed = min(snake.max_speed + 3.0, 12.0)
            snake.speed = min(snake.speed + 2.0, snake.max_speed)
            self._applied = True
        elif powerup_type == "growth_burst":
            snake.target_length += GROWTH_BURST_PTS
            self._extra_length = GROWTH_BURST_PTS
            self._applied = True

    def is_active(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

    def expire(self):
        if not self._applied:
            return
        if self.powerup_type == "speed_boost":
            self.snake.max_speed = self._original_max_speed
            self.snake.speed = min(self.snake.speed, self.snake.max_speed)
        elif self.powerup_type == "growth_burst":
            self.snake.target_length = max(40, self.snake.target_length - self._extra_length)
        self._applied = False

    def get_remaining_time(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, self.duration - elapsed) / 1000.0


def spawn_random_powerup(screen):
    powerup_type = random.choice(list(POWERUP_TYPES.keys()))
    x = random.randint(40, screen.get_width() - 40)
    y = random.randint(40, screen.get_height() - 40)
    return PowerUp(x, y, powerup_type, screen)