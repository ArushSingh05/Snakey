import pygame

from settings import show_settings

SCREEN_WIDTH = 801
SCREEN_HEIGHT = 600
BUTTON_COLOR = (36, 48, 88)
BUTTON_HOVER = (68, 98, 170)
BUTTON_TEXT = (245, 245, 245)
BACKGROUND_COLOR = (12, 18, 42)


def draw_button(screen, font, rect, label, hover=False):
    """Draw a rounded rectangular button with centered text."""
    pygame.draw.rect(screen, BUTTON_HOVER if hover else BUTTON_COLOR, rect, border_radius=12)
    text_surface = font.render(label, True, BUTTON_TEXT)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def run_main_menu(screen, clock, font, title_font, profile_data):
    """Display the main menu and return the selected next state."""
    buttons = [
        {"label": "Play", "action": "play"},
        {"label": "Profile", "action": "profile"},
        {"label": "Customisation", "action": "customization"},
        {"label": "Settings", "action": "settings"},
    ]
    button_rects = []
    button_width = 280
    button_height = 58
    start_y = 210

    for index, button in enumerate(buttons):
        rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + index * (button_height + 18),
            button_width,
            button_height,
        )
        button_rects.append((rect, button["action"], button["label"]))

    # Main menu event loop: wait for quit or button clicks.
    while True:
        mouse_pos = pygame.mouse.get_pos()
        action = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, action_key, _ in button_rects:
                    if rect.collidepoint(event.pos):
                        return action_key

        screen.fill(BACKGROUND_COLOR)
        title_surface = title_font.render("Slim Snakey", True, (240, 240, 240))
        subtitle_surface = font.render("A local multiplayer snake game", True, (200, 200, 220))
        screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        for rect, action_key, label in button_rects:
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, font, rect, label, hover=hover)

        stats_text = f"High score: {profile_data.get('high_score', 0)}  |  Food: {profile_data.get('food_consumed', 0)}"
        stats_surface = font.render(stats_text, True, (190, 190, 220))
        screen.blit(stats_surface, stats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))

        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Slim Snakey")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 32)
    title_font = pygame.font.SysFont(None, 72)


    # The main game loop: keep switching between screens until quit.
    while state != "quit":
        if state == "menu":
            pass
        elif state == "play":
            pass
        elif state == "profile":
            pass
        elif state == "customization":
            pass
        elif state == "settings":
            pass
        else:
            state = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()