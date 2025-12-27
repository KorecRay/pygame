import pygame
from settings import *

class LightManager:
    def __init__(self, light_radius):
        self.light_radius = light_radius
        self.light_size = light_radius * 2

        self.dark_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.light_brush = self._create_radial_gradient(self.light_radius)

    def _create_radial_gradient(self, radius):
        brush_size = radius * 2
        surface = pygame.Surface((brush_size, brush_size), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 255))
        for r in range(radius, 0, -1):
            alpha = int(255 * (r / radius))
            
            pygame.draw.circle(surface, (0, 0, 0, alpha), (radius, radius), r)
            
        return surface

    def draw(self, screen, player_rect):
        self.dark_mask.fill((0, 0, 0, 255))

        center_x, center_y = player_rect.center
        blit_x = center_x - self.light_radius
        blit_y = center_y - self.light_radius

        self.dark_mask.blit(self.light_brush, (blit_x, blit_y), special_flags=pygame.BLEND_RGBA_MIN)

        screen.blit(self.dark_mask, (0, 0))