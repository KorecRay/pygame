# main.py
import pygame
import sys

# 確保這些檔案存在且名稱正確
from settings import *
from core.maploader import TiledMap
from sprites.player import Player
from sprites.enemy import Enemy     # 🚨 導入 Enemy 類別
from core.light_manager import LightManager

# --- 1. 遊戲初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("墨影忍者V1")
clock = pygame.time.Clock()

# --- 2. 資源載入與物件初始化 ---
try:
    # 載入 TMX 地圖 (map_handler 現在包含 player_spawn 和 enemy_data_list)
    map_handler = TiledMap(TMX_FILE)
except FileNotFoundError:
    print(f"錯誤：找不到地圖檔案 {TMX_FILE}。請檢查路徑。")
    pygame.quit()
    sys.exit()

# 🚨 玩家初始化：從載入的關卡數據中獲取起始位置
player_start_x, player_start_y = map_handler.player_spawn
player = Player(player_start_x, player_start_y)

# 精靈群組管理
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()  # 🚨 新增敵人精靈群組
all_sprites.add(player)

# 🚨 敵人初始化：根據載入的數據創建敵人
for enemy_data in map_handler.enemy_data_list:
    x, y = enemy_data["start_pos"]
    move_range = enemy_data["move_range"]
    speed = enemy_data["speed"]
    
    # 這裡可以根據 type 欄位來創建不同類型的敵人 (目前只處理 ExplosiveBot)
    if enemy_data["type"] == "ExplosiveBot":
        new_enemy = Enemy(x, y, move_range, speed)
        enemies.add(new_enemy)
        all_sprites.add(new_enemy)

# 初始化光照管理器 (確保 PLAYER_LIGHT_RADIUS 已定義)
try:
    # 嘗試從 settings 中獲取，否則使用預設值
    light_radius = PLAYER_LIGHT_RADIUS
except NameError:
    light_radius = 32 # 使用預設值
    print("警告: PLAYER_LIGHT_RADIUS 未在 settings.py 中定義，使用預設值 32。")

light_manager = LightManager(light_radius)

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
    # 更新玩家 (傳遞地圖碰撞物、致命區域和彈跳床)
    # 敵人暫時不需要額外的碰撞列表，它們只與 walls 碰撞
    all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)
    
    # 🚨 更新敵人 (只需傳入牆壁進行碰撞檢測和重力處理)
    enemies.update(map_handler.walls) 
    
    # 🚨 玩家與敵人的碰撞檢測 (Player-Enemy Interaction)
    # False 表示玩家碰到敵人時，敵人不會自動從群組中移除
    enemy_hits = pygame.sprite.spritecollide(player, enemies, False) 
    if enemy_hits:
        for enemy in enemy_hits:
            # 敵人被觸碰，觸發爆炸，玩家重生
            enemy.explode() 
            player._respawn()
            
    # --- 3. 繪製 (Draw) ---
    screen.fill((0, 0, 0))  # 清空螢幕

    # 繪製地圖背景 (在黑暗遮罩之下)
    screen.blit(map_handler.map_surface, (0, 0))

    # 繪製所有精靈 (包括玩家和敵人)
    all_sprites.draw(screen)

    # 繪製黑暗遮罩 (必須在所有遊戲元素繪製完成後)
    light_manager.draw(screen, player.rect)

    # 刷新顯示
    pygame.display.flip()

# --- 4. 遊戲結束 ---
pygame.quit()
sys.exit()