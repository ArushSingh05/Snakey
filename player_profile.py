import json
import os
import pygame
from input_validation import validate_profile_data
from achievements import get_unlocked_achievements
from fonts import get_font
from customisation import paint_arena
from ui_helpers import draw_transparent_panel

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
TITLE_COLOR = (20, 30, 60)
TEXT_COLOR = (220, 220, 220)
LABEL_COLOR = (160, 170, 200)

def load_player_profile_data():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            data = validate_profile_data(data)
            merged = DEFAULT_PROFILE.copy()
            merged.update(data)
            merged["settings"] = {**DEFAULT_PROFILE["settings"], **data.get("settings", {})}
            merged["customization"] = {**DEFAULT_PROFILE["customization"], **data.get("customization", {})}
            return merged
        except (json.JSONDecodeError, IOError):
            return DEFAULT_PROFILE.copy()
    return DEFAULT_PROFILE.copy()

def save_profile_data(profile_data):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as handle:
            json.dump(profile_data, handle, indent=2)
    except IOError:
        pass

def draw_progress_bar(screen, x, y, width, height, progress, color=(100, 200, 100), bg_color=(40, 40, 60)):
    """Draw a horizontal progress bar with rounded corners."""
    # Background
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=height//2)
    # Fill
    fill_width = max(0, min(int(width * progress), width))
    if fill_width > 0:
        pygame.draw.rect(screen, color, (x, y, fill_width, height), border_radius=height//2)

def show_profile(screen, clock, font, big_font, profile_data):
    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Responsive fonts
        title_font = get_font(max(40, min(72, int(screen_height * 0.12))))
        name_font = get_font(max(28, min(48, int(screen_height * 0.08))))
        stat_font = get_font(max(16, min(26, int(screen_height * 0.045))))
        label_font = get_font(max(14, min(22, int(screen_height * 0.04))))
        button_font = get_font(max(14, min(24, int(screen_height * 0.055))))

        back_button_width = max(100, int(screen_width * 0.15))
        back_button_height = max(35, int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05), screen_height - back_button_height - 20,
                                back_button_width, back_button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                new_width = max(event.size[0], 320)
                new_height = max(event.size[1], 240)
                if new_width != event.size[0] or new_height != event.size[1]:
                    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        paint_arena(screen, profile_data)

        # Title
        title_surf = title_font.render("Profile", True, TITLE_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(screen_width // 2, int(screen_height * 0.09))))

        # Panel – centered, fills most of the screen
        panel_margin = int(screen_width * 0.08)
        panel_width = screen_width - 2 * panel_margin
        panel_top = int(screen_height * 0.17)
        panel_bottom = screen_height - back_button_height - 40
        panel_height = panel_bottom - panel_top
        panel_x = (screen_width - panel_width) // 2
        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        # ---- Content ----
        content_x = panel_x + int(panel_width * 0.06)
        content_width = panel_width - int(panel_width * 0.12)
        y = panel_top + int(panel_height * 0.06)

        # Player name (big)
        player_name = profile_data.get('player_name', 'Player')
        name_surf = name_font.render(player_name, True, (255, 255, 255))
        screen.blit(name_surf, (content_x + (content_width - name_surf.get_width()) // 2, y))
        y += name_surf.get_height() + int(panel_height * 0.04)

        # --- Left column: general stats ---
        left_col_x = content_x
        right_col_x = content_x + content_width // 2 + int(panel_width * 0.02)
        col_width = content_width // 2 - int(panel_width * 0.02)

        # Helper to draw a stat line with label and value
        def draw_stat(label, value, x, y, value_color=TEXT_COLOR):
            label_surf = label_font.render(label + ":", True, LABEL_COLOR)
            value_surf = stat_font.render(str(value), True, value_color)
            screen.blit(label_surf, (x, y))
            screen.blit(value_surf, (x + label_surf.get_width() + 10, y))
            return y + max(label_surf.get_height(), value_surf.get_height()) + int(panel_height * 0.03)

        # Left column stats
        stats_left = [
            ("High Score", profile_data.get('high_score', 0)),
            ("Food Collected", profile_data.get('food_consumed', 0)),
            ("Games Played", profile_data.get('games_played', 0)),
            ("Deaths", profile_data.get('deaths', 0)),
        ]
        for label, val in stats_left:
            y = draw_stat(label, val, left_col_x, y)

        # Right column: combat & progression
        y_right = panel_top + int(panel_height * 0.06) + name_surf.get_height() + int(panel_height * 0.04)
        deaths = profile_data.get('deaths', 1)
        food = profile_data.get('food_consumed', 0)
        kd = food / deaths if deaths > 0 else float(food)

        combat_stats = [
            ("K/D Ratio", f"{kd:.2f}"),
            ("PvP Wins", profile_data.get('pvp_wins', 0)),
            ("Achievements", f"{len(get_unlocked_achievements(profile_data))}/10"),
        ]
        for label, val in combat_stats:
            y_right = draw_stat(label, val, right_col_x, y_right, value_color=(255, 215, 0) if "Achievements" in label else TEXT_COLOR)

        # XP bar
        xp = profile_data.get('xp', 0)
        level = profile_data.get('level', 1)
        xp_needed = level * 500  # simple level system
        progress = min(1.0, xp / xp_needed) if xp_needed > 0 else 0

        bar_label = label_font.render("XP Progress", True, LABEL_COLOR)
        bar_x = right_col_x
        bar_y = y_right + int(panel_height * 0.02)
        screen.blit(bar_label, (bar_x, bar_y))
        bar_y += bar_label.get_height() + 4
        bar_width = col_width - 20
        bar_height = int(panel_height * 0.035)
        draw_progress_bar(screen, bar_x, bar_y, bar_width, bar_height, progress, color=(100, 200, 255))
        # XP text
        xp_text = f"{xp} / {xp_needed} XP (Level {level})"
        xp_surf = label_font.render(xp_text, True, (200, 200, 220))
        screen.blit(xp_surf, (bar_x + (bar_width - xp_surf.get_width()) // 2, bar_y + bar_height + 4))

        # Back button
        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)