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

    # 3. 獲取關卡數據 (自動讀取 TMX 對應的 JSON ID)
    level_id = TMX_FILE.split('/')[-1].split('.')[0]
    player_pos, enemy_data, prop_data = map_handler._load_level_data(level_id)

    # 4. 重新生成玩家
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

    # --- 更新邏輯 ---
    if shield_timer > 0: shield_timer -= 1
    if torch_timer > 0: torch_timer -= 1

    all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)
    enemies.update(map_handler.walls)

    # 道具碰撞
    prop_hits = pygame.sprite.spritecollide(player, props_group, True)
    for p in prop_hits:
        if p.prop_type == 1:
            player.trigger_bounce_jump()
        elif p.prop_type == 2:
            has_anti_explosion = True
        elif p.prop_type == 3:
            shield_timer = 5 * FPS
        elif p.prop_type == 4:
            torch_timer = 2 * FPS

    # 敵人碰撞
    enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
    if enemy_hits:
        for enemy in enemy_hits:
            if has_anti_explosion or shield_timer > 0:
                enemy.explode()
                has_anti_explosion = False  # 消耗斬殺
            else:
                # 🚨 關鍵：玩家死亡，呼叫 reset_level 重製一切
                print("玩家陣亡，重新開始關卡...")
                reset_level()
                break  # 跳出碰撞迴圈避免重複執行

    # 玩家墜落或踩到陷阱重製
    # 假設 Player.update 內觸發了 _respawn()，這裡我們改成偵測玩家狀態
    # 或者簡單判斷：如果玩家踩到 hazards
    player_hit_hazards = pygame.Rect.collidelist(player.rect, map_handler.hazards)
    if player_hit_hazards != -1:
        reset_level()

    # --- 繪製邏輯 ---
    screen.fill((0, 0, 0))
    screen.blit(map_handler.map_surface, (0, 0))
    all_sprites.draw(screen)

    if shield_timer > 0:
        player.image.set_alpha(150)
    else:
        player.image.set_alpha(255)

    if torch_timer <= 0:
        light_manager.draw(screen, player.rect)

    pygame.display.flip()

pygame.quit()