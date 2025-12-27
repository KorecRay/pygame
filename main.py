# main.py
import pygame
import sys
from settings import *
from core.maploader import TiledMap
from sprites.player import Player
from sprites.enemy import Enemy
from sprites.prop import Prop
from core.light_manager import LightManager

# --- 1. 遊戲初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("墨影忍者V1 - 死亡重製版")
clock = pygame.time.Clock()

# --- 2. 資源載入 ---
try:
    map_handler = TiledMap(TMX_FILE)
except FileNotFoundError:
    print(f"錯誤：找不到地圖檔案 {TMX_FILE}")
    pygame.quit()
    sys.exit()

# 建立精靈群組
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
props_group = pygame.sprite.Group()

# 狀態管理
shield_timer = 0
torch_timer = 0
has_anti_explosion = False
player = None  # 先宣告全域變數

def reset_level():
    """重新初始化關卡：清空所有精靈並根據數據重新生成"""
    global player, shield_timer, torch_timer, has_anti_explosion

    # 1. 清空舊群組
    all_sprites.empty()
    enemies.empty()
    props_group.empty()

    # 2. 重置狀態
    shield_timer = 0
    torch_timer = 0
    has_anti_explosion = False

    # 3. 獲取關卡數據
    level_id = TMX_FILE.split('/')[-1].split('.')[0]
    player_pos, enemy_data, prop_data = map_handler._load_level_data(level_id)

    # 4. 重新生成玩家 (確保這裡會觸發 Player.__init__ 重新載入動畫)
    player = Player(player_pos[0], player_pos[1])
    all_sprites.add(player)

    # 5. 重新生成敵人
    for e in enemy_data:
        new_enemy = Enemy(e["start_pos"][0], e["start_pos"][1], e["move_range"], e["speed"])
        enemies.add(new_enemy)
        all_sprites.add(new_enemy)

    # 6. 重新生成道具
    for p in prop_data:
        new_prop = Prop(p["pos"][0], p["pos"][1], p["type"])
        props_group.add(new_prop)
        all_sprites.add(new_prop)
    
    print(f"關卡已重製，玩家位置：{player_pos}")

# 第一次啟動遊戲
reset_level()

# 初始化光照
try:
    light_radius = PLAYER_LIGHT_RADIUS
except NameError:
    light_radius = 32
light_manager = LightManager(light_radius)

# --- 3. 遊戲主迴圈 ---
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- 1. 更新邏輯 ---
    if shield_timer > 0: shield_timer -= 1
    if torch_timer > 0: torch_timer -= 1

    # 更新所有精靈 (這會執行 player.update 並呼叫 _animate())
    all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)
    enemies.update(map_handler.walls)

    # --- 2. 死亡檢測 (提前處理) ---
    
    # 檢查玩家內部死亡標記 (墜落或陷阱)
    if player.is_dead:
        reset_level()
        continue # 立即跳過本幀後續碰撞，防止對已刪除的 player 進行操作

    # 道具碰撞
    prop_hits = pygame.sprite.spritecollide(player, props_group, True)
    for p in prop_hits:
        if p.prop_type == 1: player.vel.y = -12.0 # 超級跳躍
        elif p.prop_type == 2: has_anti_explosion = True
        elif p.prop_type == 3: shield_timer = 5 * FPS
        elif p.prop_type == 4: torch_timer = 2 * FPS

    # 敵人碰撞
    enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
    if enemy_hits:
        should_reset = False
        for enemy in enemy_hits:
            if has_anti_explosion or shield_timer > 0:
                enemy.explode()
                has_anti_explosion = False 
            else:
                should_reset = True
        
        if should_reset:
            reset_level()
            continue

    # --- 3. 繪製邏輯 ---
    screen.fill((0, 0, 0))
    screen.blit(map_handler.map_surface, (0, 0))
    
    # 繪製精靈
    all_sprites.draw(screen)

    # 視覺回饋 (透明度處理)
    if shield_timer > 0:
        player.image.set_alpha(150)
    else:
        player.image.set_alpha(255)

    # 光照處理
    if torch_timer <= 0:
        light_manager.draw(screen, player.rect)

    pygame.display.flip()

pygame.quit()
sys.exit()