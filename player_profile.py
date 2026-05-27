import json
import os
import pygame

PROFILE_FILE = "profile_data.json"
DEFAULT_PROFILE = {
    "player_name": "Player",
    "high_score": 0,
    "food_consumed": 0,
    "games_played": 0,
    "deaths": 0,
    "settings": {
        "turn_sensitivity": 0.08,
        "acceleration_rate": 0.08
    },
    "customization": {
        "skin_index": 0,
        "arena_index": 0
    }
}


def load_player_profile_data():
    """
    Load persistent profile data from disk, falling back to defaults if file doesn't exist.
    Merges saved data with default values to ensure all keys are present.
    
    Returns:
        Dictionary containing complete player profile data with all required keys
    """
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            merged = DEFAULT_PROFILE.copy()
            merged.update(data)
            merged["settings"] = {**DEFAULT_PROFILE["settings"], **data.get("settings", {})}
            merged["customization"] = {**DEFAULT_PROFILE["customization"], **data.get("customization", {})}
            return merged
        except (json.JSONDecodeError, IOError):
            return DEFAULT_PROFILE.copy()
    return DEFAULT_PROFILE.copy()


def save_profile_data(profile_data):
    """
    Write the current profile data back to disk as JSON.
    Silently fails if there are file system errors.
    
    Args:
        profile_data: Dictionary containing player profile information to save
    """
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as handle:
            json.dump(profile_data, handle, indent=2)
    except IOError:
        pass


def show_profile(screen, clock, font, big_font, profile_data):
    """
    Display the profile screen with saved stats and player information.
    Shows high score, food consumed, games played, deaths, and K/D ratio.
    Returns to menu when ESC is pressed or back button is clicked.
    Supports resizable window.
    
    Args:
        screen: The pygame display surface (may be resizable)
        clock: The pygame clock for frame rate control
        font: The pygame font object for regular text
        big_font: The pygame font object for title text
        profile_data: Dictionary containing player profile information
        
    Returns:
        The next game state ("menu" to return, "quit" to exit)
    """
    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Back button positioned relative to screen size
        back_rect = pygame.Rect(40, screen_height - 80, 120, 40)
        
        # Event loop for the profile screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        screen.fill((20, 24, 45))
        title = big_font.render("Profile", True, (240, 240, 240))
        screen.blit(title, title.get_rect(center=(screen_width // 2, 80)))

        stats = [
            f"Player: {profile_data.get('player_name', 'Player')}",
            f"High Score: {profile_data.get('high_score', 0)}",
            f"Food Collected: {profile_data.get('food_consumed', 0)}",
            f"Games Played: {profile_data.get('games_played', 0)}",
            f"Deaths: {profile_data.get('deaths', 0)}",
        ]
        deaths = profile_data.get("deaths", 0)
        food = profile_data.get("food_consumed", 0)
        kd = food / deaths if deaths > 0 else float(food)
        stats.append(f"K/D Ratio: {kd:.2f}")

        y = 170
        for line in stats:
            label = font.render(line, True, (220, 220, 220))
            screen.blit(label, (120, y))
            y += 48

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=8)
        back_label = font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)
