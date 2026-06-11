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

BASE_HEAD_RADIUS = 11
BASE_BODY_RADIUS = 9
BASE_FOOD_RADIUS = 8


def clamp(value, minimum, maximum):
    # Keep value within min/max range
    return max(minimum, min(value, maximum))


def is_opposite(direction_a, direction_b):
    # Check if directions are 180 degrees apart
    return direction_a[0] == -direction_b[0] and direction_a[1] == -direction_b[1]


def get_scale_factor(screen):
    # Calculate scale factor based on screen size
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    width_scale = screen_width / SCREEN_WIDTH
    height_scale = screen_height / SCREEN_HEIGHT
    return min(width_scale, height_scale)


class Food:
    # Food that snake eats to grow and score points
    
    def __init__(self, screen):
        self.screen = screen
        self.base_radius = BASE_FOOD_RADIUS
        self.respawn()

    @property
    def radius(self):
        scale = get_scale_factor(self.screen)
        return max(4, int(self.base_radius * scale))

    def respawn(self):
        # Place food at random location inside boundaries
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.pos = (
            random.randint(self.radius + 20, screen_width - self.radius - 20),
            random.randint(self.radius + 20, screen_height - self.radius - 20),
        )

    def draw(self, screen):
        pygame.draw.circle(screen, FOOD_COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius)


class Snake:
    # Player snake that moves and grows by eating food
    
    def __init__(self, x, y, body_color, head_color, screen):
        self.screen = screen
        self.points = [(float(x), float(y))]
        self.direction = (1.0, 0.0)
        self.speed = 4.0
        self.target_length = 40
        self.max_speed = 7.0
        self.min_speed = 2.8
        self.base_head_radius = BASE_HEAD_RADIUS
        self.base_body_radius = BASE_BODY_RADIUS
        self.body_color = body_color
        self.head_color = head_color
        self.dead = False

    @property
    def head_radius(self):
        scale = get_scale_factor(self.screen)
        return max(5, int(self.base_head_radius * scale))

    @property
    def body_radius(self):
        scale = get_scale_factor(self.screen)
        return max(4, int(self.base_body_radius * scale))

    def wrap(self, x, y):
        # Wrap coordinates around screen edges
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        if x < 0:
            x += screen_width
        elif x > screen_width:
            x -= screen_width

        if y < 0:
            y += screen_height
        elif y > screen_height:
            y -= screen_height

        return x, y

    def update(self, direction, accelerate, settings):
        # Move snake and manage body segments
        self.direction = direction or self.direction
        accel_rate = settings.get("acceleration_rate", 0.08)
        self.speed += accel_rate if accelerate else -0.05
        self.speed = clamp(self.speed, self.min_speed, self.max_speed)

        head_x, head_y = self.points[-1]
        dx = self.direction[0] * self.speed
        dy = self.direction[1] * self.speed
        new_head = self.wrap(head_x + dx, head_y + dy)
        self.points.append(new_head)

        if len(self.points) > self.target_length:
            self.points.pop(0)

    def grow(self, amount):
        # Increase target body length
        self.target_length += amount

    def draw(self, screen):
        # Render snake body and head as circles
        total = len(self.points)
        for index, point in enumerate(self.points):
            x, y = int(point[0]), int(point[1])
            if index == total - 1:
                pygame.draw.circle(screen, self.head_color, (x, y), self.head_radius)
            else:
                pygame.draw.circle(screen, self.body_color, (x, y), self.body_radius)

    def head_position(self):
        return self.points[-1]

    def check_self_collision(self):
        # Check if head collides with body (skip tail buffer)
        head_x, head_y = self.head_position()
        head_radius = self.head_radius
        body_radius = self.body_radius
        collision_dist = (head_radius + body_radius) ** 2
        
        for point in self.points[20:-20]:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < collision_dist:
                return True
        return False

    def check_food_collision(self, food):
        # Check if head overlaps with food
        head_x, head_y = self.head_position()
        head_radius = self.head_radius
        food_radius = food.radius
        fx, fy = food.pos
        return (head_x - fx) ** 2 + (head_y - fy) ** 2 < (head_radius + food_radius) ** 2

    def check_collision_with_segments(self, segments):
        # Check if head collides with opponent snake
        head_x, head_y = self.head_position()
        head_radius = self.head_radius
        body_radius = self.body_radius
        collision_dist = (head_radius + body_radius - 2) ** 2
        
        for point in segments:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < collision_dist:
                return True
        return False


def paint_arena(screen, profile_data):
    # Draw arena background with image or fallback color
    if not ARENA_OPTIONS:
        screen.fill((30, 30, 30))
        return
    
    custom = profile_data.get("customization", {})
    arena_index = custom.get("arena_index", 0) % len(ARENA_OPTIONS)
    arena = ARENA_OPTIONS[arena_index]
    image = arena.get("image")
    
    if image:
        scaled_image = pygame.transform.scale(image, screen.get_size())
        screen.blit(scaled_image, (0, 0))
    else:
        color = arena.get("color", (30, 30, 30))
        screen.fill(color)


def run_match(screen, clock, font, big_font, profile_data, mode):
    # Main game loop for solo or duo mode
    custom = profile_data.get("customization", {})
    skin_index = custom.get("skin_index", 0) % len(SKIN_OPTIONS)
    skin = SKIN_OPTIONS[skin_index]
    settings = profile_data.get("settings", {})

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    snake = Snake(screen_width / 4, screen_height / 2, skin["body"], skin["head"], screen)
    score = 0
    food = Food(screen)
    player_two = None
    score_two = 0
    winner = None

    if mode == "duo":
        player_two = Snake(3 * screen_width / 4, screen_height / 2, (240, 110, 110), (255, 170, 170), screen)

    hazard = Enemy(100, 120, 64, 64, "images/enemy/test", screen, extension="jpg")

    game_over = False
    running = True

    while running:
        direction_one = snake.direction
        accelerate_one = False
        direction_two = player_two.direction if player_two else None
        accelerate_two = False

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

            hazard.update()
            head_x = int(snake.head_position()[0])
            head_y = int(snake.head_position()[1])
            head_radius = snake.head_radius

            if hazard.get_rect().colliderect(pygame.Rect(head_x - head_radius, head_y - head_radius, head_radius * 2, head_radius * 2)):
                game_over = True
                winner = "Player 2" if player_two else None
            if player_two:
                head_x_p2 = int(player_two.head_position()[0])
                head_y_p2 = int(player_two.head_position()[1])
                head_radius_p2 = player_two.head_radius
                
                if hazard.get_rect().colliderect(pygame.Rect(head_x_p2 - head_radius_p2, head_y_p2 - head_radius_p2, head_radius_p2 * 2, head_radius_p2 * 2)):
                    game_over = True
                    winner = "Player 1"

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

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        if player_two:
            draw_label(screen, font, f"P1: {score}", 24, 24)
            draw_label(screen, font, f"P2: {score_two}", 24, 54)
        else:
            draw_label(screen, font, f"Score: {score}", 24, 24)
        draw_label(screen, font, f"Press ESC to return", 24, screen_height - 40)

        if game_over:
            game_over_text = "Game Over"
            if winner:
                game_over_text = f"{winner} wins!"
            screen.blit(big_font.render(game_over_text, True, TEXT_COLOR), (screen_width / 2 - 180, screen_height / 2 - 40))
            screen.blit(font.render("Press SPACE to restart", True, TEXT_COLOR), (screen_width / 2 - 130, screen_height / 2 + 20))

        pygame.display.flip()
        clock.tick(60)

    return "menu"


def draw_label(screen, font, text, x, y):
    # Draw text label at position
    screen.blit(font.render(text, True, TEXT_COLOR), (x, y))


def show_play_menu(screen, clock, font, big_font, profile_data):
    # Menu to select solo or duo mode
    options = ["Solo", "Play with friend"]
    selected = 0

    while True:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
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
        screen.blit(title, title.get_rect(center=(screen_width / 2, 100)))

        for idx, label in enumerate(options):
            color = (255, 255, 255) if idx == selected else (180, 180, 180)
            screen.blit(font.render(label, True, color), (screen_width / 2 - 90, 220 + idx * 70))

        hint = font.render("Use UP/DOWN and ENTER. ESC to go back.", True, (190, 190, 190))
        screen.blit(hint, (screen_width / 2 - 190, screen_height - 90))

        pygame.display.flip()
        clock.tick(60)
