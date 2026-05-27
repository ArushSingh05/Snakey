import pygame

DEFAULT_SETTINGS = {
    "turn_sensitivity": 0.08,
    "acceleration_rate": 0.08
}


def ensure_settings(data):
    """
    Ensure profile data has all settings values defined.
    Provides default values for any missing settings keys.
    
    Args:
        data: The profile data dictionary to validate
        
    Returns:
        The settings sub-dictionary with all required keys present
    """
    settings = data.get("settings", {})
    for key, default in DEFAULT_SETTINGS.items():
        settings.setdefault(key, default)
    data["settings"] = settings
    return settings


def show_settings(screen, clock, font, big_font, profile_data):
    """
    Display settings menu where the user can modify game control sensitivity values.
    Allows adjustment of turn sensitivity and acceleration rate using arrow keys.
    Supports resizable window.
    
    Args:
        screen: The pygame display surface (may be resizable)
        clock: The pygame clock for frame rate control
        font: The pygame font object for regular text
        big_font: The pygame font object for title text
        profile_data: Dictionary containing player profile and settings
        
    Returns:
        The next game state ("menu" to return, "quit" to exit)
    """
    settings = ensure_settings(profile_data)
    option_index = 0
    options = ["turn_sensitivity", "acceleration_rate"]
    value_labels = {
        "turn_sensitivity": "Turn sensitivity",
        "acceleration_rate": "Acceleration"
    }

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Event loop for the settings screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_UP:
                    option_index = max(0, option_index - 1)
                if event.key == pygame.K_DOWN:
                    option_index = min(len(options) - 1, option_index + 1)
                if event.key == pygame.K_LEFT:
                    key = options[option_index]
                    settings[key] = max(0.02, settings[key] - 0.01)
                if event.key == pygame.K_RIGHT:
                    key = options[option_index]
                    settings[key] = min(0.18, settings[key] + 0.01)
                if event.key == pygame.K_RETURN:
                    return "menu"

        screen.fill((14, 18, 35))
        title = big_font.render("Settings", True, (235, 235, 235))
        screen.blit(title, title.get_rect(center=(screen_width // 2, 80)))

        for idx, key in enumerate(options):
            label_text = f"{value_labels[key]}: {settings[key]:.2f}"
            color = (255, 255, 255) if idx == option_index else (180, 180, 180)
            label = font.render(label_text, True, color)
            screen.blit(label, (140, 200 + idx * 60))

        help_text = font.render("Use UP/DOWN to select, LEFT/RIGHT to change, ESC to go back", True, (192, 192, 192))
        screen.blit(help_text, (100, screen_height - 80))

        pygame.display.flip()
        clock.tick(60)
