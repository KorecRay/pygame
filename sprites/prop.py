import pygame
from settings import TILE_SIZE, resource_path


class Prop(pygame.sprite.Sprite):
    def __init__(self, x, y, prop_type):
        super().__init__()

        self.prop_type = int(prop_type)  # 1:Jump, 2:Anti-Explosion, 3:Shield, 4:Torch

        # Load static image (e.g., assets/sprites/prop_1.png)
        try:
            path = f"assets/sprites/prop_{self.prop_type}.png"
            self.image = pygame.image.load(resource_path(path)).convert_alpha()
            # Ensure size fits game settings
            if self.image.get_size() != (32, 32):
                self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            # Fallback: Draw colored square if image missing
            self.image = pygame.Surface((32, 32))
            colors = {1: (0, 255, 0), 2: (255, 100, 0), 3: (0, 100, 255), 4: (255, 255, 0)}
            self.image.fill(colors.get(self.prop_type, (200, 200, 200)))

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args, **kwargs):
        # Static props don't need update logic
        pass