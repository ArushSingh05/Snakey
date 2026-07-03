import pygame
from input_validation import clamp_value
from fonts import get_font
from customisation import paint_arena
from ui_helpers import draw_transparent_panel

DEFAULT_SETTINGS = {
    "turn_sensitivity": 0.08,
}
TITLE_COLOR = (20, 30, 60)


def ensure_settings(data):
    settings = data.get("settings", {})
    for key, default in DEFAULT_SETTINGS.items():
        settings.setdefault(key, default)
    data["settings"] = settings
    return settings


def show_settings(screen, clock, font, big_font, profile_data):
    settings = ensure_settings(profile_data)
    option_index = 0
    # Only turn_sensitivity is exposed; acceleration is handled via power-ups
    options = ["turn_sensitivity"]
    value_labels = {
        "turn_sensitivity": "Turn sensitivity",
    }

    MIN_VAL = 0.02
    MAX_VAL = 0.18
    STEP    = 0.01

    while True:
        screen_width  = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(36, min(64, int(screen_height * 0.12))))
        settings_font  = get_font(max(18, min(28, int(screen_height * 0.07))))
        hint_font      = get_font(max(14, min(22, int(screen_height * 0.048))))
        button_font    = get_font(max(14, min(24, int(screen_height * 0.055))))

        back_button_width  = max(100, int(screen_width * 0.15))
        back_button_height = max(35,  int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05),
                                screen_height - back_button_height - 20,
                                back_button_width, back_button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                nw = max(event.size[0], 320)
                nh = max(event.size[1], 240)
                screen = pygame.display.set_mode((nw, nh), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_UP:
                    option_index = max(0, option_index - 1)
                if event.key == pygame.K_DOWN:
                    option_index = min(len(options) - 1, option_index + 1)
                if event.key == pygame.K_LEFT:
                    key = options[option_index]
                    settings[key] = clamp_value(settings[key] - STEP, MIN_VAL, MAX_VAL, MIN_VAL)
                if event.key == pygame.K_RIGHT:
                    key = options[option_index]
                    settings[key] = clamp_value(settings[key] + STEP, MIN_VAL, MAX_VAL, MAX_VAL)
                if event.key == pygame.K_RETURN:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        paint_arena(screen, profile_data)
        title = title_font_dyn.render("Settings", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(screen_width // 2, int(screen_height * 0.1))))

        panel_top    = int(screen_height * 0.22)
        panel_bottom = int(screen_height * 0.65)
        panel_width  = screen_width - int(screen_width * 0.20)
        panel_x      = (screen_width - panel_width) // 2
        panel_height = panel_bottom - panel_top
        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        option_y = panel_top + int(panel_height * 0.20)
        option_spacing = int(panel_height * 0.30)
        for idx, key in enumerate(options):
            label_text = f"{value_labels[key]}: {settings[key]:.2f}"
            color = (255, 255, 255) if idx == option_index else (180, 180, 180)
            label = settings_font.render(label_text, True, color)
            label_x = panel_x + (panel_width - label.get_width()) // 2
            screen.blit(label, (label_x, option_y + idx * option_spacing))

        # Note about acceleration
        note = hint_font.render("Acceleration: collect Speed Boost power-ups in-game!", True, (180, 200, 255))
        note_x = panel_x + (panel_width - note.get_width()) // 2
        screen.blit(note, (note_x, panel_top + int(panel_height * 0.60)))

        hint = button_font.render("Use UP/DOWN to switch, LEFT/RIGHT to change", True, (210, 225, 255))
        hint_x = panel_x + (panel_width - hint.get_width()) // 2
        screen.blit(hint, (hint_x, panel_top + int(panel_height * 0.74)))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)