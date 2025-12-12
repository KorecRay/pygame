# main.py
import pygame
import sys

# 確保這些檔案存在且名稱正確
from settings import *
from core.maploader import TiledMap
from sprites.player import Player
from core.light_manager import LightManager # 導入光照管理器

# 遊戲常數
PLAYER_LIGHT_RADIUS = 128 # 玩家視野半徑 (直徑 64 像素)

# --- 1. 遊戲初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("墨影忍者V1")
clock = pygame.time.Clock()

# --- 2. 資源載入與物件初始化 ---
try:
    # 載入 TMX 地圖 (包含 Walls, Hazards, Bouncers 列表)
    map_handler = TiledMap(TMX_FILE)
except FileNotFoundError:
    print(f"錯誤：找不到地圖檔案 {TMX_FILE}。請檢查路徑。")
    pygame.quit()
    sys.exit()

# 玩家初始化 (初始位置: x=100, y=840)
player_start_x = 100
player_start_y = 840
player = Player(player_start_x, player_start_y)

# 精靈群組管理
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# 初始化光照管理器
light_manager = LightManager(PLAYER_LIGHT_RADIUS)

# --- 3. 遊戲主迴圈 ---
running = True
while running:

    # 設置幀率 (FPS)
    clock.tick(FPS)

    # --- 1. 事件處理 (Events) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- 2. 更新 (Update) ---
    # 傳遞地圖碰撞物、致命區域和彈跳床給玩家
    all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)

    # --- 3. 繪製 (Draw) ---
    screen.fill((0, 0, 0))  # 清空螢幕

    # 繪製地圖背景 (在黑暗遮罩之下)
    screen.blit(map_handler.map_surface, (0, 0))

    # 繪製所有精靈 (玩家在黑暗遮罩之下)
    all_sprites.draw(screen)

    # 繪製黑暗遮罩 (必須在所有遊戲元素繪製完成後)
    # 遮罩會以玩家的碰撞箱中心為原點鑿出光圈
    light_manager.draw(screen, player.rect)

    # ⚠️ 除錯模式：繪製碰撞箱 (這些現在會被黑暗遮罩部分遮蓋)
    # for wall in map_handler.walls:
    #     pygame.draw.rect(screen, (0, 255, 0), wall, 1)
    # for hazard in map_handler.hazards:
    #     pygame.draw.rect(screen, (255, 0, 0), hazard, 1)
    # for bouncer in map_handler.bouncers:
    #     pygame.draw.rect(screen, (0, 0, 255), bouncer, 1)

    # 刷新顯示
    pygame.display.flip()

# --- 4. 遊戲結束 ---
pygame.quit()
sys.exit()