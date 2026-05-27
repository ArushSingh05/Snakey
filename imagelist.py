import pygame
from os.path import exists

class ImageList:
    """
    Loads a sequence of numbered image files and provides them as an accessible list.
    Automatically scales all images to the specified dimensions for consistent sprite rendering.
    Useful for loading animation frame sequences like "sprite0.png", "sprite1.png", etc.
    """

    def __init__(self, filename, width, height, extension="png"):
        """
        Initialize ImageList by loading a sequence of numbered image files.
        Searches for files named like: filename0.ext, filename1.ext, filename2.ext, etc.
        
        Args:
            filename: The path and prefix for image files (without number or extension)
            width: Target width to scale all images to
            height: Target height to scale all images to
            extension: File extension to look for (default: "png")
        """
        self._images = []
        count = 0
        while exists(f"{filename}{count}.{extension}"):
            image = pygame.image.load(f"{filename}{count}.{extension}")
            scaled = pygame.transform.smoothscale(image, (width, height))
            self._images.append(scaled)
            count += 1

    @property
    def images(self):
        """
        Get the list of loaded and scaled images.
        
        Returns:
            List of pygame.Surface objects containing the loaded images
        """
        return self._images


if __name__ == "__main__":
    SCR_X = 640
    SCR_Y = 480
    TEST_X = 50
    TEST_Y = 50
    TEST_W = 64
    TEST_H = 64
    TEST_FILES = "images/test/test"

    image_obj = ImageList(TEST_FILES, TEST_W, TEST_H, "png")

    pygame.init()
    screen = pygame.display.set_mode((SCR_X, SCR_Y), pygame.RESIZABLE)
    quitting = False
    while not quitting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitting = True

        screen.fill((18, 20, 30))
        for count, image in enumerate(image_obj.images):
            image_rect = pygame.Rect(TEST_X + (count * (TEST_W + 10)), TEST_Y, TEST_W, TEST_H)
            screen.blit(image, image_rect)
        pygame.display.flip()

    pygame.quit()
