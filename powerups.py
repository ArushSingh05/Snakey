"""
Power-ups system for time-limited in-game effects.
Implements invincibility, double growth, and speed boost mechanics.
"""

import pygame
import random

# Power-up types with duration and effects
POWERUP_TYPES = {
    "invincibility": {
        "name": "Invincibility",
        "color": (255, 215, 0),
        "duration": 5000,  # milliseconds
        "effect": "immune_to_damage"
    },
    "double_growth": {
        "name": "Double Growth",
        "color": (255, 105, 180),
        "duration": 8000,
        "effect": "double_growth_rate"
    },
    "speed_boost": {
        "name": "Speed Boost",
        "color": (0, 255, 255),
        "duration": 6000,
        "effect": "increase_speed"
    }
}


class PowerUp:
    """
    Represents a time-limited power-up in the game.
    Tracks type, position, and active status.
    """
    
    def __init__(self, x, y, powerup_type, screen):
        """
        Initialize a power-up at given position.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            powerup_type (str): Type of power-up (invincibility, double_growth, speed_boost)
            screen: Pygame display surface
        """
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
        """
        Draw power-up as colored circle with animation.
        
        Args:
            screen: Pygame display surface
        """
        if not self.active or self.collected:
            return
        
        # Pulsing effect based on time
        elapsed = pygame.time.get_ticks() - self.spawn_time
        pulse = abs((elapsed % 500) - 250) / 250
        animated_radius = int(self.radius + pulse * 5)
        
        color = POWERUP_TYPES[self.powerup_type]["color"]
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), animated_radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), animated_radius, 2)
    
    def is_expired(self):
        """
        Check if power-up has been on screen too long without being collected.
        
        Returns:
            bool: True if expired
        """
        # Power-ups expire after 15 seconds if not collected
        return pygame.time.get_ticks() - self.spawn_time > 15000


class ActivePowerUp:
    """
    Tracks an active power-up effect on a snake.
    """
    
    def __init__(self, powerup_type, snake):
        """
        Apply power-up effect to snake.
        
        Args:
            powerup_type (str): Type of power-up
            snake: Snake object to apply effect to
        """
        if powerup_type not in POWERUP_TYPES:
            raise ValueError(f"Invalid power-up type: {powerup_type}")
        
        self.powerup_type = powerup_type
        self.duration = POWERUP_TYPES[powerup_type]["duration"]
        self.start_time = pygame.time.get_ticks()
        self.active = True
    
    def is_active(self):
        """
        Check if power-up effect is still active.
        
        Returns:
            bool: True if still active
        """
        elapsed = pygame.time.get_ticks() - self.start_time
        return elapsed < self.duration
    
    def get_remaining_time(self):
        """
        Get remaining time for power-up effect.
        
        Returns:
            float: Remaining time in seconds
        """
        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, self.duration - elapsed)
        return remaining / 1000.0  # Convert to seconds


def spawn_random_powerup(screen):
    """
    Create a random power-up at random screen location.
    
    Args:
        screen: Pygame display surface
        
    Returns:
        PowerUp: New power-up instance
    """
    powerup_type = random.choice(list(POWERUP_TYPES.keys()))
    x = random.randint(30, screen.get_width() - 30)
    y = random.randint(30, screen.get_height() - 30)
    return PowerUp(x, y, powerup_type, screen)
