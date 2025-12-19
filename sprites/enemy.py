# sprites/enemy.py
import pygame
from settings import TILE_SIZE

# --- 物理常數 ---
GRAVITY = 0.7  # 敵人也受重力影響


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range, speed):
        # 使用 pygame.sprite.Sprite 的初始化
        super().__init__()

        # 尺寸與視覺 (例如 1 瓦片寬高)
        width = TILE_SIZE
        height = TILE_SIZE
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 100, 0))  # 橘色代表爆炸機器人

        # 碰撞箱
        self.rect = self.image.get_rect(topleft=(x, y))

        # 物理屬性
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)

        # 移動/巡邏屬性
        self.start_x = x
        self.move_range = move_range  # 巡邏中心點的左右範圍
        self.speed = speed
        self.direction = 1  # 1: 右移, -1: 左移

        self.is_dead = False  # 爆炸狀態

    def update(self, walls, hazards=None, bouncers=None):
        """更新敵人狀態、執行移動和碰撞檢測。"""

        if self.is_dead:
            # 如果敵人已經死亡/爆炸，不執行任何操作
            return

        self._apply_gravity()
        self._patrol_move()

        # 執行 X/Y 分離移動和牆壁碰撞
        self.rect.x = int(self.pos.x + self.vel.x)
        self._collide_and_resolve_x(walls)

        self.rect.y = int(self.pos.y + self.vel.y)
        self._collide_and_resolve_y(walls)

        self.pos.x = self.rect.x  # 更新浮點數位置
        self.pos.y = self.rect.y

    def _apply_gravity(self):
        """應用重力，敵人也會下落。"""
        self.vel.y += GRAVITY
        if self.vel.y > 10:
            self.vel.y = 10

    def _patrol_move(self):
        """左右巡邏移動邏輯。"""

        # 設定水平速度
        self.vel.x = self.direction * self.speed

        # 檢查是否超出移動範圍
        current_center_x = self.pos.x + self.rect.width / 2  # 當前中心點

        # 左邊界
        if current_center_x <= self.start_x - self.move_range / 2:
            self.direction = 1  # 轉向右

        # 右邊界
        elif current_center_x >= self.start_x + self.move_range / 2:
            self.direction = -1  # 轉向左

    def _collide_and_resolve_x(self, walls):
        """X 軸碰撞檢測與推回。"""
        for wall in walls:
            if self.rect.colliderect(wall):
                # 碰到牆壁，立刻轉向
                self.direction *= -1
                self.vel.x = self.direction * self.speed

                # 推回 (防止卡牆)
                if self.vel.x > 0:
                    self.rect.right = wall.left
                else:
                    self.rect.left = wall.right

                break

    def _collide_and_resolve_y(self, walls):
        """Y 軸碰撞檢測與推回。"""
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel.y > 0:
                    self.rect.bottom = wall.top
                else:
                    self.rect.top = wall.bottom
                self.vel.y = 0
                break  # 確保只處理一次 Y 軸碰撞

    def explode(self):
        """觸發爆炸/死亡邏輯。"""
        self.is_dead = True
        self.kill()  # 將精靈從所有群組中移除 (Pygame 內建方法)
        print(f"敵人 {self.__class__.__name__} 爆炸！")