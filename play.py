import math
import random
import pygame

from player_profile import save_profile_data
from customisation import SKIN_OPTIONS, ARENA_OPTIONS
from my_sprite import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOOD_COLOR = (250, 190, 45)
TEXT_COLOR = (220, 220, 220)


def clamp(value, minimum, maximum):
    """Keep a value inside a minimum/maximum range."""
    return max(minimum, min(value, maximum))


def is_opposite(direction_a, direction_b):
    """Return True if two cardinal directions are exactly opposite."""
    return direction_a[0] == -direction_b[0] and direction_a[1] == -direction_b[1]


class Food:
    def __init__(self):
        """Initialize food with a random position on the arena."""
        self.radius = 8
        self.respawn()

    def respawn(self):
        """Place food somewhere inside the screen boundaries."""
        self.pos = (
            random.randint(self.radius + 20, SCREEN_WIDTH - self.radius - 20),
            random.randint(self.radius + 20, SCREEN_HEIGHT - self.radius - 20),
        )

    def draw(self, screen):
        """Draw the food as a small circle."""
        pygame.draw.circle(screen, FOOD_COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius)


class Snake:
    def __init__(self, x, y, body_color, head_color):
        self.points = [(float(x), float(y))]
        self.direction = (1.0, 0.0)
        self.speed = 4.0
        self.target_length = 40
        self.max_speed = 7.0
        self.min_speed = 2.8
        self.head_radius = 11
        self.body_radius = 9
        self.body_color = body_color
        self.head_color = head_color
        self.dead = False

    def wrap(self, x, y):
        """Wrap coordinates around the screen when the head crosses the edge."""
        if x < 0:
            x += SCREEN_WIDTH
        elif x > SCREEN_WIDTH:
            x -= SCREEN_WIDTH

        if y < 0:
            y += SCREEN_HEIGHT
        elif y > SCREEN_HEIGHT:
            y -= SCREEN_HEIGHT

        return x, y

    def update(self, direction, accelerate, settings):
        """Move the snake in the current direction and grow the body over time."""
        self.direction = direction or self.direction
        accel_rate = settings.get("acceleration_rate", 0.08)
        self.speed += accel_rate if accelerate else -0.05
        self.speed = clamp(self.speed, self.min_speed, self.max_speed)

        head_x, head_y = self.points[-1]
        dx = self.direction[0] * self.speed
        dy = self.direction[1] * self.speed
        new_head = self.wrap(head_x + dx, head_y + dy)
        self.points.append(new_head)

        # Remove oldest body point when the snake exceeds its target length.
        if len(self.points) > self.target_length:
            self.points.pop(0)

    def grow(self, amount):
        """Increase snake length by extending the target body size."""
        self.target_length += amount

    def draw(self, screen):
        """Render the snake body and head as circles on the screen."""
        total = len(self.points)
        for index, point in enumerate(self.points):
            x, y = int(point[0]), int(point[1])
            if index == total - 1:
                pygame.draw.circle(screen, self.head_color, (x, y), self.head_radius)
            else:
                pygame.draw.circle(screen, self.body_color, (x, y), self.body_radius)

    def head_position(self):
        """Return the current head position."""
        return self.points[-1]

    def check_self_collision(self):
        head_x, head_y = self.head_position()
        for point in self.points[:-12]:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < (self.head_radius + self.body_radius) ** 2:
                return True
        return False

    def check_food_collision(self, food):
        """Return True if the snake head is overlapping the food."""
        head_x, head_y = self.head_position()
        fx, fy = food.pos
        return (head_x - fx) ** 2 + (head_y - fy) ** 2 < (self.head_radius + food.radius) ** 2

    def check_collision_with_segments(self, segments):
        """Return True when the head collides with any given body segment list."""
        head_x, head_y = self.head_position()
        for point in segments:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < (self.head_radius + self.body_radius) ** 2:
                return True
        return False


def paint_arena(screen, profile_data):
    """Paint the playing arena using the selected customization color."""
    custom = profile_data.get("customization", {})
    arena_index = custom.get("arena_index", 0) % len(ARENA_OPTIONS)
    screen.fill(ARENA_OPTIONS[arena_index]["color"])


def run_match(screen, clock, font, big_font, profile_data, mode):
    """Run a single game match in solo or duo mode."""
    custom = profile_data.get("customization", {})
    skin_index = custom.get("skin_index", 0) % len(SKIN_OPTIONS)
    skin = SKIN_OPTIONS[skin_index]
    settings = profile_data.get("settings", {})

    snake = Snake(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2, skin["body"], skin["head"])
    score = 0
    food = Food()
    player_two = None
    score_two = 0
    winner = None

    if mode == "duo":
        player_two = Snake(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2, (240, 110, 110), (255, 170, 170))

    # Use my_sprite Enemy as a moving arena hazard.
    hazard = Enemy(100, 120, 64, 64, "images/enemy/test", screen, extension="jpg")

    game_over = False
    running = True

    # Game loop for the current match.
    while running:
        direction_one = snake.direction
        accelerate_one = False
        direction_two = player_two.direction if player_two else None
        accelerate_two = False

        # Handle input events such as quitting, escaping back to menu, and restart.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_profile_data(profile_data)
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_profile_data(profile_data)
                    return "menu"
                if event.key == pygame.K_SPACE and game_over:
                    return run_match(screen, clock, font, big_font, profile_data, mode)

        # Use key state to update the direction for each player.
        keys = pygame.key.get_pressed()
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

            # Check food collisions for each snake and respawn food if eaten.
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

            # Update hazard and check for collisions with player snakes.
            hazard.update()
            if hazard.get_rect().colliderect(pygame.Rect(int(snake.head_position()[0] - snake.head_radius), int(snake.head_position()[1] - snake.head_radius), snake.head_radius * 2, snake.head_radius * 2)):
                game_over = True
                winner = "Player 2" if player_two else None
            if player_two and hazard.get_rect().colliderect(pygame.Rect(int(player_two.head_position()[0] - player_two.head_radius), int(player_two.head_position()[1] - player_two.head_radius), player_two.head_radius * 2, player_two.head_radius * 2)):
                game_over = True
                winner = "Player 1"

            # Check collisions against self and opponent.
            if snake.check_self_collision():
                game_over = True
                winner = "Player 2" if player_two else None
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

            if game_over:
                # Update profile stats on match end.
                profile_data["games_played"] = profile_data.get("games_played", 0) + 1
                profile_data["deaths"] = profile_data.get("deaths", 0) + 1
                if score > profile_data.get("high_score", 0):
                    profile_data["high_score"] = score
                if score_two > profile_data.get("high_score", 0):
                    profile_data["high_score"] = score_two
                save_profile_data(profile_data)

        paint_arena(screen, profile_data)
        food.draw(screen)
        snake.draw(screen)
        if player_two:
            player_two.draw(screen)
        hazard.draw()

        if player_two:
            draw_label(screen, font, f"P1: {score}", 24, 24)
            draw_label(screen, font, f"P2: {score_two}", 24, 54)
        else:
            draw_label(screen, font, f"Score: {score}", 24, 24)
        draw_label(screen, font, f"Press ESC to return", 24, SCREEN_HEIGHT - 40)

        if game_over:
            game_over_text = "Game Over"
            if winner:
                game_over_text = f"{winner} wins!"
            screen.blit(big_font.render(game_over_text, True, TEXT_COLOR), (SCREEN_WIDTH / 2 - 180, SCREEN_HEIGHT / 2 - 40))
            screen.blit(font.render("Press SPACE to restart", True, TEXT_COLOR), (SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 + 20))

        pygame.display.flip()
        clock.tick(60)

    return "menu"


def draw_label(screen, font, text, x, y):
    """Draw a single text label at the given position."""
    screen.blit(font.render(text, True, TEXT_COLOR), (x, y))


def show_play_menu(screen, clock, font, big_font, profile_data):
    """Display the play menu and return the selected game mode."""
    options = ["Solo", "Play with friend"]
    selected = 0

    while True:
        # Menu event loop: choose solo or local duo play.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                if event.key == pygame.K_DOWN:
                    selected = min(len(options) - 1, selected + 1)
                if event.key == pygame.K_RETURN:
                    mode = "solo" if selected == 0 else "duo"
                    return run_match(screen, clock, font, big_font, profile_data, mode)

        screen.fill((12, 18, 42))
        title = big_font.render("Play", True, (245, 245, 245))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, 100)))

        for idx, label in enumerate(options):
            color = (255, 255, 255) if idx == selected else (180, 180, 180)
            screen.blit(font.render(label, True, color), (SCREEN_WIDTH / 2 - 90, 220 + idx * 70))

        hint = font.render("Use UP/DOWN and ENTER. ESC to go back.", True, (190, 190, 190))
        screen.blit(hint, (SCREEN_WIDTH / 2 - 190, SCREEN_HEIGHT - 90))

        pygame.display.flip()
        clock.tick(60)