import math
import random
import pygame

from player_profile import save_profile_data
from customisation import SKIN_OPTIONS, ARENA_OPTIONS, paint_arena
from my_sprite import Enemy, Snake, Food, EnemyAI
from achievements import update_achievements
from powerups import PowerUp, ActivePowerUp, POWERUP_TYPES
from time_limited_mode import TIME_LIMITS, show_time_limit_menu
from fonts import get_font
from ui_helpers import draw_transparent_panel

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_SCREEN_WIDTH = 320
MIN_SCREEN_HEIGHT = 240
FOOD_COLOR = (250, 190, 45)
TEXT_COLOR = (255, 255, 255)
TEXT_OUTLINE_COLOR = (0, 0, 0)
TITLE_COLOR = (20, 30, 60)

BASE_HEAD_RADIUS = 11
BASE_BODY_RADIUS = 9
BASE_FOOD_RADIUS = 8

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def is_opposite(direction_a, direction_b):
    return direction_a[0] == -direction_b[0] and direction_a[1] == -direction_b[1]

def get_scale_factor(screen):
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    width_scale = screen_width / SCREEN_WIDTH
    height_scale = screen_height / SCREEN_HEIGHT
    return min(width_scale, height_scale)

def render_outlined_text(surface, text, font, x, y, color=TEXT_COLOR, outline_color=TEXT_OUTLINE_COLOR, outline_width=2):
    text_surf = font.render(text, True, color)
    outline_surf = font.render(text, True, outline_color)
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                surface.blit(outline_surf, (x+dx, y+dy))
    surface.blit(text_surf, (x, y))

def draw_label_with_panel(screen, font, text, x, y, panel_padding=10):
    text_surf = font.render(text, True, TEXT_COLOR)
    tw, th = text_surf.get_size()
    panel_rect = pygame.Rect(x - panel_padding, y - panel_padding//2,
                             tw + panel_padding*2, th + panel_padding)
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surf.fill((0, 0, 0, 0))
    pygame.draw.rect(panel_surf, (0, 0, 0, 160), panel_surf.get_rect(), border_radius=8)
    screen.blit(panel_surf, (panel_rect.x, panel_rect.y))
    render_outlined_text(screen, text, font, x, y)

def run_match(screen, clock, font, big_font, profile_data, mode, time_limit_ms=None):
    if screen.get_width() < MIN_SCREEN_WIDTH or screen.get_height() < MIN_SCREEN_HEIGHT:
        screen = pygame.display.set_mode((max(screen.get_width(), MIN_SCREEN_WIDTH), max(screen.get_height(), MIN_SCREEN_HEIGHT)), pygame.RESIZABLE)

    active_powerups = []
    powerups_on_screen = []
    powerup_spawn_timer = 0

    custom = profile_data.get("customization", {})
    skin_index = custom.get("skin_index", 0) % len(SKIN_OPTIONS)
    skin = SKIN_OPTIONS[skin_index]
    settings = profile_data.get("settings", {})

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    start_time = pygame.time.get_ticks() if time_limit_ms is not None else None

    # Player snake
    snake = Snake(screen_width / 4, screen_height / 2, skin["body"], skin["head"], screen)
    score = 0
    food = Food(screen)

    # Second player (duo mode)
    player_two = None
    score_two = 0

    # Enemy AI (solo and time-limited only)
    enemy_ai = None
    if mode in ("solo", "time_limited"):
        enemy_ai = EnemyAI(3 * screen_width / 4, screen_height / 2, screen, snake, settings)
        enemy_ai.target_length = 30
        enemy_ai.speed = 4.5
        enemy_ai.max_speed = 7.0

    winner = None
    game_over = False
    running = True

    while running:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        score_font = get_font(max(16, min(28, int(screen_height * 0.055))))
        game_over_font = get_font(max(40, min(72, int(screen_height * 0.15))))
        restart_font = get_font(max(14, min(24, int(screen_height * 0.04))))

        direction_one = snake.direction
        accelerate_one = False
        direction_two = player_two.direction if player_two else None
        accelerate_two = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_profile_data(profile_data)
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                new_width = max(event.size[0], MIN_SCREEN_WIDTH)
                new_height = max(event.size[1], MIN_SCREEN_HEIGHT)
                if new_width != event.size[0] or new_height != event.size[1]:
                    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                    screen_width = new_width
                    screen_height = new_height
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_profile_data(profile_data)
                    return "menu"
                if event.key == pygame.K_SPACE and game_over:
                    return run_match(screen, clock, font, big_font, profile_data, mode)

        keys = pygame.key.get_pressed()
        # Player 1 controls
        if keys[pygame.K_LEFT]:
            new_dir = (-1.0, 0.0)
            if not is_opposite(new_dir, direction_one):
                direction_one = new_dir
        elif keys[pygame.K_RIGHT]:
            new_dir = (1.0, 0.0)
            if not is_opposite(new_dir, direction_one):
                direction_one = new_dir
        elif keys[pygame.K_UP]:
            new_dir = (0.0, -1.0)
            if not is_opposite(new_dir, direction_one):
                direction_one = new_dir
        elif keys[pygame.K_DOWN]:
            new_dir = (0.0, 1.0)
            if not is_opposite(new_dir, direction_one):
                direction_one = new_dir

        # Player 2 controls (duo only)
        if player_two:
            if keys[pygame.K_a]:
                new_dir = (-1.0, 0.0)
                if not is_opposite(new_dir, direction_two):
                    direction_two = new_dir
            elif keys[pygame.K_d]:
                new_dir = (1.0, 0.0)
                if not is_opposite(new_dir, direction_two):
                    direction_two = new_dir
            elif keys[pygame.K_w]:
                new_dir = (0.0, -1.0)
                if not is_opposite(new_dir, direction_two):
                    direction_two = new_dir
            elif keys[pygame.K_s]:
                new_dir = (0.0, 1.0)
                if not is_opposite(new_dir, direction_two):
                    direction_two = new_dir

        if not game_over:
            snake.update(direction_one, accelerate_one, settings)

            if player_two:
                player_two.update(direction_two, accelerate_two, settings)

            if enemy_ai:
                enemy_ai.update()

            if time_limit_ms is not None:
                elapsed = pygame.time.get_ticks() - start_time
                if elapsed >= time_limit_ms:
                    game_over = True
                    winner = None

            # Power-ups
            powerup_spawn_timer += 1
            if powerup_spawn_timer > 600:
                from powerups import spawn_random_powerup
                powerups_on_screen.append(spawn_random_powerup(screen))
                powerup_spawn_timer = 0

            for powerup in powerups_on_screen[:]:
                if powerup.is_expired():
                    powerups_on_screen.remove(powerup)
                elif snake.check_food_collision(powerup):
                    active_powerups.append(ActivePowerUp(powerup.powerup_type, snake))
                    powerup.collected = True
                    powerups_on_screen.remove(powerup)

            # Food collision
            if snake.check_food_collision(food):
                score += 1
                profile_data["food_consumed"] = profile_data.get("food_consumed", 0) + 1
                snake.grow(14)
                food.respawn()

            if player_two and player_two.check_food_collision(food):
                score_two += 1
                profile_data["food_consumed"] = profile_data.get("food_consumed", 0) + 1
                player_two.grow(14)
                food.respawn()

            # Enemy AI food (optional)
            if enemy_ai and enemy_ai.check_food_collision(food):
                enemy_ai.grow(10)
                food.respawn()

            # Self-collision (player)
            if snake.check_self_collision():
                game_over = True
                winner = "Player 2" if player_two else "Enemy"

            # Player vs enemy AI collision
            if enemy_ai:
                if snake.check_collision_with_segments(enemy_ai.points[:-5]):
                    game_over = True
                    winner = "Enemy"
                if enemy_ai.check_collision_with_segments(snake.points[:-5]):
                    game_over = True
                    winner = "Player"

            # Duo mode collisions (player vs player)
            if player_two:
                if player_two.check_self_collision():
                    game_over = True
                    winner = "Player 1"
                if snake.check_collision_with_segments(player_two.points[:-5]):
                    game_over = True
                    winner = "Player 2"
                if player_two.check_collision_with_segments(snake.points[:-5]):
                    game_over = True
                    winner = "Player 1"

        # Game over handling
        if game_over:
            profile_data["games_played"] = profile_data.get("games_played", 0) + 1
            profile_data["deaths"] = profile_data.get("deaths", 0) + 1

            if player_two and winner == "Player 1":
                profile_data["pvp_wins"] = profile_data.get("pvp_wins", 0) + 1

            if score > profile_data.get("high_score", 0):
                profile_data["high_score"] = score
            if score_two > profile_data.get("high_score", 0):
                profile_data["high_score"] = score_two

            update_achievements(profile_data)
            save_profile_data(profile_data)

            game_over = "displayed"

        # Rendering
        paint_arena(screen, profile_data)
        food.draw(screen)
        for powerup in powerups_on_screen:
            powerup.draw(screen)
        snake.draw(screen)
        if player_two:
            player_two.draw(screen)
        if enemy_ai:
            enemy_ai.draw(screen)

        # HUD
        if player_two:
            draw_label_with_panel(screen, score_font, f"P1: {score}",
                                  int(screen_width * 0.02), int(screen_height * 0.03))
            draw_label_with_panel(screen, score_font, f"P2: {score_two}",
                                  int(screen_width * 0.02), int(screen_height * 0.08))
        else:
            if time_limit_ms is not None:
                elapsed = pygame.time.get_ticks() - start_time
                remaining = max(0, time_limit_ms - elapsed) / 1000
                draw_label_with_panel(screen, score_font, f"Time left: {remaining:.1f}s",
                                      int(screen_width * 0.02), int(screen_height * 0.03))
                draw_label_with_panel(screen, score_font, f"Score: {score}",
                                      int(screen_width * 0.02), int(screen_height * 0.08))
            else:
                draw_label_with_panel(screen, score_font, f"Score: {score}",
                                      int(screen_width * 0.02), int(screen_height * 0.03))

        if game_over == "displayed":
            game_over_text = "Game Over" if not winner else f"{winner} wins!"
            go_surf = game_over_font.render(game_over_text, True, TEXT_COLOR)
            go_outline = game_over_font.render(game_over_text, True, TEXT_OUTLINE_COLOR)
            gx = screen_width / 2 - go_surf.get_width() / 2
            gy = screen_height / 2 - int(screen_height * 0.1)
            for dx in (-2, 0, 2):
                for dy in (-2, 0, 2):
                    if dx != 0 or dy != 0:
                        screen.blit(go_outline, (gx+dx, gy+dy))
            screen.blit(go_surf, (gx, gy))

            restart_surf = restart_font.render("Press SPACE to restart", True, TEXT_COLOR)
            restart_outline = restart_font.render("Press SPACE to restart", True, TEXT_OUTLINE_COLOR)
            rx = screen_width / 2 - restart_surf.get_width() / 2
            ry = screen_height / 2 + int(screen_height * 0.05)
            for dx in (-2, 0, 2):
                for dy in (-2, 0, 2):
                    if dx != 0 or dy != 0:
                        screen.blit(restart_outline, (rx+dx, ry+dy))
            screen.blit(restart_surf, (rx, ry))

        pygame.display.flip()
        clock.tick(60)

    return "menu"

def draw_label(screen, font, text, x, y):
    screen.blit(font.render(text, True, TEXT_COLOR), (x, y))


def show_play_menu(screen, clock, font, big_font, profile_data):
    options = ["Solo", "Play with friend", "Time Limited"]
    selected = 0

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(36, min(64, int(screen_height * 0.12))))
        menu_font = get_font(max(20, min(32, int(screen_height * 0.07))))
        hint_font = get_font(max(14, min(24, int(screen_height * 0.05))))
        button_font = get_font(max(14, min(24, int(screen_height * 0.05))))

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
                    selected = min(len(options) - 1, selected + 1)
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        return run_match(screen, clock, font, big_font, profile_data, "solo")
                    if selected == 1:
                        return run_match(screen, clock, font, big_font, profile_data, "duo")
                    if selected == 2:
                        time_limit_key = show_time_limit_menu(screen, clock, font, big_font, profile_data)
                        if time_limit_key == "quit":
                            return "quit"
                        if time_limit_key == "menu":
                            return "menu"
                        time_limit_ms = TIME_LIMITS.get(time_limit_key)
                        if time_limit_ms is None:
                            return "menu"
                        return run_match(screen, clock, font, big_font, profile_data, "time_limited", time_limit_ms=time_limit_ms)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        paint_arena(screen, profile_data)

        title = title_font_dyn.render("Play", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(screen_width / 2, int(screen_height * 0.15))))

        panel_top = int(screen_height * 0.25)
        panel_bottom = int(screen_height * 0.70)
        panel_width = screen_width - int(screen_width * 0.20)
        panel_x = (screen_width - panel_width) // 2
        panel_height = panel_bottom - panel_top
        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        option_y_start = panel_top + int(panel_height * 0.12)
        option_spacing = int(panel_height * 0.2)
        for idx, label in enumerate(options):
            color = (255, 255, 255) if idx == selected else (180, 180, 180)
            label_surf = menu_font.render(label, True, color)
            label_x = panel_x + (panel_width - label_surf.get_width()) // 2
            screen.blit(label_surf, (label_x, option_y_start + idx * option_spacing))

        if selected == 2:
            help_text = hint_font.render("Select a time limit and press ENTER.", True, (200, 200, 220))
            help_x = panel_x + (panel_width - help_text.get_width()) // 2
            screen.blit(help_text, (help_x, option_y_start + len(options) * option_spacing + 10))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)