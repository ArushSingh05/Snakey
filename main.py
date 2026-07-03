import math
import pygame
import random

from player_profile import load_player_profile_data, save_profile_data, show_profile
from play import show_play_menu
from customisation import show_customisation, SKIN_OPTIONS
from settings import show_settings
from fonts import get_font
from customisation import paint_arena
from ui_helpers import draw_transparent_panel

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_SCREEN_WIDTH = 320
MIN_SCREEN_HEIGHT = 240
BUTTON_COLOR = (36, 48, 88)
BUTTON_HOVER = (68, 98, 170)
BUTTON_TEXT = (245, 245, 245)

TITLE_COLOR = (20, 30, 60)


def draw_button(screen, font, rect, label, hover=False):
    pygame.draw.rect(screen, BUTTON_HOVER if hover else BUTTON_COLOR, rect, border_radius=20)
    text_surface = font.render(label, True, BUTTON_TEXT)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def run_main_menu(screen, clock, font, title_font, profile_data):
    buttons = [
        {"label": "Play", "action": "play"},
        {"label": "Profile", "action": "profile"},
        {"label": "Customisation", "action": "customisation"},
        {"label": "Settings", "action": "settings"},
        {"label": "Achievements", "action": "achievements"},
        {"label": "Exit", "action": "exit"},
    ]

    mouse_down_pos = None
    show_exit_confirm = False
    confirm_candidate = None
    confirm_yes_rect = pygame.Rect(0, 0, 0, 0)
    confirm_no_rect = pygame.Rect(0, 0, 0, 0)

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(48, min(96, int(screen_height * 0.16))))
        menu_font = get_font(max(20, min(34, int(screen_height * 0.06))))

        button_width = max(220, min(int(screen_width * 0.5), 340))
        button_height = max(50, min(int(screen_height * 0.09), 66))
        gap = max(10, min(int(screen_height * 0.02), 16))

        title_height = int(screen_height * 0.25)
        available_height = screen_height - title_height - int(screen_height * 0.08)
        total_buttons_height = len(buttons) * button_height + (len(buttons) - 1) * gap

        if total_buttons_height > available_height:
            button_height = max(40, (available_height - (len(buttons) - 1) * gap) // len(buttons))
            total_buttons_height = len(buttons) * button_height + (len(buttons) - 1) * gap

        start_y = title_height + (available_height - total_buttons_height) // 2
        start_x = (screen_width - button_width) // 2

        button_rects = []
        for index, button in enumerate(buttons):
            rect = pygame.Rect(
                start_x,
                start_y + index * (button_height + gap),
                button_width,
                button_height,
            )
            button_rects.append((rect, button["action"], button["label"]))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                new_width = max(event.size[0], MIN_SCREEN_WIDTH)
                new_height = max(event.size[1], MIN_SCREEN_HEIGHT)
                if new_width != event.size[0] or new_height != event.size[1]:
                    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down_pos = event.pos
                confirm_candidate = None
                if show_exit_confirm:
                    if confirm_yes_rect.collidepoint(event.pos):
                        confirm_candidate = "quit"
                    elif confirm_no_rect.collidepoint(event.pos):
                        confirm_candidate = "cancel"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if mouse_down_pos and abs(event.pos[0] - mouse_down_pos[0]) < 5 and abs(event.pos[1] - mouse_down_pos[1]) < 5:
                    if show_exit_confirm and confirm_candidate is not None:
                        if confirm_candidate == "quit" and confirm_yes_rect.collidepoint(event.pos):
                            return "quit"
                        if confirm_candidate == "cancel" and confirm_no_rect.collidepoint(event.pos):
                            show_exit_confirm = False
                    elif not show_exit_confirm:
                        for rect, action_key, _ in button_rects:
                            if rect.collidepoint(event.pos):
                                if action_key == "exit":
                                    show_exit_confirm = True
                                else:
                                    return action_key
                mouse_down_pos = None

        paint_arena(screen, profile_data)

        title_text = "Slim Snakey"
        title_surf = title_font_dyn.render(title_text, True, TITLE_COLOR)
        shadow_surf = title_font_dyn.render(title_text, True, (255, 255, 255, 30))
        tx = (screen_width - title_surf.get_width()) // 2
        ty = int(screen_height * 0.08)
        screen.blit(shadow_surf, (tx + 4, ty + 4))
        screen.blit(title_surf, (tx, ty))

        for rect, action_key, label in button_rects:
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, menu_font, rect, label, hover=hover)

        if show_exit_confirm:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            box_width = max(320, int(screen_width * 0.45))
            box_height = max(160, int(screen_height * 0.24))
            box_x = (screen_width - box_width) // 2
            box_y = (screen_height - box_height) // 2
            pygame.draw.rect(screen, (30, 40, 70), pygame.Rect(box_x, box_y, box_width, box_height), border_radius=24)
            pygame.draw.rect(screen, (200, 220, 255), pygame.Rect(box_x, box_y, box_width, box_height), 2, border_radius=24)
            prompt_text = menu_font.render("Exit the game?", True, (245, 245, 245))
            screen.blit(prompt_text, (box_x + 24, box_y + 24))
            button_row_y = box_y + box_height - 58
            button_width = 90
            button_height = 34
            button_gap = 16
            button_row_x = box_x + (box_width - (2 * button_width + button_gap)) // 2
            confirm_yes_rect = pygame.Rect(button_row_x, button_row_y, button_width, button_height)
            confirm_no_rect = pygame.Rect(button_row_x + button_width + button_gap, button_row_y, button_width, button_height)
            pygame.draw.rect(screen, (70, 130, 180), confirm_yes_rect, border_radius=16)
            pygame.draw.rect(screen, (130, 80, 80), confirm_no_rect, border_radius=16)
            yes_label = menu_font.render("Yes", True, (255, 255, 255))
            no_label = menu_font.render("No", True, (255, 255, 255))
            screen.blit(yes_label, yes_label.get_rect(center=confirm_yes_rect.center))
            screen.blit(no_label, no_label.get_rect(center=confirm_no_rect.center))

        pygame.display.flip()
        clock.tick(60)


def show_achievements_screen(screen, clock, font, title_font, profile_data):
    from achievements import ACHIEVEMENTS, get_unlocked_achievements
    unlocked_keys = get_unlocked_achievements(profile_data)
    selected = -1
    scroll_offset = 0

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(36, min(64, int(screen_height * 0.12))))
        ach_font = get_font(max(16, min(26, int(screen_height * 0.055))))
        button_font = get_font(max(14, min(24, int(screen_height * 0.055))))

        back_button_width = max(100, int(screen_width * 0.15))
        back_button_height = max(35, int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05), screen_height - back_button_height - 20, back_button_width, back_button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                new_width = max(event.size[0], MIN_SCREEN_WIDTH)
                new_height = max(event.size[1], MIN_SCREEN_HEIGHT)
                if new_width != event.size[0] or new_height != event.size[1]:
                    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_UP:
                    if selected < 0:
                        selected = len(ACHIEVEMENTS) - 1
                    else:
                        selected = max(0, selected - 1)
                if event.key == pygame.K_DOWN:
                    if selected < 0:
                        selected = 0
                    else:
                        selected = min(len(ACHIEVEMENTS) - 1, selected + 1)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, scroll_offset - event.y * int(screen_height * 0.06))

        paint_arena(screen, profile_data)

        title_surface = title_font_dyn.render("Achievements", True, TITLE_COLOR)
        screen.blit(title_surface, title_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.09))))

        top_y = int(screen_height * 0.18)
        header_height = max(36, int(screen_height * 0.06))
        line_spacing = max(42, int(screen_height * 0.07))
        list_top = top_y + header_height + 10
        visible_height = screen_height - list_top - (back_button_height + 40)
        total_height = len(ACHIEVEMENTS) * line_spacing
        max_scroll = max(0, total_height - visible_height)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        panel_width = screen_width - int(screen_width * 0.20)
        panel_height = visible_height + header_height + 30
        panel_x = (screen_width - panel_width) // 2
        panel_y = top_y - 10
        draw_transparent_panel(screen, panel_x, panel_y, panel_width, panel_height, radius=20)

        unlocked_count = len(unlocked_keys)
        summary_text = f"Unlocked: {unlocked_count}/{len(ACHIEVEMENTS)}"
        summary_surf = button_font.render(summary_text, True, (220, 230, 255))
        screen.blit(summary_surf, (panel_x + 20, panel_y + 16))
        pygame.draw.rect(screen, (70, 130, 180), pygame.Rect(panel_x + 12, panel_y + header_height + 6, panel_width - 24, 3), border_radius=2)

        for idx, (key, achievement) in enumerate(ACHIEVEMENTS.items()):
            y_pos = list_top + idx * line_spacing - scroll_offset
            if y_pos + line_spacing < list_top or y_pos > list_top + visible_height:
                continue
            if key in unlocked_keys:
                color = (100, 255, 100)
                status = "Unlocked"
            else:
                color = (140, 150, 170)
                status = "Locked"
            text = f"{status}  {achievement['name']}"
            if key in unlocked_keys:
                text += f"  (+{achievement['xp_reward']} XP)"
            txt_surf = ach_font.render(text, True, color)
            txt_x = panel_x + 24
            if selected >= 0 and idx == selected:
                bg_rect = pygame.Rect(panel_x + 12, y_pos - 6, panel_width - 24, line_spacing - 8)
                pygame.draw.rect(screen, (30, 40, 70), bg_rect, border_radius=12)
            screen.blit(txt_surf, (txt_x, y_pos))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Slim Snakey")
    clock = pygame.time.Clock()

    font = get_font(32)
    title_font = get_font(72)

    profile_data = load_player_profile_data()

    state = "menu"
    while state != "quit":
        current_width = screen.get_width()
        current_height = screen.get_height()
        if current_width < MIN_SCREEN_WIDTH or current_height < MIN_SCREEN_HEIGHT:
            new_width = max(current_width, MIN_SCREEN_WIDTH)
            new_height = max(current_height, MIN_SCREEN_HEIGHT)
            screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

        if state == "menu":
            state = run_main_menu(screen, clock, font, title_font, profile_data)
        elif state == "play":
            state = show_play_menu(screen, clock, font, title_font, profile_data)
        elif state == "profile":
            state = show_profile(screen, clock, font, title_font, profile_data)
            save_profile_data(profile_data)
        elif state == "customisation":
            state = show_customisation(screen, clock, font, title_font, profile_data)
            save_profile_data(profile_data)
        elif state == "settings":
            state = show_settings(screen, clock, font, title_font, profile_data)
            save_profile_data(profile_data)
        elif state == "achievements":
            state = show_achievements_screen(screen, clock, font, title_font, profile_data)
            save_profile_data(profile_data)
        else:
            state = "menu"

    save_profile_data(profile_data)
    pygame.quit()


if __name__ == "__main__":
    main()