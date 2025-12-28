import pygame
from settings import *

class LightManager:
    def __init__(self, light_radius):
        self.default_radius = light_radius
        self.dark_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # 建立一個基礎的漸層光圈 (256x256)，稍後用來縮放
        self.base_size = 512
        self.base_brush = self._create_base_brush(self.base_size // 2)

    def _create_base_brush(self, radius):
        """建立一個固定的基礎漸層圓形"""
        brush_size = radius * 2
        surface = pygame.Surface((brush_size, brush_size), pygame.SRCALPHA)
        # 初始填充不透明黑
        surface.fill((0, 0, 0, 255))
        
        for r in range(radius, 0, -2):
            # 計算透明度：越往中心越透明 (0)
            alpha = int(255 * (r / radius))
            pygame.draw.circle(surface, (0, 0, 0, alpha), (radius, radius), r)
        return surface

    def draw(self, screen, player_rect, current_radius):
        # 1. 填充遮罩為全黑
        self.dark_mask.fill((0, 0, 0, 255))

        # 2. 根據當前要求的半徑縮放基礎光圈
        r_int = int(current_radius)
        if r_int <= 0: return # 防止半徑為 0 導致錯誤
        
        # 動態縮放 brush
        scaled_brush = pygame.transform.scale(self.base_brush, (r_int * 2, r_int * 2))
        
        # 3. 計算繪製位置 (讓光圈中心對準玩家中心)
        center = player_rect.center
        blit_x = center[0] - r_int
        blit_y = center[1] - r_int

        # 4. 使用 BLEND_RGBA_MIN 挖洞
        self.dark_mask.blit(scaled_brush, (blit_x, blit_y), special_flags=pygame.BLEND_RGBA_MIN)

        # 5. 蓋到主螢幕
        screen.blit(self.dark_mask, (0, 0))