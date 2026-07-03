import pygame

# Helper function to draw a rounded semi-transparent panel
def draw_transparent_panel(screen, x, y, width, height, radius=20, color=(0, 0, 0, 180)):
    """Draw a rounded semi-transparent panel."""
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 0))
    pygame.draw.rect(panel, color, (0, 0, width, height), border_radius=radius)
    screen.blit(panel, (x, y))