import json
import os
import pygame
from input_validation import validate_profile_data, validate_nickname
from achievements import get_unlocked_achievements
from fonts import get_font
from customisation import paint_arena
from ui_helpers import draw_transparent_panel

# Player profile
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


def get_kd_ratio(profile_data):
    kills = max(0, int(profile_data.get("kills", 0)))
    deaths = max(0, int(profile_data.get("deaths", 0)))
    if deaths <= 0:
        return float(kills) if kills > 0 else 0.0
    return kills / deaths


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
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=height // 2)
    fill_width = max(0, min(int(width * progress), width))
    if fill_width > 0:
        pygame.draw.rect(screen, color, (x, y, fill_width, height), border_radius=height // 2)


def show_profile(screen, clock, font, big_font, profile_data):
    edit_mode = None
    pending_name = profile_data.get("player_name", "Player")
    error_message = ""

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        title_font = get_font(max(40, min(72, int(screen_height * 0.12))))
        name_font = get_font(max(28, min(48, int(screen_height * 0.08))))
        stat_font = get_font(max(16, min(26, int(screen_height * 0.045))))
        label_font = get_font(max(14, min(22, int(screen_height * 0.04))))
        button_font = get_font(max(14, min(24, int(screen_height * 0.055))))

        back_button_width = max(100, int(screen_width * 0.15))
        back_button_height = max(35, int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05), screen_height - back_button_height - 20,
                                back_button_width, back_button_height)

        player_name = profile_data.get("player_name", "Player")
        name_surf = name_font.render(player_name, True, (255, 255, 255))
        name_x = 0
        change_name_rect = pygame.Rect(0, 0, 0, 0)
        save_rect = pygame.Rect(0, 0, 0, 0)
        cancel_rect = pygame.Rect(0, 0, 0, 0)
        confirm_rect = pygame.Rect(0, 0, 0, 0)
        retry_rect = pygame.Rect(0, 0, 0, 0)

        panel_margin = int(screen_width * 0.08)
        panel_width = screen_width - 2 * panel_margin
        panel_top = int(screen_height * 0.17)
        panel_bottom = screen_height - back_button_height - 40
        panel_height = panel_bottom - panel_top
        panel_x = (screen_width - panel_width) // 2
        content_x = panel_x + int(panel_width * 0.06)
        content_width = panel_width - int(panel_width * 0.12)
        y = panel_top + int(panel_height * 0.06)
        name_x = content_x + (content_width - name_surf.get_width()) // 2
        change_name_width = max(90, int(screen_width * 0.13))
        change_name_height = max(34, int(screen_height * 0.06))
        change_name_rect = pygame.Rect(name_x + name_surf.get_width() + 12, y + 4, change_name_width, change_name_height)

        if edit_mode == "editing":
            box_width = max(320, int(screen_width * 0.5))
            box_height = max(170, int(screen_height * 0.3))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            button_row_y = box_y + box_height - 58
            button_width = 90
            button_height = 34
            button_gap = 16
            button_row_x = box_x + (box_width - (2 * button_width + button_gap)) // 2
            save_rect = pygame.Rect(button_row_x, button_row_y, button_width, button_height)
            cancel_rect = pygame.Rect(button_row_x + button_width + button_gap, button_row_y, button_width, button_height)
        elif edit_mode == "confirm":
            box_width = max(320, int(screen_width * 0.5))
            box_height = max(170, int(screen_height * 0.3))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            button_row_y = box_y + box_height - 58
            button_width = 110
            button_height = 34
            button_gap = 16
            button_row_x = box_x + (box_width - (2 * button_width + button_gap)) // 2
            confirm_rect = pygame.Rect(button_row_x, button_row_y, button_width, button_height)
            cancel_rect = pygame.Rect(button_row_x + button_width + button_gap, button_row_y, button_width, button_height)
        elif edit_mode == "error":
            box_width = max(340, int(screen_width * 0.55))
            box_height = max(190, int(screen_height * 0.32))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            button_row_y = box_y + box_height - 58
            button_width = 90
            button_height = 34
            button_gap = 16
            button_row_x = box_x + (box_width - (2 * button_width + button_gap)) // 2
            retry_rect = pygame.Rect(button_row_x, button_row_y, button_width, button_height)
            cancel_rect = pygame.Rect(button_row_x + button_width + button_gap, button_row_y, button_width, button_height)

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
                    if edit_mode in {"editing", "confirm", "error"}:
                        edit_mode = None
                        pending_name = profile_data.get("player_name", "Player")
                        error_message = ""
                    else:
                        return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"
                if change_name_rect.collidepoint(event.pos):
                    edit_mode = "editing"
                    pending_name = profile_data.get("player_name", "Player")
                    error_message = ""

            if edit_mode == "editing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        pending_name = pending_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        is_valid, message = validate_nickname(pending_name)
                        if is_valid:
                            edit_mode = "confirm"
                            error_message = ""
                        else:
                            edit_mode = "error"
                            error_message = message
                    elif event.unicode and event.unicode.isalnum():
                        pending_name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if save_rect.collidepoint(event.pos):
                        is_valid, message = validate_nickname(pending_name)
                        if is_valid:
                            edit_mode = "confirm"
                            error_message = ""
                        else:
                            edit_mode = "error"
                            error_message = message
                    elif cancel_rect.collidepoint(event.pos):
                        edit_mode = None
                        pending_name = profile_data.get("player_name", "Player")
            elif edit_mode == "confirm":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if confirm_rect.collidepoint(event.pos):
                        profile_data["player_name"] = pending_name
                        edit_mode = None
                    elif cancel_rect.collidepoint(event.pos):
                        edit_mode = None
                        pending_name = profile_data.get("player_name", "Player")
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    profile_data["player_name"] = pending_name
                    edit_mode = None
            elif edit_mode == "error":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if retry_rect.collidepoint(event.pos):
                        edit_mode = "editing"
                    elif cancel_rect.collidepoint(event.pos):
                        edit_mode = None
                        pending_name = profile_data.get("player_name", "Player")
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    edit_mode = "editing"
        paint_arena(screen, profile_data)

        title_surf = title_font.render("Profile", True, TITLE_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(screen_width // 2, int(screen_height * 0.09))))

        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        screen.blit(name_surf, (name_x, y))

        change_name_hover = change_name_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (68, 98, 170) if change_name_hover else (36, 48, 88), change_name_rect, border_radius=16)
        change_name_label = button_font.render("Edit", True, (245, 245, 245))
        screen.blit(change_name_label, change_name_label.get_rect(center=change_name_rect.center))
        y += name_surf.get_height() + int(panel_height * 0.04)

        left_col_x = content_x
        right_col_x = content_x + content_width // 2 + int(panel_width * 0.02)
        col_width = content_width // 2 - int(panel_width * 0.02)

        def draw_stat(label, value, x, y, value_color=TEXT_COLOR):
            label_surf = label_font.render(label + ":", True, LABEL_COLOR)
            value_surf = stat_font.render(str(value), True, value_color)
            screen.blit(label_surf, (x, y))
            screen.blit(value_surf, (x + label_surf.get_width() + 10, y))
            return y + max(label_surf.get_height(), value_surf.get_height()) + int(panel_height * 0.03)

        stats_left = [
            ("High Score", profile_data.get("high_score", 0)),
            ("Food Collected", profile_data.get("food_consumed", 0)),
            ("Games Played", profile_data.get("games_played", 0)),
            ("Deaths", profile_data.get("deaths", 0)),
        ]
        for label, val in stats_left:
            y = draw_stat(label, val, left_col_x, y)

        y_right = panel_top + int(panel_height * 0.06) + name_surf.get_height() + int(panel_height * 0.04)
        deaths = profile_data.get("deaths", 0)
        kills = profile_data.get("kills", 0)
        kd = get_kd_ratio(profile_data)
        kd_text = f"{kd:.2f}"

        combat_stats = [
            ("K/D Ratio", kd_text),
            ("PvP Wins", profile_data.get("pvp_wins", 0)),
            ("Achievements", f"{len(get_unlocked_achievements(profile_data))}/10"),
        ]
        for label, val in combat_stats:
            y_right = draw_stat(label, val, right_col_x, y_right, value_color=(255, 215, 0) if "Achievements" in label else TEXT_COLOR)

        xp = profile_data.get("xp", 0)
        level = profile_data.get("level", 1)
        xp_needed = level * 500
        progress = min(1.0, xp / xp_needed) if xp_needed > 0 else 0

        bar_label = label_font.render("XP Progress", True, LABEL_COLOR)
        bar_x = right_col_x
        bar_y = y_right + int(panel_height * 0.02)
        screen.blit(bar_label, (bar_x, bar_y))
        bar_y += bar_label.get_height() + 4
        bar_width = col_width - 20
        bar_height = int(panel_height * 0.035)
        draw_progress_bar(screen, bar_x, bar_y, bar_width, bar_height, progress, color=(100, 200, 255))
        xp_text = f"{xp} / {xp_needed} XP (Level {level})"
        xp_surf = label_font.render(xp_text, True, (200, 200, 220))
        screen.blit(xp_surf, (bar_x + (bar_width - xp_surf.get_width()) // 2, bar_y + bar_height + 4))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        if edit_mode == "editing":
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            box_width = max(320, int(screen_width * 0.5))
            box_height = max(170, int(screen_height * 0.3))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            pygame.draw.rect(screen, (30, 40, 70), pygame.Rect(box_x, box_y, box_width, box_height), border_radius=24)
            pygame.draw.rect(screen, (200, 220, 255), pygame.Rect(box_x, box_y, box_width, box_height), 2, border_radius=24)
            prompt = button_font.render("Enter new nickname", True, (245, 245, 245))
            screen.blit(prompt, (box_x + 24, box_y + 24))
            input_rect = pygame.Rect(box_x + 24, box_y + 70, box_width - 48, 44)
            pygame.draw.rect(screen, (255, 255, 255), input_rect, border_radius=12)
            input_label = button_font.render(pending_name, True, (40, 40, 60))
            text_width = input_label.get_width()
            text_height = input_label.get_height()
            caret_x = input_rect.x + 10 + text_width
            caret_y = input_rect.y + 8
            screen.blit(input_label, (input_rect.x + 10, input_rect.y + 10))
            if pygame.time.get_ticks() // 500 % 2 == 0:
                pygame.draw.line(screen, (40, 40, 60), (caret_x, caret_y), (caret_x, caret_y + text_height + 2), 2)
            pygame.draw.rect(screen, (70, 130, 180), save_rect, border_radius=16)
            pygame.draw.rect(screen, (130, 80, 80), cancel_rect, border_radius=16)
            save_label = button_font.render("Save", True, (255, 255, 255))
            cancel_label = button_font.render("Cancel", True, (255, 255, 255))
            screen.blit(save_label, save_label.get_rect(center=save_rect.center))
            screen.blit(cancel_label, cancel_label.get_rect(center=cancel_rect.center))
        elif edit_mode == "confirm":
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            box_width = max(320, int(screen_width * 0.5))
            box_height = max(170, int(screen_height * 0.3))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            pygame.draw.rect(screen, (30, 40, 70), pygame.Rect(box_x, box_y, box_width, box_height), border_radius=24)
            pygame.draw.rect(screen, (200, 220, 255), pygame.Rect(box_x, box_y, box_width, box_height), 2, border_radius=24)
            confirm_text = button_font.render(f"Confirm nickname: {pending_name}?", True, (245, 245, 245))
            screen.blit(confirm_text, (box_x + 24, box_y + 24))
            pygame.draw.rect(screen, (70, 130, 180), confirm_rect, border_radius=16)
            pygame.draw.rect(screen, (130, 80, 80), cancel_rect, border_radius=16)
            confirm_label = button_font.render("Confirm", True, (255, 255, 255))
            cancel_label = button_font.render("Cancel", True, (255, 255, 255))
            screen.blit(confirm_label, confirm_label.get_rect(center=confirm_rect.center))
            screen.blit(cancel_label, cancel_label.get_rect(center=cancel_rect.center))
        elif edit_mode == "error":
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            box_width = max(340, int(screen_width * 0.55))
            box_height = max(190, int(screen_height * 0.32))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            pygame.draw.rect(screen, (30, 40, 70), pygame.Rect(box_x, box_y, box_width, box_height), border_radius=24)
            pygame.draw.rect(screen, (200, 220, 255), pygame.Rect(box_x, box_y, box_width, box_height), 2, border_radius=24)
            error_title = button_font.render("Nickname invalid", True, (255, 200, 200))
            screen.blit(error_title, (box_x + 24, box_y + 24))
            error_text = button_font.render(error_message, True, (245, 245, 245))
            screen.blit(error_text, (box_x + 24, box_y + 72))
            pygame.draw.rect(screen, (70, 130, 180), retry_rect, border_radius=16)
            pygame.draw.rect(screen, (130, 80, 80), cancel_rect, border_radius=16)
            retry_label = button_font.render("Retry", True, (255, 255, 255))
            cancel_label = button_font.render("Cancel", True, (255, 255, 255))
            screen.blit(retry_label, retry_label.get_rect(center=retry_rect.center))
            screen.blit(cancel_label, cancel_label.get_rect(center=cancel_rect.center))

        pygame.display.flip()
        clock.tick(60)