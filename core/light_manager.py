import pygame
from settings import *

class LightManager:
    def __init__(self, light_radius):
        self.default_radius = light_radius
        self.dark_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Create a base gradient circle (512x512) for later scaling
        self.base_size = 512
        self.base_brush = self._create_base_brush(self.base_size // 2)

    def _create_base_brush(self, radius):
        """Creates a fixed base gradient circle."""
        brush_size = radius * 2
        surface = pygame.Surface((brush_size, brush_size), pygame.SRCALPHA)
        # Fill with opaque black initially
        surface.fill((0, 0, 0, 255))
        
        for r in range(radius, 0, -2):
            # Calculate alpha: more transparent (0) towards the center
            alpha = int(255 * (r / radius))
            pygame.draw.circle(surface, (0, 0, 0, alpha), (radius, radius), r)
        return surface

    def draw(self, screen, player_rect, current_radius):
        # 1. Fill mask with solid black
        self.dark_mask.fill((0, 0, 0, 255))

        # 2. Scale base brush according to current radius
        r_int = int(current_radius)
        if r_int <= 0: return # Prevent error if radius is 0
        
        # Dynamic scaling of brush
        scaled_brush = pygame.transform.scale(self.base_brush, (r_int * 2, r_int * 2))
        
        # 3. Calculate draw position (center brush on player)
        center = player_rect.center
        blit_x = center[0] - r_int
        blit_y = center[1] - r_int

        # 4. Carve hole using BLEND_RGBA_MIN
        self.dark_mask.blit(scaled_brush, (blit_x, blit_y), special_flags=pygame.BLEND_RGBA_MIN)

        # 5. Blit to main screen
        screen.blit(self.dark_mask, (0, 0))