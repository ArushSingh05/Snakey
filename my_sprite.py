import pygame
import time
from imagelist import ImageList

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


class MySprite(pygame.sprite.Sprite):
    # Base sprite class for position, movement, and animation
    
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
        # Set both x and y at once
        self.set_x(x)
        self.set_y(y)

    def move(self, x_delta=None, y_delta=None):
        # Move sprite by delta, updating velocity
        if x_delta is not None:
            self._xd = x_delta
        if y_delta is not None:
            self._yd = y_delta
        self.set_x(self._x + self._xd)
        self.set_y(self._y + self._yd)

    def get_rect(self):
        # Return bounding box rect
        return pygame.Rect(self._x, self._y, self._w, self._h)

    def collide(self, other_rect):
        # Check collision with rectangle
        return isinstance(other_rect, pygame.Rect) and self.get_rect().colliderect(other_rect)

    def set_animation(self, start_frame=0, end_frame=0, delay=0.1, repeat=True):
        # Configure animation parameters
        length = len(self._images.images)
        self._start_frame = max(0, min(start_frame, length - 1))
        self._end_frame = max(self._start_frame, min(end_frame, length - 1))
        self._delay = delay
        self._repeat = bool(repeat)
        self._current_frame = self._start_frame
        self._next_frame = time.time() + self._delay

    def animate(self, reset_animation=False):
        # Update animation frame based on elapsed time
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
        # Draw current animation frame to screen
        if 0 <= self._current_frame < len(self._images.images):
            self._screen.blit(self._images.images[self._current_frame], self.get_rect())


class Enemy(MySprite):
    # Enemy sprite that patrols back and forth
    
    def __init__(self, x, y, w, h, image_prefix, screen, count=4, extension="png"):
        images = ImageList(image_prefix, w, h, extension)
        super().__init__(x, y, w, h, images, screen)
        self.direction = 1  # 1 for right, -1 for left
        self.set_animation(0, max(0, len(images.images) - 1), 0.2, repeat=True)

    def patrol(self):
        # Move horizontally and reverse at edges
        screen_width = self._screen.get_width()
        self.move(self.direction * 2, 0)
        if self._x <= 0 or self._x + self._w >= screen_width:
            self.direction *= -1

    def update(self):
        # Update position and animation
        self.patrol()
        self.animate()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Testing MySprite")

    image_obj = ImageList("images/test/test", 64, 64, "png")
    enemy = Enemy(100, 100, 64, 64, "images/test/test", screen, extension="png")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 30))
        enemy.update()
        enemy.draw()
        pygame.display.flip()
    pygame.quit()
