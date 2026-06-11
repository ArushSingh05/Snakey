import pygame
from os.path import exists

class ImageList:
    # Loads numbered image files and scales them for consistent rendering

    def __init__(self, filename, width, height, extension="png"):
        # filename: path prefix, width/height: target dimensions
        self._images = []
        count = 0
        while exists(f"{filename}{count}.{extension}"):
            image = pygame.image.load(f"{filename}{count}.{extension}")
            scaled = pygame.transform.smoothscale(image, (width, height))
            self._images.append(scaled)
            count += 1

    @property
    def images(self):
        # Returns list of loaded and scaled images
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
