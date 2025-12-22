import pygame
from settings import TILE_SIZE

# --- 物理常數 ---
GRAVITY = 0.2
PLAYER_SPEED = 3.0  # 固定移動速度
JUMP_STRENGTH = -7.0
BOOST_JUMP_STRENGTH = -12.0  # 超級彈跳速度 (新增)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # 尺寸與視覺
        width = TILE_SIZE * 0.6
        height = TILE_SIZE * 1.2
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 255))

        # 碰撞箱
        self.rect = self.image.get_rect(topleft=(x, y))

        # 記錄起始點，用於死亡重生
        self.spawn_pos = (x, y)

        # 狀態
        self.vel = pygame.math.Vector2(0, 0)
        self.on_ground = False

    def update(self, walls, hazards, bouncers):  # 🚨 新增 bouncers 參數

        self._get_input()
        self._apply_gravity()

        # 執行 X/Y 分離移動和牆壁碰撞
        self.rect.x += self.vel.x
        self._collide_and_resolve(self.vel.x, 0, walls)

        self.rect.y += self.vel.y
        self._collide_and_resolve(0, self.vel.y, walls)

        # 檢查致命障礙物
        if self._check_lethal_collision(hazards):
            self._respawn()

        # 檢查彈跳床 (新增)
        self._check_bouncer_collision(bouncers)

    def trigger_bounce_jump(self):
        """用於觸發超級彈跳。"""
        self.vel.y = BOOST_JUMP_STRENGTH
        self.on_ground = False
        print("觸發超級彈跳！")

    def _respawn(self):
        """將玩家傳送回起始點並重設物理狀態。"""
        self.rect.topleft = self.spawn_pos
        self.vel = pygame.math.Vector2(0, 0)
        self.on_ground = False
        print("玩家死亡，傳送回起點。")

    def _get_input(self):

        keys = pygame.key.get_pressed()
        self.vel.x = 0

        if keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel.y = JUMP_STRENGTH
            self.on_ground = False

    def _apply_gravity(self):

        self.vel.y += GRAVITY
        if self.vel.y > 15:
            self.vel.y = 15

    def _collide_and_resolve(self, dx, dy, walls):

        for wall in walls:
            if self.rect.colliderect(wall):

                if dx != 0:
                    if dx > 0:
                        self.rect.right = wall.left
                    else:
                        self.rect.left = wall.right
                    self.vel.x = 0

                if dy != 0:
                    if dy > 0:
                        self.rect.bottom = wall.top
                        self.on_ground = True
                    else:
                        self.rect.top = wall.bottom
                    self.vel.y = 0

    def _check_lethal_collision(self, hazards):

        for hazard_rect in hazards:
            if self.rect.colliderect(hazard_rect):
                return True
        return False

    def _check_bouncer_collision(self, bouncers):
        """檢查是否與彈跳床重疊，並在從上方落下時觸發彈跳。"""
        if self.vel.y > 0:  # 僅在下落時檢查
            for bouncer_rect in bouncers:
                if self.rect.colliderect(bouncer_rect):

                    # 檢查玩家的上一次位置，確保是從上方落下
                    # 注意：由於是整數座標，這裡的檢查會比較簡單粗暴
                    prev_bottom = self.rect.bottom - self.vel.y

                    # 如果上次底部位置在上一次更新時高於彈跳床頂部
                    if prev_bottom <= bouncer_rect.top:
                        self.trigger_bounce_jump()

                        # 碰撞處理：將玩家推回彈跳床頂部
                        self.rect.bottom = bouncer_rect.top

                        return