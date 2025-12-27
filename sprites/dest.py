import pygame
import settings

class Destination(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 紅色 32x64 矩形
        self.image = pygame.Surface((32, 64))
        self.image.fill((255, 0, 0))  # 紅色
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args, **kwargs):
        pass