# player.py
import pygame
from settings import *  # 導入 TILESIZE, WIDTH, HEIGHT 等常數

# 物理常數
GRAVITY = 0.1  # 重力加速度
PLAYER_SPEED = 1.0
JUMP_STRENGTH = -8.0  # 負值代表向上


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # 繼承 pygame.sprite.Sprite
        super().__init__()

        # 視覺表示 (暫時用矩形代替)
        # 玩家尺寸設定為 10x15 像素 (比單個瓦片稍小)
        player_width = TILE_SIZE  # 10
        player_height = TILE_SIZE * 1.5  # 15

        # 圖像 (用於 blit)
        self.image = pygame.Surface((player_width, player_height))
        self.image.fill((0, 0, 255))  # 藍色矩形

        # 碰撞箱 (Rect)
        # 初始位置：x=10, y=550
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # 物理狀態
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_on_ground = False  # 判斷是否在地面，用於控制跳躍

    def get_input(self):
        """處理鍵盤輸入，設定 x 軸速度和跳躍。"""
        keys = pygame.key.get_pressed()
        self.velocity_x = 0

        # 水平移動 (W/S 暫不使用，平台遊戲只用 A/D)
        if keys[pygame.K_a]:
            self.velocity_x = -PLAYER_SPEED
        if keys[pygame.K_d]:
            self.velocity_x = PLAYER_SPEED

        # 跳躍 (Space)
        if keys[pygame.K_SPACE] and self.is_on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.is_on_ground = False  # 跳起後不在地面

    def apply_gravity(self):
        """施加重力並更新 y 軸速度。"""
        # 只有在空中才施加重力
        self.velocity_y += GRAVITY
        # 限制下落速度 (防止穿過地面)
        if self.velocity_y > 10:
            self.velocity_y = 10

    def update(self, wall_rects):
        """更新玩家狀態，並處理碰撞。"""
        self.get_input()
        self.apply_gravity()

        # -------------------------------------
        # 執行 X 軸碰撞處理
        # -------------------------------------
        self.rect.x += self.velocity_x
        self._collide_with_walls(self.velocity_x, 0, wall_rects)

        # -------------------------------------
        # 執行 Y 軸碰撞處理
        # -------------------------------------
        self.rect.y += self.velocity_y
        self._collide_with_walls(0, self.velocity_y, wall_rects)

    def _collide_with_walls(self, dx, dy, wall_rects):
        """X/Y 分離碰撞檢測與處理 (Resolution)。"""

        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dx != 0:  # 處理水平碰撞 (X 軸)
                    if dx > 0:  # 玩家向右撞到左牆
                        self.rect.right = wall.left
                    elif dx < 0:  # 玩家向左撞到右牆
                        self.rect.left = wall.right
                    self.velocity_x = 0  # 停止水平移動

                if dy != 0:  # 處理垂直碰撞 (Y 軸)
                    if dy > 0:  # 玩家向下撞到頂部 (著地)
                        self.rect.bottom = wall.top
                        self.is_on_ground = True  # 設為在地面
                    elif dy < 0:  # 玩家向上撞到底部 (頂頭)
                        self.rect.top = wall.bottom
                    self.velocity_y = 0  # 停止垂直移動