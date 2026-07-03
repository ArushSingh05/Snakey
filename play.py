import math
import random
import pygame

from player_profile import save_profile_data
from customisation import SKIN_OPTIONS, ARENA_OPTIONS, paint_arena
from my_sprite import Enemy, Snake, Food, EnemyAI
from achievements import update_achievements
from powerups import PowerUp, ActivePowerUp, POWERUP_TYPES, spawn_random_powerup
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

# Player 2 skin (always blue tones so it's clearly distinct)
P2_BODY_COLOR = (60, 120, 220)
P2_HEAD_COLOR = (180, 210, 255)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def award_food_xp(profile_data):
    food_consumed = profile_data.get("food_consumed", 0) + 1
    profile_data["food_consumed"] = food_consumed

    if food_consumed <= 25:
        xp_gain = 1
    elif food_consumed <= 75:
        xp_gain = 2
    else:
        xp_gain = 3

    profile_data["xp"] = profile_data.get("xp", 0) + xp_gain
    profile_data["level"] = (profile_data.get("xp", 0) // 500) + 1


def award_kill(profile_data):
    profile_data["kills"] = profile_data.get("kills", 0) + 1
    profile_data["xp"] = profile_data.get("xp", 0) + 10
    profile_data["level"] = (profile_data.get("xp", 0) // 500) + 1


def award_death(profile_data):
    profile_data["deaths"] = profile_data.get("deaths", 0) + 1


def register_collision_outcome(profile_data, player_won):
    if player_won:
        award_kill(profile_data)
    else:
        award_death(profile_data)


def resolve_collision_result(player_hit_other_snake):
    if player_hit_other_snake:
        return False, "Enemy"
    return True, "Player"


def is_opposite(a, b):
    return a[0] == -b[0] and a[1] == -b[1]


def get_scale_factor(screen):
    return min(screen.get_width() / SCREEN_WIDTH, screen.get_height() / SCREEN_HEIGHT)


def render_outlined_text(surface, text, font, x, y,
                         color=TEXT_COLOR, outline_color=TEXT_OUTLINE_COLOR, outline_width=2):
    text_surf = font.render(text, True, color)
    outline_surf = font.render(text, True, outline_color)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                surface.blit(outline_surf, (x + dx, y + dy))
    surface.blit(text_surf, (x, y))


def draw_label_with_panel(screen, font, text, x, y, panel_padding=10):
    text_surf = font.render(text, True, TEXT_COLOR)
    tw, th = text_surf.get_size()
    panel_rect = pygame.Rect(x - panel_padding, y - panel_padding // 2,
                             tw + panel_padding * 2, th + panel_padding)
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surf.fill((0, 0, 0, 0))
    pygame.draw.rect(panel_surf, (0, 0, 0, 160), panel_surf.get_rect(), border_radius=8)
    screen.blit(panel_surf, (panel_rect.x, panel_rect.y))
    render_outlined_text(screen, text, font, x, y)


def _process_active_powerups(active_powerups):
    """Expire and remove finished power-ups, calling their cleanup method."""
    for pu in active_powerups[:]:
        if not pu.is_active():
            pu.expire()
            active_powerups.remove(pu)


def run_match(screen, clock, font, big_font, profile_data, mode, time_limit_ms=None):
    if screen.get_width() < MIN_SCREEN_WIDTH or screen.get_height() < MIN_SCREEN_HEIGHT:
        screen = pygame.display.set_mode(
            (max(screen.get_width(), MIN_SCREEN_WIDTH),
             max(screen.get_height(), MIN_SCREEN_HEIGHT)),
            pygame.RESIZABLE)

    # Active power-ups per snake (each list contains ActivePowerUp objects)
    active_powerups_p1 = []
    active_powerups_p2 = []
    powerups_on_screen  = []
    powerup_spawn_timer = 0

    custom     = profile_data.get("customization", {})
    skin_index = custom.get("skin_index", 0) % len(SKIN_OPTIONS)
    skin       = SKIN_OPTIONS[skin_index]
    settings   = profile_data.get("settings", {})

    screen_width  = screen.get_width()
    screen_height = screen.get_height()
    start_time    = pygame.time.get_ticks() if time_limit_ms is not None else None

    # Player 1
    snake  = Snake(screen_width / 4, screen_height / 2, skin["body"], skin["head"], screen)
    score  = 0
    food   = Food(screen)

    # Player 2 (duo)
    player_two  = None
    score_two   = 0
    if mode == "duo":
        # Spawn P2 on the right side, heading left
        player_two = Snake(3 * screen_width / 4, screen_height / 2,
                           P2_BODY_COLOR, P2_HEAD_COLOR, screen)
        player_two.direction = (-1.0, 0.0)

    # Enemy AI (solo / time_limited only)
    enemy_ai = None
    if mode in ("solo", "time_limited"):
        enemy_ai = EnemyAI(3 * screen_width / 4, screen_height / 2, screen, snake, settings)
        enemy_ai.target_length = 30
        enemy_ai.speed         = 4.8
        enemy_ai.max_speed     = 7.5
        enemy_ai._foods        = [food]
        enemy_ai.powerups      = powerups_on_screen

    winner    = None
    game_over = False
    running   = True

    while running:
        screen_width  = screen.get_width()
        screen_height = screen.get_height()

        score_font     = get_font(max(16, min(28, int(screen_height * 0.055))))
        game_over_font = get_font(max(40, min(72, int(screen_height * 0.15))))
        restart_font   = get_font(max(14, min(24, int(screen_height * 0.04))))

        direction_one = snake.direction
        direction_two = player_two.direction if player_two else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_profile_data(profile_data)
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                nw = max(event.size[0], MIN_SCREEN_WIDTH)
                nh = max(event.size[1], MIN_SCREEN_HEIGHT)
                screen = pygame.display.set_mode((nw, nh), pygame.RESIZABLE)
                screen_width, screen_height = nw, nh
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_profile_data(profile_data)
                    return "menu"
                if event.key == pygame.K_SPACE and game_over:
                    return run_match(screen, clock, font, big_font, profile_data, mode, time_limit_ms)

        keys = pygame.key.get_pressed()

        # Player 1: arrow keys
        if keys[pygame.K_LEFT]:
            nd = (-1.0, 0.0)
            if not is_opposite(nd, direction_one):
                direction_one = nd
        elif keys[pygame.K_RIGHT]:
            nd = (1.0, 0.0)
            if not is_opposite(nd, direction_one):
                direction_one = nd
        elif keys[pygame.K_UP]:
            nd = (0.0, -1.0)
            if not is_opposite(nd, direction_one):
                direction_one = nd
        elif keys[pygame.K_DOWN]:
            nd = (0.0, 1.0)
            if not is_opposite(nd, direction_one):
                direction_one = nd

        # Player 2: WASD
        if player_two:
            if keys[pygame.K_a]:
                nd = (-1.0, 0.0)
                if not is_opposite(nd, direction_two):
                    direction_two = nd
            elif keys[pygame.K_d]:
                nd = (1.0, 0.0)
                if not is_opposite(nd, direction_two):
                    direction_two = nd
            elif keys[pygame.K_w]:
                nd = (0.0, -1.0)
                if not is_opposite(nd, direction_two):
                    direction_two = nd
            elif keys[pygame.K_s]:
                nd = (0.0, 1.0)
                if not is_opposite(nd, direction_two):
                    direction_two = nd

        if not game_over:
            # Expire power-ups
            _process_active_powerups(active_powerups_p1)
            _process_active_powerups(active_powerups_p2)

            # Update snakes
            snake.update(direction_one, False, settings)
            if player_two:
                player_two.update(direction_two, False, settings)
            if enemy_ai:
                enemy_ai.update()

            # Time limit
            if time_limit_ms is not None:
                if pygame.time.get_ticks() - start_time >= time_limit_ms:
                    game_over = True
                    winner = None

            # Spawn power-ups
            powerup_spawn_timer += 1
            if powerup_spawn_timer > 480:
                powerups_on_screen.append(spawn_random_powerup(screen))
                powerup_spawn_timer = 0

            # Expire uncollected power-ups on screen
            for pu in powerups_on_screen[:]:
                if pu.is_expired():
                    powerups_on_screen.remove(pu)

            # P1 collects power-up
            for pu in powerups_on_screen[:]:
                if snake.check_food_collision(pu):
                    active_powerups_p1.append(ActivePowerUp(pu.powerup_type, snake))
                    pu.collected = True
                    powerups_on_screen.remove(pu)

            # P2 collects power-up
            if player_two:
                for pu in powerups_on_screen[:]:
                    if player_two.check_food_collision(pu):
                        active_powerups_p2.append(ActivePowerUp(pu.powerup_type, player_two))
                        pu.collected = True
                        powerups_on_screen.remove(pu)

            # Enemy AI collects power-up
            if enemy_ai:
                for pu in powerups_on_screen[:]:
                    if enemy_ai.check_food_collision(pu):
                        active_powerups_p2.append(ActivePowerUp(pu.powerup_type, enemy_ai))
                        pu.collected = True
                        powerups_on_screen.remove(pu)

            # Food collisions
            if snake.check_food_collision(food):
                score += 1
                award_food_xp(profile_data)
                snake.grow(14)
                food.respawn()

            if player_two and player_two.check_food_collision(food):
                score_two += 1
                award_food_xp(profile_data)
                player_two.grow(14)
                food.respawn()

            if enemy_ai and enemy_ai.check_food_collision(food):
                enemy_ai.grow(10)
                food.respawn()

            # Collision detection
            if snake.check_self_collision():
                game_over = True
                winner = "Player 2" if player_two else "Enemy"
                register_collision_outcome(profile_data, player_won=False)

            if enemy_ai and not game_over:
                if snake.check_collision_with_segments(enemy_ai.points[:-5]):
                    game_over = True
                    player_won, winner_text = resolve_collision_result(player_hit_other_snake=True)
                    winner = winner_text
                    register_collision_outcome(profile_data, player_won=player_won)
                if enemy_ai.check_collision_with_segments(snake.points[:-5]):
                    game_over = True
                    player_won, winner_text = resolve_collision_result(player_hit_other_snake=False)
                    winner = winner_text
                    register_collision_outcome(profile_data, player_won=player_won)

            if player_two and not game_over:
                if player_two.check_self_collision():
                    game_over = True
                    winner = "Player 1"
                    register_collision_outcome(profile_data, player_won=False)
                if snake.check_collision_with_segments(player_two.points[:-5]):
                    game_over = True
                    winner = "Player 2"
                    register_collision_outcome(profile_data, player_won=False)
                if player_two.check_collision_with_segments(snake.points[:-5]):
                    game_over = True
                    winner = "Player 1"
                    register_collision_outcome(profile_data, player_won=True)

        # Stats & save on game-over.
        if game_over and game_over is not True.__class__:
            pass
        if game_over is True:
            profile_data["games_played"] = profile_data.get("games_played", 0) + 1
            if not profile_data.get("deaths"):
                profile_data["deaths"] = 0
            if player_two and winner == "Player 1":
                profile_data["pvp_wins"] = profile_data.get("pvp_wins", 0) + 1
            if score > profile_data.get("high_score", 0):
                profile_data["high_score"] = score
            if score_two > profile_data.get("high_score", 0):
                profile_data["high_score"] = score_two
            update_achievements(profile_data)
            save_profile_data(profile_data)
            game_over = "displayed"

        # Render
        paint_arena(screen, profile_data)
        food.draw(screen)
        for pu in powerups_on_screen:
            pu.draw(screen)
        snake.draw(screen)
        if player_two:
            player_two.draw(screen)
        if enemy_ai:
            enemy_ai.draw(screen)

        # HUD
        hud_y = int(screen_height * 0.03)
        hud_y2 = int(screen_height * 0.08)
        hud_y3 = int(screen_height * 0.13)

        if player_two:
            draw_label_with_panel(screen, score_font,
                                  f"P1 (Arrows): {score}",
                                  int(screen_width * 0.02), hud_y)
            draw_label_with_panel(screen, score_font,
                                  f"P2 (WASD): {score_two}",
                                  int(screen_width * 0.02), hud_y2)
            # Show active power-ups for P1
            _draw_powerup_hud(screen, score_font, active_powerups_p1,
                              int(screen_width * 0.02), hud_y3, prefix="P1")
            # P2 power-ups on the right
            _draw_powerup_hud(screen, score_font, active_powerups_p2,
                              int(screen_width * 0.55), hud_y, prefix="P2")
        else:
            if time_limit_ms is not None:
                elapsed   = pygame.time.get_ticks() - start_time
                remaining = max(0, time_limit_ms - elapsed) / 1000
                draw_label_with_panel(screen, score_font,
                                      f"Time: {remaining:.1f}s",
                                      int(screen_width * 0.02), hud_y)
                draw_label_with_panel(screen, score_font,
                                      f"Score: {score}",
                                      int(screen_width * 0.02), hud_y2)
            else:
                draw_label_with_panel(screen, score_font,
                                      f"Score: {score}",
                                      int(screen_width * 0.02), hud_y)
            draw_label_with_panel(screen, score_font,
                                  "Use Arrow Keys to Move",
                                  int(screen_width * 0.02), hud_y2 + (score_font.get_height() + 8) if time_limit_ms is None else hud_y3)
            _draw_powerup_hud(screen, score_font, active_powerups_p1,
                              int(screen_width * 0.02), hud_y2 if time_limit_ms is None else hud_y3,
                              prefix="")

        # ── Game-over overlay ─────────────────────────────────────────────────
        if game_over == "displayed":
            go_text = "Game Over" if not winner else f"{winner} wins!"
            go_surf    = game_over_font.render(go_text, True, TEXT_COLOR)
            go_outline = game_over_font.render(go_text, True, TEXT_OUTLINE_COLOR)
            gx = screen_width  // 2 - go_surf.get_width()  // 2
            gy = screen_height // 2 - int(screen_height * 0.1)
            for dx in (-2, 0, 2):
                for dy in (-2, 0, 2):
                    if dx != 0 or dy != 0:
                        screen.blit(go_outline, (gx + dx, gy + dy))
            screen.blit(go_surf, (gx, gy))

            rs = restart_font.render("Press SPACE to restart", True, TEXT_COLOR)
            ro = restart_font.render("Press SPACE to restart", True, TEXT_OUTLINE_COLOR)
            rx = screen_width  // 2 - rs.get_width()  // 2
            ry = screen_height // 2 + int(screen_height * 0.05)
            for dx in (-2, 0, 2):
                for dy in (-2, 0, 2):
                    if dx != 0 or dy != 0:
                        screen.blit(ro, (rx + dx, ry + dy))
            screen.blit(rs, (rx, ry))

        pygame.display.flip()
        clock.tick(60)

    return "menu"


def _draw_powerup_hud(screen, font, active_list, x, y, prefix=""):
    """Draw active power-up timers on screen."""
    offset = 0
    for apu in active_list:
        if apu.is_active():
            t = apu.get_remaining_time()
            name = POWERUP_TYPES[apu.powerup_type]["name"]
            color = POWERUP_TYPES[apu.powerup_type]["color"]
            label = f"{prefix+' ' if prefix else ''}{name}: {t:.1f}s"
            surf = font.render(label, True, color)
            # small shadow
            shadow = font.render(label, True, (0, 0, 0))
            screen.blit(shadow, (x + 1, y + offset + 1))
            screen.blit(surf,   (x,     y + offset))
            offset += surf.get_height() + 4


def draw_label(screen, font, text, x, y):
    screen.blit(font.render(text, True, TEXT_COLOR), (x, y))


def show_play_menu(screen, clock, font, big_font, profile_data):
    options = ["Solo", "Play with friend (Duo)", "Time Limited"]
    selected = 0

    while True:
        screen_width  = screen.get_width()
        screen_height = screen.get_height()

        title_font_dyn = get_font(max(36, min(64, int(screen_height * 0.12))))
        menu_font      = get_font(max(20, min(32, int(screen_height * 0.07))))
        hint_font      = get_font(max(14, min(24, int(screen_height * 0.05))))
        button_font    = get_font(max(14, min(24, int(screen_height * 0.05))))

        back_button_width  = max(100, int(screen_width * 0.15))
        back_button_height = max(35,  int(screen_height * 0.08))
        back_rect = pygame.Rect(int(screen_width * 0.05),
                                screen_height - back_button_height - 20,
                                back_button_width, back_button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                nw = max(event.size[0], MIN_SCREEN_WIDTH)
                nh = max(event.size[1], MIN_SCREEN_HEIGHT)
                screen = pygame.display.set_mode((nw, nh), pygame.RESIZABLE)
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
                        return run_match(screen, clock, font, big_font, profile_data,
                                         "time_limited", time_limit_ms=time_limit_ms)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

        paint_arena(screen, profile_data)

        title = title_font_dyn.render("Play", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(screen_width // 2, int(screen_height * 0.15))))

        panel_top    = int(screen_height * 0.25)
        panel_bottom = int(screen_height * 0.75)
        panel_width  = screen_width - int(screen_width * 0.20)
        panel_x      = (screen_width - panel_width) // 2
        panel_height = panel_bottom - panel_top
        draw_transparent_panel(screen, panel_x, panel_top, panel_width, panel_height, radius=20)

        option_y_start = panel_top + int(panel_height * 0.12)
        option_spacing = int(panel_height * 0.22)
        for idx, label in enumerate(options):
            color      = (255, 255, 255) if idx == selected else (180, 180, 180)
            label_surf = menu_font.render(label, True, color)
            label_x    = panel_x + (panel_width - label_surf.get_width()) // 2
            screen.blit(label_surf, (label_x, option_y_start + idx * option_spacing))

        # Duo hint
        if selected == 1:
            hint = hint_font.render("P1: Arrow keys   P2: WASD", True, (200, 200, 220))
            screen.blit(hint, (panel_x + (panel_width - hint.get_width()) // 2,
                                option_y_start + len(options) * option_spacing + 8))

        if selected == 2:
            hint = hint_font.render("Select a time limit and press ENTER.", True, (200, 200, 220))
            screen.blit(hint, (panel_x + (panel_width - hint.get_width()) // 2,
                                option_y_start + len(options) * option_spacing + 8))

        pygame.draw.rect(screen, (70, 130, 180), back_rect, border_radius=20)
        back_label = button_font.render("Back", True, (255, 255, 255))
        screen.blit(back_label, back_label.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(60)