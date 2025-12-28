import pygame
import settings

class Destination(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 96), pygame.SRCALPHA)

        self.image.fill((255, 120, 120, 0))

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args, **kwargs):
        pass