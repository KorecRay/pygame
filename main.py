# main.py
import pygame
import sys

# 確保這些檔案存在且名稱正確
from settings import *
from core.maploader import TiledMap
from sprites.player import Player

# --- 1. 遊戲初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("墨影忍者V1")
clock = pygame.time.Clock()

# --- load resource ---
try:
    # load tmx map (pre-rendering Surface & Collision Rects)
    map_handler = TiledMap(TMX_FILE)
except FileNotFoundError:
    print(f"錯誤：找不到地圖檔案 {TMX_FILE}。請檢查路徑。")
    pygame.quit()
    sys.exit()

# player init (初始位置: x=10, y=550)
player_start_x = 1228
player_start_y = 570
player = Player(player_start_x, player_start_y)

# 精靈群組管理 (用於統一更新和繪製)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

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
    # 更新所有精靈。Player.update() 會接收並處理 map_handler.walls
    all_sprites.update(map_handler.walls, map_handler.hazards)

    # --- 3. 繪製 (Draw) ---
    screen.fill((0, 0, 0))  # 清空螢幕

    # 繪製地圖背景 (貼在 (0, 0) 點)
    screen.blit(map_handler.map_surface, (0, 0))

    # 繪製所有精靈 (玩家)
    all_sprites.draw(screen)

    # ⚠️ 除錯模式：繪製碰撞箱 (請在除錯時取消註解)
    # for wall in map_handler.walls:
    #     pygame.draw.rect(screen, (0, 255, 0), wall, 1)
    for wall in map_handler.hazards:
        pygame.draw.rect(screen, (255, 0, 0), wall, 1)

    # 刷新顯示
    pygame.display.flip()

# --- 4. 遊戲結束 ---
pygame.quit()
sys.exit()