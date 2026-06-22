import pygame
import time
import math
import random
from imagelist import ImageList

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


class MySprite(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, images, screen):
        super().__init__()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if x < 0 or x > screen_width or y < 0 or y > screen_height:
            raise ValueError("Sprite position is out of range")
        self._screen = screen
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._xd = 0
        self._yd = 0
        self._images = images
        self._current_frame = 0
        self._start_frame = 0
        self._end_frame = 0
        self._delay = 0.1
        self._repeat = False
        self._next_frame = time.time() + self._delay

    def get_x(self):
        return self._x

    def set_x(self, x):
        screen_width = self._screen.get_width()
        self._x = max(0, min(x, screen_width))

    def get_y(self):
        return self._y

    def set_y(self, y):
        screen_height = self._screen.get_height()
        self._y = max(0, min(y, screen_height))

    x = property(get_x, set_x)
    y = property(get_y, set_y)

    def set_pos(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def move(self, x_delta=None, y_delta=None):
        if x_delta is not None:
            self._xd = x_delta
        if y_delta is not None:
            self._yd = y_delta
        self.set_x(self._x + self._xd)
        self.set_y(self._y + self._yd)

    def get_rect(self):
        return pygame.Rect(self._x, self._y, self._w, self._h)

    def collide(self, other_rect):
        return isinstance(other_rect, pygame.Rect) and self.get_rect().colliderect(other_rect)

    def set_animation(self, start_frame=0, end_frame=0, delay=0.1, repeat=True):
        length = len(self._images.images)
        self._start_frame = max(0, min(start_frame, length - 1))
        self._end_frame = max(self._start_frame, min(end_frame, length - 1))
        self._delay = delay
        self._repeat = bool(repeat)
        self._current_frame = self._start_frame
        self._next_frame = time.time() + self._delay

    def animate(self, reset_animation=False):
        if self._delay <= 0:
            return
        if reset_animation:
            self._current_frame = self._start_frame
            self._next_frame = time.time() + self._delay
            return
        if time.time() >= self._next_frame:
            if self._current_frame >= self._end_frame:
                if self._repeat:
                    self._current_frame = self._start_frame
                else:
                    self._current_frame = self._end_frame
            else:
                self._current_frame += 1
            self._next_frame = time.time() + self._delay

    def draw(self):
        if 0 <= self._current_frame < len(self._images.images):
            self._screen.blit(self._images.images[self._current_frame], self.get_rect())


class Enemy(MySprite):
    def __init__(self, x, y, w, h, image_prefix, screen, count=4, extension="png"):
        images = ImageList(image_prefix, w, h, extension)
        super().__init__(x, y, w, h, images, screen)
        self.direction = 1

    def patrol(self):
        screen_width = self._screen.get_width()
        self.move(self.direction * 2, 0)
        if self._x <= 0 or self._x + self._w >= screen_width:
            self.direction *= -1

    def update(self):
        self.patrol()
        self.animate()


#Snake & Food (from play.py)
BASE_HEAD_RADIUS = 11
BASE_BODY_RADIUS = 9
BASE_FOOD_RADIUS = 8
FOOD_COLOR = (250, 190, 45)

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def get_scale_factor(screen):
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    width_scale = screen_width / SCREEN_WIDTH
    height_scale = screen_height / SCREEN_HEIGHT
    return min(width_scale, height_scale)


class Snake:
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
        self.direction = direction or self.direction
        accel_rate = settings.get("acceleration_rate", 0.08)
        self.speed += accel_rate if accelerate else -0.05
        self.speed = clamp(self.speed, self.min_speed, self.max_speed)
        scale = get_scale_factor(self.screen)
        scaled_speed = self.speed * scale
        head_x, head_y = self.points[-1]
        dx = self.direction[0] * scaled_speed
        dy = self.direction[1] * scaled_speed
        new_head = self.wrap(head_x + dx, head_y + dy)
        self.points.append(new_head)
        if len(self.points) > self.target_length:
            self.points.pop(0)

    def grow(self, amount):
        self.target_length += amount

    def draw(self, screen):
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
        head_x, head_y = self.head_position()
        head_radius = self.head_radius
        body_radius = self.body_radius
        collision_dist = (head_radius + body_radius) ** 2
        for point in self.points[20:-20]:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < collision_dist:
                return True
        return False

    def check_food_collision(self, item):
        head_x, head_y = self.head_position()
        head_radius = self.head_radius
        item_radius = item.radius
        if hasattr(item, 'pos'):
            fx, fy = item.pos
        else:
            fx, fy = item.x, item.y
        return (head_x - fx) ** 2 + (head_y - fy) ** 2 < (head_radius + item_radius) ** 2

    def check_collision_with_segments(self, segments):
        head_x, head_y = self.head_position()
        head_radius = self.head_radius
        body_radius = self.body_radius
        collision_dist = (head_radius + body_radius - 2) ** 2
        for point in segments:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < collision_dist:
                return True
        return False


class Food:
    def __init__(self, screen):
        self.screen = screen
        self.base_radius = BASE_FOOD_RADIUS
        self.respawn()

    @property
    def radius(self):
        scale = get_scale_factor(self.screen)
        return max(4, int(self.base_radius * scale))

    def respawn(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.pos = (
            random.randint(self.radius + 20, screen_width - self.radius - 20),
            random.randint(self.radius + 20, screen_height - self.radius - 20),
        )

    def draw(self, screen):
        pygame.draw.circle(screen, FOOD_COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius)


#Enemy AI Snake

class EnemyAI(Snake):
    """
    Aggressive AI that chases the player with fast direction updates.
    Speed is set slightly higher than the player.
    """
    def __init__(self, x, y, screen, target_snake, settings=None):
        body_color = (200, 50, 50)
        head_color = (255, 120, 120)
        super().__init__(x, y, body_color, head_color, screen)
        self.target = target_snake
        self.settings = settings or {}
        self.speed = 4.5
        self.max_speed = 7.0
        self.min_speed = 3.5
        self.direction_change_timer = 0
        self.direction_change_interval = 3

    def update(self, direction=None, accelerate=False, settings=None):
        if self.target is None or self.target.dead:
            self._wander()
            super().update(self.direction, False, settings or self.settings)
            return

        # Choose a new direction
        self.direction_change_timer -= 1
        if self.direction_change_timer <= 0:
            self._choose_direction()
            self.direction_change_timer = self.direction_change_interval

        # Update movement with the chosen direction
        super().update(self.direction, False, settings or self.settings)

    def _choose_direction(self):
        """Pick the best direction to intercept the player."""
        head = self.head_position()
        target_head = self.target.head_position()
        target_dir = self.target.direction

        # Predict the player's position a few steps ahead
        predict_steps = 8
        predict_x = target_head[0] + target_dir[0] * predict_steps * 4
        predict_y = target_head[1] + target_dir[1] * predict_steps * 4
        # Clamp to screen bounds
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        predict_x = max(0, min(predict_x, screen_w))
        predict_y = max(0, min(predict_y, screen_h))

        # Direction towards the predicted position
        dx = predict_x - head[0]
        dy = predict_y - head[1]

        # If the player is very close, just go straight
        if abs(dx) < 10 and abs(dy) < 10:
            return

        # Choose the dominant axis for 4-direction movement
        if abs(dx) > abs(dy):
            new_dir = (1.0, 0.0) if dx > 0 else (-1.0, 0.0)
        else:
            new_dir = (0.0, 1.0) if dy > 0 else (0.0, -1.0)

        # Prevent reversing direction
        if self.direction[0] == -new_dir[0] and self.direction[1] == -new_dir[1]:
            new_dir = self.direction

        # Test if this direction leads to self-collision
        head_x, head_y = self.points[-1]
        test_x = head_x + new_dir[0] * 5
        test_y = head_y + new_dir[1] * 5
        collides = False
        for point in self.points[:-1]:  # skip tail
            if (point[0] - test_x) ** 2 + (point[1] - test_y) ** 2 < (self.body_radius * 2) ** 2:
                collides = True
                break

        if not collides:
            self.direction = new_dir
            return

        # If blocked, try other directions in order of preference
        # Preferred directions: straight, left, right
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        dirs = [d for d in dirs if not (d[0] == -self.direction[0] and d[1] == -self.direction[1])]
        dirs = [d for d in dirs if not (d[0] == self.direction[0] and d[1] == self.direction[1])]
        random.shuffle(dirs)

        for d in dirs:
            test_x = head_x + d[0] * 5
            test_y = head_y + d[1] * 5
            blocked = False
            for point in self.points[:-1]:
                if (point[0] - test_x) ** 2 + (point[1] - test_y) ** 2 < (self.body_radius * 2) ** 2:
                    blocked = True
                    break
            if not blocked:
                self.direction = d
                return

    def _wander(self):
        """Random wandering when no target."""
        if random.random() < 0.05:
            dirs = [(1,0), (-1,0), (0,1), (0,-1)]
            dirs = [d for d in dirs if not (d[0] == -self.direction[0] and d[1] == -self.direction[1])]
            self.direction = random.choice(dirs)