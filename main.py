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
from my_sprite import Snake, Food

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_SCREEN_WIDTH = 320
MIN_SCREEN_HEIGHT = 240
BUTTON_COLOR = (36, 48, 88)
BUTTON_HOVER = (68, 98, 170)
BUTTON_TEXT = (245, 245, 245)

TITLE_COLOR = (20, 30, 60)

# Grid size for background snake
GRID_SIZE = 20

class BackgroundSnake(Snake):
    """Snake that moves on a grid with 90-degree turns and self-avoidance."""
    def __init__(self, x, y, body_color, head_color, screen):
        super().__init__(x, y, body_color, head_color, screen)
        self.speed = 0.5
        self.step_counter = 0
        self.step_interval = 2
        self.direction = (1.0, 0.0)
        self.next_direction = None

    def snap_to_grid(self, x, y):
        g = GRID_SIZE
        return round(x / g) * g, round(y / g) * g

    def update(self, direction=None, accelerate=False, settings=None):
        if direction is not None:
            self.next_direction = direction

        head_x, head_y = self.points[-1]
        if head_x % GRID_SIZE != 0 or head_y % GRID_SIZE != 0:
            self._move_towards_grid()
            return

        candidates = self._get_cardinal_directions()
        candidates = [d for d in candidates if not self._is_opposite(d, self.direction)]
        target = self._find_nearest_food()
        if target:
            candidates.sort(key=lambda d: self._distance_to_point(d, target))
        for d in candidates:
            new_head = (head_x + d[0] * GRID_SIZE, head_y + d[1] * GRID_SIZE)
            if not self._would_collide(new_head):
                self.direction = d
                self._move_one_step()
                return

        new_head = (head_x + self.direction[0] * GRID_SIZE, head_y + self.direction[1] * GRID_SIZE)
        if not self._would_collide(new_head):
            self._move_one_step()
            return
        pass

    def _move_towards_grid(self):
        head_x, head_y = self.points[-1]
        g = GRID_SIZE
        dx = 0
        dy = 0
        if head_x % g != 0:
            dx = 1 if head_x % g < g/2 else -1
        if head_y % g != 0:
            dy = 1 if head_y % g < g/2 else -1
        if dx != 0 and dy != 0:
            if abs(self.direction[0]) > 0:
                dy = 0
            else:
                dx = 0
        new_x = head_x + dx
        new_y = head_y + dy
        self.points.append((new_x, new_y))
        if len(self.points) > self.target_length:
            self.points.pop(0)

    def _get_cardinal_directions(self):
        return [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def _is_opposite(self, d1, d2):
        return d1[0] == -d2[0] and d1[1] == -d2[1]

    def _distance_to_point(self, direction, point):
        hx, hy = self.points[-1]
        nx, ny = hx + direction[0] * GRID_SIZE, hy + direction[1] * GRID_SIZE
        return (nx - point[0]) ** 2 + (ny - point[1]) ** 2

    def _would_collide(self, new_head_pos):
        tail_pos = self.points[0] if len(self.points) > 0 else None
        for idx, point in enumerate(self.points[:-1]):
            if idx == 0 and tail_pos == new_head_pos:
                continue
            if (point[0] - new_head_pos[0]) ** 2 + (point[1] - new_head_pos[1]) ** 2 < (self.body_radius * 2) ** 2:
                return True
        return False

    def _move_one_step(self):
        head_x, head_y = self.points[-1]
        new_x = head_x + self.direction[0] * GRID_SIZE
        new_y = head_y + self.direction[1] * GRID_SIZE
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        new_x = new_x % screen_width
        new_y = new_y % screen_height
        self.points.append((new_x, new_y))
        if len(self.points) > self.target_length:
            self.points.pop(0)

    def _find_nearest_food(self):
        if not hasattr(self, '_foods') or not self._foods:
            return None
        head = self.points[-1]
        nearest = min(self._foods, key=lambda f: ((head[0] - f.pos[0]) ** 2 + (head[1] - f.pos[1]) ** 2))
        return nearest.pos


class BackgroundGame:
    def __init__(self, screen, profile_data):
        self.screen = screen
        self.profile_data = profile_data
        self.foods = []
        self.init_game()

    def init_game(self):
        custom = self.profile_data.get("customization", {})
        skin_index = custom.get("skin_index", 0) % len(SKIN_OPTIONS)
        skin = SKIN_OPTIONS[skin_index]
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.snake = BackgroundSnake(screen_width / 2, screen_height / 2, skin["body"], skin["head"], self.screen)
        self.snake.target_length = 30
        self.snake._foods = []
        self.foods = [Food(self.screen) for _ in range(4)]
        for food in self.foods:
            self.avoid_snake(food)
        self.snake._foods = self.foods

    def avoid_snake(self, food):
        max_attempts = 20
        for _ in range(max_attempts):
            ok = True
            for point in self.snake.points:
                if ((point[0] - food.pos[0]) ** 2 + (point[1] - food.pos[1]) ** 2) < 400:
                    ok = False
                    break
            if ok:
                return
            food.respawn()

    def update(self):
        if not self.foods:
            return
        self.snake.update()
        for food in self.foods[:]:
            if self.snake.check_food_collision(food):
                self.snake.grow(10)
                food.respawn()
                self.avoid_snake(food)
        if len(self.snake.points) > 150:
            self.snake.points = self.snake.points[-150:]

    def draw(self, screen):
        for food in self.foods:
            food.draw(screen)
        self.snake.draw(screen)


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
    ]

    bg_game = BackgroundGame(screen, profile_data)

    mouse_down_pos = None

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
                    bg_game.screen = screen
                    bg_game.init_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if mouse_down_pos and abs(event.pos[0] - mouse_down_pos[0]) < 5 and abs(event.pos[1] - mouse_down_pos[1]) < 5:
                    for rect, action_key, _ in button_rects:
                        if rect.collidepoint(event.pos):
                            return action_key
                mouse_down_pos = None

        paint_arena(screen, profile_data)
        bg_game.update()
        bg_game.draw(screen)

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

        pygame.display.flip()
        clock.tick(60)


def show_achievements_screen(screen, clock, font, title_font, profile_data):
    from achievements import ACHIEVEMENTS, get_unlocked_achievements
    unlocked_keys = get_unlocked_achievements(profile_data)
    selected = 0
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
                    selected = max(0, selected - 1)
                if event.key == pygame.K_DOWN:
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
        line_spacing = int(screen_height * 0.07)
        left_x = int(screen_width * 0.12)
        visible_height = screen_height - top_y - (back_button_height + 40)
        total_height = len(ACHIEVEMENTS) * line_spacing
        max_scroll = max(0, total_height - visible_height)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        panel_width = screen_width - int(screen_width * 0.20)
        panel_height = visible_height + 20
        panel_x = (screen_width - panel_width) // 2
        panel_y = top_y - 10
        draw_transparent_panel(screen, panel_x, panel_y, panel_width, panel_height, radius=20)

        for idx, (key, achievement) in enumerate(ACHIEVEMENTS.items()):
            y_pos = top_y + idx * line_spacing - scroll_offset
            if y_pos + line_spacing < top_y or y_pos > top_y + visible_height:
                continue
            if key in unlocked_keys:
                color = (100, 255, 100)
                text = f"✓ {achievement['name']} (+{achievement['xp_reward']} XP)"
            else:
                color = (100, 100, 100)
                text = f"✗ {achievement['name']}"
            txt_surf = ach_font.render(text, True, color)
            txt_x = panel_x + (panel_width - txt_surf.get_width()) // 2
            if idx == selected:
                bg_rect = pygame.Rect(txt_x - 8, y_pos - 4, txt_surf.get_width() + 16, line_spacing)
                pygame.draw.rect(screen, (30, 40, 70), bg_rect)
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