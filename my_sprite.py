import pygame
import imagelist
import time

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class MySprite(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, images, screen):
        super().__init__()
        valid = False
        
        if x >= 0 and x <= SCREEN_WIDTH:
            valid = True
        
        if not valid:
            print("Invalid. Please Quit.")
            exit(0)
        
        self._screen = screen
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._xd = 0
        self._yd = 0
        self._images = images
        self._screen = screen

        # Set default frame
        self._current_frame = 10
        self._start_frame = 10
        self._end_frame = 10
        self._delay = 10
        self._repeat = False

    # Internal get/set function
    def get_x(self):
        return self._x

    def set_x(self, x):
        if x >= 0 and x <= SCREEN_WIDTH:
            self._x = x
        elif x < 0:
            self._x = 0
        else:
            self._x = SCREEN_WIDTH

    def get_y(self):
        return self._y

    def set_y(self, y):
        if y >= 0 and y <= SCREEN_HEIGHT:
            self._y = y
        elif y < 0:
            self._y = 0
        else:
            self._y = SCREEN_HEIGHT

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
        if isinstance(other_rect, pygame.Rect):
            if not (self._x + self._w < other_rect.x or \
                    self._y + self._h < other_rect.y or \
                    self._x > other_rect.x + other_rect.width or \
                    self._y > other_rect.y + other_rect.height):
                return True
            else:
                return False
        else:
            return False

    def set_animation(self, start_frame=0, end_frame=0, delay=0, repeat=-1):
        if start_frame >= 0 and start_frame < len(self._images.images):
            self._start_frame = start_frame
        if end_frame >= 0 and end_frame < len(self._images.images) and start_frame <= end_frame:
            self._end_frame = end_frame
        if delay > 0:
            self._delay = delay
        if repeat:
            self._repeat = True
        else:
            self._repeat = False

        self._next_frame = time.time() + delay

    def animate(self, reset_animation=False):
        if self._delay != -1:
            # If we're resetting
            if reset_animation == True:
                self._current_frame = self._start_frame
            else:
                if time.time() > self._next_frame:
                    if self._current_frame == self._end_frame:
                        if self._repeat == True:
                            self._current_frame = self._start_frame
                        else:
                            self._current_frame += 1
                    else:
                        self._current_frame += 1

            self._next_frame = self._next_frame + self._delay

    def draw(self):
        if self._current_frame < len(self._images.images):
            self._screen.blit(self._images.images[self._current_frame], self.get_rect())


if __name__ == "__main__":
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480

    pygame.init()

    screen=pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Testing the MySprite Class')

    image_obj = imagelist("images\\apple", 20, 20,"png")

    # loop while not quitting
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
    pygame.quit()
