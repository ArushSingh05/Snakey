import pygame
import time
import math
import random
from imagelist import ImageList

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20


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
        self._x = max(0, min(x, self._screen.get_width()))

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = max(0, min(y, self._screen.get_height()))

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


BASE_HEAD_RADIUS = 11
BASE_BODY_RADIUS = 9
BASE_FOOD_RADIUS = 8
FOOD_COLOR = (250, 190, 45)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def get_scale_factor(screen):
    width_scale = screen.get_width() / SCREEN_WIDTH
    height_scale = screen.get_height() / SCREEN_HEIGHT
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
        return max(5, int(self.base_head_radius * get_scale_factor(self.screen)))

    @property
    def body_radius(self):
        return max(4, int(self.base_body_radius * get_scale_factor(self.screen)))

    def wrap(self, x, y):
        w = self.screen.get_width()
        h = self.screen.get_height()
        if x < 0: x += w
        elif x > w: x -= w
        if y < 0: y += h
        elif y > h: y -= h
        return x, y

    def update(self, direction, accelerate, settings):
        self.direction = direction or self.direction
        # Fixed moderate speed – acceleration setting removed
        self.speed += -0.05 if not accelerate else 0.0
        self.speed = clamp(self.speed, self.min_speed, self.max_speed)
        scaled_speed = self.speed * get_scale_factor(self.screen)
        head_x, head_y = self.points[-1]
        new_head = self.wrap(head_x + self.direction[0] * scaled_speed,
                             head_y + self.direction[1] * scaled_speed)
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
        collision_dist = (self.head_radius + self.body_radius) ** 2
        for point in self.points[20:-20]:
            px, py = point
            if (head_x - px) ** 2 + (head_y - py) ** 2 < collision_dist:
                return True
        return False

    def check_food_collision(self, item):
        head_x, head_y = self.head_position()
        fx, fy = item.pos if hasattr(item, 'pos') else (item.x, item.y)
        return (head_x - fx) ** 2 + (head_y - fy) ** 2 < (self.head_radius + item.radius) ** 2

    def check_collision_with_segments(self, segments):
        head_x, head_y = self.head_position()
        collision_dist = (self.head_radius + self.body_radius - 2) ** 2
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
        return max(4, int(self.base_radius * get_scale_factor(self.screen)))

    def respawn(self):
        w = self.screen.get_width()
        h = self.screen.get_height()
        self.pos = (
            random.randint(self.radius + 20, w - self.radius - 20),
            random.randint(self.radius + 20, h - self.radius - 20),
        )

    def draw(self, screen):
        pygame.draw.circle(screen, FOOD_COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius)


# ─────────────────────────────────────────────────────────────────────────────
#  AGGRESSIVE ENEMY AI  –  reactive, goal-driven, slither.io-style
# ─────────────────────────────────────────────────────────────────────────────

CARDINALS = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]
LOOKAHEAD_STEPS = 8   # how many frames ahead to simulate per direction


class EnemyAI(Snake):
    """
    Every frame the AI:
      1. Scores every possible goal (food, powerups, player intercept, encircle)
         and picks the highest-value one.
      2. Scores all 4 cardinal directions against that goal using lookahead
         that penalises its own body but NOT the player body when hunting.
      3. Picks the safest direction that makes progress toward the goal.

    Danger avoidance is separate from goal selection: the AI always avoids its
    own body regardless of mode, but only avoids the player's body when it is
    in FOOD/GROW mode (small / far away). When hunting it charges through.
    """

    MODE_GROW  = "grow"   # eat food/powerups to get bigger
    MODE_HUNT  = "hunt"   # intercept / cut off the player
    MODE_TRAP  = "trap"   # circle ahead of the player to create a wall

    def __init__(self, x, y, screen, target_snake, settings=None):
        super().__init__(x, y, (200, 50, 50), (255, 120, 120), screen)
        self.target    = target_snake
        self.settings  = settings or {}
        self.speed     = 4.8
        self.max_speed = 7.5
        self.min_speed = 3.5
        self._foods    = []   # set from play.py
        self.powerups  = []   # set from play.py

        self._mode         = self.MODE_GROW
        self._frame        = 0
        self._circle_side  = 1   # flips to alternate trap side
        self._trap_flipped = 0   # frame when last flipped

    # ── main update (called every frame) ────────────────────────────────────

    # Pixels the AI must travel before being allowed to make a 90° turn.
    # Smaller = tighter/faster turns (player feel is ~12-16 px).
    _TURN_INTERVAL   = 14
    _dist_since_turn = 0.0

    def update(self, direction=None, accelerate=False, settings=None):
        self._frame += 1
        self._mode = self._choose_mode()

        scale = get_scale_factor(self.screen)
        self._dist_since_turn += self.speed * scale

        # Only commit a new direction once we've travelled _TURN_INTERVAL px
        if self._dist_since_turn >= self._TURN_INTERVAL:
            new_dir = self._decide_direction()
            if new_dir and new_dir != self.direction:
                is_reverse = (new_dir[0] == -self.direction[0] and
                              new_dir[1] == -self.direction[1])
                if not is_reverse:
                    self.direction = new_dir
                    self._dist_since_turn = 0.0

        # Pass current (cardinal) direction into base Snake.update
        super().update(self.direction, False, settings or self.settings)

    # ── mode selection ───────────────────────────────────────────────────────

    def _choose_mode(self):
        if self.target is None or self.target.dead:
            return self.MODE_GROW

        my_head = self.head_position()
        ph      = self.target.head_position()
        dist    = math.hypot(ph[0] - my_head[0], ph[1] - my_head[1])
        ai_len  = len(self.points)
        pl_len  = len(self.target.points)

        # Grow priority: always grab powerups or food if very close (<120 px),
        # regardless of mode, by boosting their score in _pick_goal.
        # Mode just determines the secondary objective.

        if dist < 280 and ai_len >= pl_len * 0.7:
            return self.MODE_TRAP   # close + big enough → try to wall them in
        elif dist < 450:
            return self.MODE_HUNT   # medium range → intercept
        else:
            return self.MODE_GROW   # far away → eat and grow

    # ── goal picking ─────────────────────────────────────────────────────────

    def _pick_goal(self):
        """
        Return the single best (x, y) target point this frame.
        Scores: nearby powerup > nearby food > hunt intercept / trap point.
        """
        my_head = self.head_position()
        w = self.screen.get_width()
        h = self.screen.get_height()

        best_score = -1e9
        best_pos   = (w // 2, h // 2)

        # ── Food ────────────────────────────────────────────────────────────
        for food in self._foods:
            d = math.hypot(food.pos[0] - my_head[0], food.pos[1] - my_head[1])
            # Value decays with distance; always worth chasing
            score = 800 - d * 0.8
            if score > best_score:
                best_score = score
                best_pos   = food.pos

        # ── Powerups (high value – worth detour) ────────────────────────────
        for pu in self.powerups:
            if not getattr(pu, 'active', False) or getattr(pu, 'collected', True):
                continue
            d = math.hypot(pu.x - my_head[0], pu.y - my_head[1])
            score = 1200 - d * 0.8   # powerups score higher than food
            if score > best_score:
                best_score = score
                best_pos   = (pu.x, pu.y)

        # ── Player-based goals (hunt / trap) – only compete if no item is very close
        if self.target and not self.target.dead:
            ph = self.target.head_position()
            d_player = math.hypot(ph[0] - my_head[0], ph[1] - my_head[1])

            if self._mode == self.MODE_HUNT:
                # Intercept: predict player position N frames ahead
                intercept = self._intercept_point(frames_ahead=18)
                # Score: valuable when close, very valuable when we're bigger
                size_bonus = 300 if len(self.points) >= len(self.target.points) * 0.9 else 0
                score = 600 + size_bonus - d_player * 0.3
                if score > best_score:
                    best_score = score
                    best_pos   = intercept

            elif self._mode == self.MODE_TRAP:
                # Trap: aim ahead-and-to-the-side of player to build a wall
                trap = self._trap_point()
                score = 900 - d_player * 0.2   # trapping is top priority when close
                if score > best_score:
                    best_score = score
                    best_pos   = trap

        return best_pos

    # ── goal helpers ────────────────────────────────────────────────────────

    def _intercept_point(self, frames_ahead=18):
        px, py   = self.target.head_position()
        pdx, pdy = self.target.direction
        spd      = self.target.speed * get_scale_factor(self.screen)
        pred_x   = (px + pdx * spd * frames_ahead) % self.screen.get_width()
        pred_y   = (py + pdy * spd * frames_ahead) % self.screen.get_height()
        return (pred_x, pred_y)

    def _trap_point(self):
        """
        Aim for a point perpendicular to the player's direction of travel,
        ahead of them, to place our body as a wall.
        """
        px, py   = self.target.head_position()
        pdx, pdy = self.target.direction
        # Flip which side we circle every ~2.5 s to tighten the spiral
        if self._frame - self._trap_flipped > 150:
            self._circle_side  *= -1
            self._trap_flipped  = self._frame
        perp_x = -pdy * self._circle_side
        perp_y =  pdx * self._circle_side
        goal_x = px + pdx * 100 + perp_x * 130
        goal_y = py + pdy * 100 + perp_y * 130
        goal_x = clamp(goal_x, 30, self.screen.get_width()  - 30)
        goal_y = clamp(goal_y, 30, self.screen.get_height() - 30)
        return (goal_x, goal_y)

    # ── direction decision ───────────────────────────────────────────────────

    def _decide_direction(self):
        goal    = self._pick_goal()
        reverse = (-self.direction[0], -self.direction[1])

        # Score all 4 directions; exclude reverse unless totally stuck
        scored = []
        for d in CARDINALS:
            if d == reverse:
                continue
            s = self._score_direction(d, goal)
            scored.append((s, d))

        scored.sort(key=lambda x: -x[0])

        # Best safe direction
        if scored and scored[0][0] > -9000:
            return scored[0][1]

        # All forward directions are bad – try reverse as last resort
        s = self._score_direction(reverse, goal)
        if s > -9000:
            return reverse

        return None  # keep current direction

    # ── direction scoring (lookahead) ───────────────────────────────────────

    def _score_direction(self, d, goal):
        """
        Simulate LOOKAHEAD_STEPS frames in direction d.
        Penalties:
          - hitting own body  → large penalty, stop counting
          - hitting player body → penalty ONLY in GROW mode (self-preservation)
            In HUNT/TRAP mode we ignore player body (we WANT to be near them)
        Reward:
          - proximity of simulated final position to goal
          - number of safe steps (open space)
        """
        hx, hy = self.head_position()
        w      = self.screen.get_width()
        h      = self.screen.get_height()
        step   = max(6.0, self.speed * get_scale_factor(self.screen))

        avoid_player_body = (self._mode == self.MODE_GROW)
        safe_steps = 0

        for i in range(1, LOOKAHEAD_STEPS + 1):
            nx = (hx + d[0] * step * i) % w
            ny = (hy + d[1] * step * i) % h

            # Own body – always avoid (skip last 4 pts which will have moved)
            hit_self = False
            for pt in self.points[:-4]:
                if (pt[0] - nx) ** 2 + (pt[1] - ny) ** 2 < (self.body_radius * 1.6) ** 2:
                    hit_self = True
                    break
            if hit_self:
                return safe_steps * 12 - 800

            # Player body – only dangerous in GROW mode
            if avoid_player_body and self.target and not self.target.dead:
                hit_player = False
                for pt in self.target.points:
                    if (pt[0] - nx) ** 2 + (pt[1] - ny) ** 2 < (self.body_radius + self.target.body_radius) ** 2:
                        hit_player = True
                        break
                if hit_player:
                    return safe_steps * 12 - 400

            safe_steps += 1

        # Proximity reward: how close is the simulated final position to the goal?
        final_x = (hx + d[0] * step * LOOKAHEAD_STEPS) % w
        final_y = (hy + d[1] * step * LOOKAHEAD_STEPS) % h
        dist_to_goal = math.hypot(goal[0] - final_x, goal[1] - final_y)
        proximity = max(0, 700 - dist_to_goal)

        return safe_steps * 12 + proximity