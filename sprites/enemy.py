import pygame
from settings import TILE_SIZE

GRAVITY = 0.7


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range, speed):
        super().__init__()

        # --- 動畫設定 ---
        self.frame_index = 0
        self.animation_speed = 0.15  # 數字越小動畫越慢
        self.state = "run"  # 初始狀態
        self.facing_right = True  # 面向方向

        # 載入並切分圖片 (假設檔案路徑如下)
        self.animations = {
            "idle": self._load_frames("assets/sprites/enemy_idle.png", 4),
            "run": self._load_frames("assets/sprites/enemy_run.png", 6)
        }

        # 設定初始圖片
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # 物理與移動屬性
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.start_x = x
        self.move_range = move_range
        self.speed = speed
        self.direction = 1
        self.is_dead = False

    def _load_frames(self, path, frame_count):
        """切分 Spritesheet 的工具函式"""
        frames = []
        try:
            sheet = pygame.image.load(path).convert_alpha()
            for i in range(frame_count):
                # 每個動作都是 32x32，橫向切分
                frame = sheet.subsurface((i * 32, 0, 32, 32))
                # 如果你的 TILE_SIZE 不是 32，可以在這裡縮放
                if TILE_SIZE != 32:
                    frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
                frames.append(frame)
        except Exception as e:
            print(f"載入動畫錯誤 {path}: {e}")
            # 沒圖時的防呆機制：給個顏色方塊
            dummy = pygame.Surface((TILE_SIZE, TILE_SIZE))
            dummy.fill((255, 0, 0))
            frames = [dummy]
        return frames

    def _animate(self):
        """處理動畫幀切換與翻轉"""
        animation = self.animations[self.state]

        # 增加索引
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # 取得當前幀圖片
        current_frame = animation[int(self.frame_index)]

        # 🚨 處理左右翻面
        # 如果 direction 是 -1 且目前面向右，就翻轉
        if self.direction < 0:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame

    def update(self, walls, *args, **kwargs):
        """
        接收所有參數 (*args) 避免報錯，
        解決之前的 TypeError: Enemy.update() takes 2 positional arguments but 4 were given
        """
        if self.is_dead:
            return

        self._apply_gravity()
        self._patrol_move()

        # 根據速度決定狀態 (如果速度為 0 就 idle，但你的巡邏通常都在跑)
        self.state = "run" if self.vel.x != 0 else "idle"

        # 執行 X/Y 移動
        self.rect.x = int(self.pos.x + self.vel.x)
        self._collide_and_resolve_x(walls)
        self.rect.y = int(self.pos.y + self.vel.y)
        self._collide_and_resolve_y(walls)

        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

        # 更新動畫
        self._animate()

    # --- 以下 _apply_gravity, _patrol_move, _collide_and_resolve 等邏輯保持不變 ---
    def _apply_gravity(self):
        self.vel.y += GRAVITY
        if self.vel.y > 10: self.vel.y = 10

    def _patrol_move(self):
        self.vel.x = self.direction * self.speed
        current_center_x = self.pos.x + self.rect.width / 2
        if current_center_x <= self.start_x - self.move_range / 2:
            self.direction = 1
        elif current_center_x >= self.start_x + self.move_range / 2:
            self.direction = -1

    def _collide_and_resolve_x(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                self.direction *= -1
                if self.direction > 0:
                    self.rect.right = wall.left
                else:
                    self.rect.left = wall.right
                break

    def _collide_and_resolve_y(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel.y > 0:
                    self.rect.bottom = wall.top
                else:
                    self.rect.top = wall.bottom
                self.vel.y = 0
                break

    def explode(self):
        pass
        # self.is_dead = True
        # self.kill()