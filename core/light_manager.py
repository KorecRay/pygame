# core/light_manager.py
import pygame
from settings import WIDTH, HEIGHT


class LightManager:
    """
    使用單一 Surface 和 BLEND_RGBA_MIN 模式實現全黑場景中的玩家視野光圈。
    """

    def __init__(self, light_radius):
        self.light_radius = light_radius
        self.light_size = light_radius * 4

        # 1. 創建光照 Surface (用於在上面繪製透明圓形)
        # 尺寸與螢幕相同，初始為完全不透明的黑色 (R, G, B, Alpha=255)
        self.dark_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.dark_mask.fill((0, 0, 0, 255))

        # 2. 創建透明光圈筆刷 (Brush)
        # 這是一個小 Surface，中心是透明圓形，周圍是黑色，用於 Blit 到 dark_mask 上。
        self.light_brush = pygame.Surface((self.light_size, self.light_size), pygame.SRCALPHA)
        self.light_brush.fill((0, 0, 0, 255))  # 初始全黑

        # 在中心鑿出一個完全透明的圓形 (Alpha=0)
        pygame.draw.circle(self.light_brush, (0, 0, 0, 0),
                           (self.light_size // 2, self.light_size // 2),
                           self.light_radius)

    def draw(self, screen, player_rect):
        """
        將黑暗遮罩應用到螢幕上，並以玩家為中心鑿出可見光圈。
        """

        # 1. 重設黑暗遮罩 (每幀都必須將其恢復為全黑，否則光圈會殘留)
        self.dark_mask.fill((0, 0, 0, 255))

        # 2. 計算光圈筆刷的 Blit 座標
        center_x, center_y = player_rect.center
        blit_x = center_x - (self.light_size // 2)
        blit_y = center_y - (self.light_size // 2)

        # 3. 關鍵：將透明筆刷 Blit 到黑暗遮罩上，使用 BLEND_RGBA_MIN 模式
        # 邏輯：黑色層 (255 Alpha) 遇到透明筆刷 (0 Alpha) 進行 MIN 運算，
        # 結果是該區域的 Alpha 值變為 0 (透明)。
        self.dark_mask.blit(self.light_brush,
                            (blit_x, blit_y),
                            special_flags=pygame.BLEND_RGBA_MIN)

        # 4. 將最終帶有光圈的黑暗遮罩繪製到螢幕上
        #
        screen.blit(self.dark_mask, (0, 0))