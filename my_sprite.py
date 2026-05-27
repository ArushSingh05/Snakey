import pygame
import time
from imagelist import ImageList

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


class MySprite(pygame.sprite.Sprite):
    """
    Base sprite class that handles position, movement, animation, and rendering.
    Inherits from pygame.sprite.Sprite to leverage Pygame's sprite functionality.
    Provides properties for position, movement, and frame-based animation.
    """
    
    def __init__(self, x, y, w, h, images, screen):
        """
        Initialize a sprite at the given position with animation support.
        
        Args:
            x: Initial x position of the sprite
            y: Initial y position of the sprite
            w: Width of the sprite
            h: Height of the sprite
            images: ImageList object containing animation frames
            screen: The pygame display surface
            
        Raises:
            ValueError: If sprite position is outside screen boundaries
        """
        super().__init__()
        if x < 0 or x > SCREEN_WIDTH or y < 0 or y > SCREEN_HEIGHT:
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
        """
        Get the current x position.
        
        Returns:
            The x coordinate of the sprite
        """
        return self._x

    def set_x(self, x):
        """
        Set the x position, clamping to screen boundaries.
        
        Args:
            x: The new x coordinate
        """
        self._x = max(0, min(x, SCREEN_WIDTH))

    def get_y(self):
        """
        Get the current y position.
        
        Returns:
            The y coordinate of the sprite
        """
        return self._y

    def set_y(self, y):
        """
        Set the y position, clamping to screen boundaries.
        
        Args:
            y: The new y coordinate
        """
        self._y = max(0, min(y, SCREEN_HEIGHT))

    x = property(get_x, set_x)
    y = property(get_y, set_y)

    def set_pos(self, x, y):
        """
        Set both x and y position at once.
        
        Args:
            x: The new x coordinate
            y: The new y coordinate
        """
        self.set_x(x)
        self.set_y(y)

    def move(self, x_delta=None, y_delta=None):
        """
        Move the sprite by the given delta values.
        Updates internal velocity and position, clamping to screen boundaries.
        
        Args:
            x_delta: Amount to move in x direction (updates velocity if provided)
            y_delta: Amount to move in y direction (updates velocity if provided)
        """
        if x_delta is not None:
            self._xd = x_delta
        if y_delta is not None:
            self._yd = y_delta
        self.set_x(self._x + self._xd)
        self.set_y(self._y + self._yd)

    def get_rect(self):
        """
        Get a pygame Rect representing the sprite's bounding box.
        
        Returns:
            pygame.Rect object for collision detection and positioning
        """
        return pygame.Rect(self._x, self._y, self._w, self._h)

    def collide(self, other_rect):
        """
        Check if this sprite collides with the given rectangle.
        
        Args:
            other_rect: pygame.Rect object to check collision with
            
        Returns:
            True if rectangles overlap, False otherwise
        """
        return isinstance(other_rect, pygame.Rect) and self.get_rect().colliderect(other_rect)

    def set_animation(self, start_frame=0, end_frame=0, delay=0.1, repeat=True):
        """
        Set up animation parameters for frame-based animation.
        Defines which frames to play and at what speed.
        
        Args:
            start_frame: Index of the first frame to animate
            end_frame: Index of the last frame to animate
            delay: Seconds between frame updates
            repeat: Whether to loop the animation
        """
        length = len(self._images.images)
        self._start_frame = max(0, min(start_frame, length - 1))
        self._end_frame = max(self._start_frame, min(end_frame, length - 1))
        self._delay = delay
        self._repeat = bool(repeat)
        self._current_frame = self._start_frame
        self._next_frame = time.time() + self._delay

    def animate(self, reset_animation=False):
        """
        Update animation frame based on elapsed time.
        Advances to the next frame when enough time has passed.
        
        Args:
            reset_animation: If True, resets animation to start frame
        """
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
        """
        Draw the current animation frame onto the screen.
        Only draws if the current frame index is valid.
        """
        if 0 <= self._current_frame < len(self._images.images):
            self._screen.blit(self._images.images[self._current_frame], self.get_rect())


class Enemy(MySprite):
    """
    Enemy sprite subclass that patrols back and forth across the screen.
    Inherits animation and movement functionality from MySprite.
    Reverses direction when reaching screen edges.
    """
    
    def __init__(self, x, y, w, h, image_prefix, screen, count=4, extension="png"):
        """
        Initialize an enemy sprite that loads images and sets up patrol behavior.
        
        Args:
            x: Initial x position
            y: Initial y position
            w: Width of the sprite
            h: Height of the sprite
            image_prefix: Path prefix for loading animation frames
            screen: The pygame display surface
            count: Number of animation frames to load (deprecated, loads all available)
            extension: File extension for animation frames (default: "png")
        """
        images = ImageList(image_prefix, w, h, extension)
        super().__init__(x, y, w, h, images, screen)
        self.direction = 1  # 1 for right, -1 for left
        self.set_animation(0, max(0, len(images.images) - 1), 0.2, repeat=True)

    def patrol(self):
        """
        Move the enemy back and forth horizontally.
        Reverses direction when reaching the screen edges.
        """
        self.move(self.direction * 2, 0)
        if self._x <= 0 or self._x + self._w >= SCREEN_WIDTH:
            self.direction *= -1

    def update(self):
        """
        Update the enemy sprite by moving it and advancing animation.
        Call this every game frame to update the enemy.
        """
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
