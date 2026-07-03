"""
Time-limited game mode where players compete for maximum score in fixed duration
Helps players develop strategy and improve decision-making under pressure.
"""

import pygame
from fonts import get_font
from customisation import paint_arena
from ui_helpers import draw_transparent_panel

TIME_LIMITS = {
    "30_seconds": 30000,
    "1_minute": 60000,
    "3_minutes": 180000,
    "5_minutes": 300000
}
TITLE_COLOR = (20, 30, 60)

def show_time_limit_menu(screen, clock, font, big_font, profile_data):
    options = [
        ("30 Seconds", "30_seconds"),
        ("1 Minute", "1_minute"),
        ("3 Minutes", "3_minutes"),
        ("5 Minutes", "5_minutes"),
    ]
    selected = 0

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(36, min(64, int(screen_height * 0.12))))
        menu_font = get_font(max(18, min(28, int(screen_height * 0.06))))
        hint_font = get_font(max(14, min(22, int(screen_height * 0.045))))
        button_font = get_font(max(14, min(24, int(screen_height * 0.055))))

        back_button_width = max(100, int(screen_width * 0.15))
        back_button_height = max(35, int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05), screen_height - back_button_height - 20, back_button_width, back_button_height)

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
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_DOWN:
                    selected = min(len(options) - 1, selected + 1)
                if event.key == pygame.K_RETURN:
                    return options[selected][1]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        paint_arena(screen, profile_data)
        title = title_font_dyn.render("Time Limited Mode", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(screen_width / 2, int(screen_height * 0.12))))

        instructions = menu_font.render("Select time limit:", True, (200, 200, 220))
        screen.blit(instructions, (screen_width / 2 - instructions.get_width() // 2, int(screen_height * 0.25)))

        # Panel for options – centered
        panel_top = int(screen_height * 0.30)
        panel_bottom = int(screen_height * 0.75)
        panel_width = screen_width - int(screen_width * 0.20)
        panel_x = (screen_width - panel_width) // 2
        panel_height = panel_bottom - panel_top
        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        option_y = panel_top + int(panel_height * 0.15)
        option_spacing = int(panel_height * 0.18)
        for idx, (label, _) in enumerate(options):
            color = (255, 255, 255) if idx == selected else (180, 180, 180)
            label_surf = menu_font.render(label, True, color)
            label_x = panel_x + (panel_width - label_surf.get_width()) // 2
            screen.blit(label_surf, (label_x, option_y + idx * option_spacing))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)

def run_time_limited_match(screen, clock, font, big_font, profile_data, time_limit_key):
    if time_limit_key not in TIME_LIMITS:
        return "menu"

    time_limit_ms = TIME_LIMITS[time_limit_key]
    start_time = pygame.time.get_ticks()

    while True:
        elapsed = pygame.time.get_ticks() - start_time
        remaining = max(0, time_limit_ms - elapsed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"

        paint_arena(screen, profile_data)

        seconds = remaining / 1000
        time_text = f"Time: {seconds:.1f}s"
        time_surface = big_font.render(time_text, True, (255, 100, 100))
        screen.blit(time_surface, time_surface.get_rect(center=(screen.get_width() / 2, 150)))

        info = font.render("Time-limited mode (Under Development)", True, (200, 200, 220))
        screen.blit(info, info.get_rect(center=(screen.get_width() / 2, 300)))

        pygame.display.flip()
        clock.tick(60)

        if remaining <= 0:
            return "menu"