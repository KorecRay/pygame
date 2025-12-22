import pygame
from settings import TILE_SIZE


class Prop(pygame.sprite.Sprite):
    def __init__(self, x, y, prop_type):
        super().__init__()

        self.prop_type = int(prop_type)  # 1:跳躍, 2:防爆, 3:護盾, 4:火把

        # 載入靜態圖片 (例如 assets/sprites/prop_1.png)
        try:
            path = f"assets/sprites/prop_{self.prop_type}.png"
            self.image = pygame.image.load(path).convert_alpha()
            # 確保尺寸符合遊戲設定
            if self.image.get_size() != (32, 32):
                self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            # 防呆：如果讀不到圖，就畫個有色方塊
            self.image = pygame.Surface((32, 32))
            colors = {1: (0, 255, 0), 2: (255, 100, 0), 3: (0, 100, 255), 4: (255, 255, 0)}
            self.image.fill(colors.get(self.prop_type, (200, 200, 200)))

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args, **kwargs):
        # 靜態道具不需要額外更新邏輯
        pass