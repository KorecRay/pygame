import pygame
import sys
import settings
from settings import *
from core.maploader import TiledMap
from sprites.player import Player
from sprites.enemy import Enemy
from sprites.prop import Prop
from sprites.dest import Destination
from core.light_manager import LightManager
from core.level import LvSelect
from core.debug import Debugger

# --- 1. 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("墨影忍者 - LV 系統重製版")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 64, bold=True)

# --- 2. 全域變數與群組 ---
game_state = "LV_MENU" # 狀態: LV_MENU / PLAYING
lv_selector = LvSelect(screen)
map_handler = None
light_manager = None

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
props_group = pygame.sprite.Group()
dest_group = pygame.sprite.Group()

player = None
shield_timer = 0
torch_timer = 0
has_anti_explosion = False
lv_cleared = False

# 視野縮放
base_radius = PLAYER_LIGHT_RADIUS
current_radius = base_radius
target_radius = base_radius
lerp_speed = 0.08

def load_lv(lv_num):
    """根據編號載入關卡檔案"""
    global map_handler, game_state
    # 修改 settings 中的檔案路徑
    settings.TMX_FILE = f"assets/map/lv{lv_num}.tmx"
    try:
        map_handler = TiledMap(settings.TMX_FILE)
        reset_lv_data()
        game_state = "PLAYING"
    except Exception as e:
        print(f"載入失敗: {e}")

def reset_lv_data():
    """完全重置當前關卡的所有物件"""
    global player, shield_timer, torch_timer, has_anti_explosion, lv_cleared
    global current_radius, target_radius
    
    # 清空
    all_sprites.empty()
    enemies.empty()
    props_group.empty()
    dest_group.empty()
    
    # 重設狀態
    lv_cleared = False
    shield_timer = 0
    torch_timer = 0
    has_anti_explosion = False
    current_radius = base_radius
    target_radius = base_radius

    # 讀取地圖數據
    lv_id = settings.TMX_FILE.split('/')[-1].split('.')[0]
    p_spawn, d_pos, e_list, p_list = map_handler._load_level_data(lv_id)

    # 1. 終點
    if d_pos:
        goal = Destination(d_pos[0], d_pos[1])
        dest_group.add(goal)
        all_sprites.add(goal)

    # 2. 玩家
    player = Player(p_spawn[0], p_spawn[1])
    all_sprites.add(player)

    # 3. 敵人 (🚨 關鍵：確保重新加入 all_sprites 與 enemies)
    for e in e_list:
        new_enemy = Enemy(e["start_pos"][0], e["start_pos"][1], e["move_range"], e["speed"])
        enemies.add(new_enemy)
        all_sprites.add(new_enemy)

    # 4. 道具 (🚨 關鍵：確保重新加入 all_sprites 與 props_group)
    for p in p_list:
        new_prop = Prop(p["pos"][0], p["pos"][1], p["type"])
        props_group.add(new_prop)
        all_sprites.add(new_prop)
    
    print(f"--- {lv_id} 重置完成 ---")

# 初始化光照系統
light_manager = LightManager(base_radius)

# --- 3. 遊戲主迴圈 ---
running = True
while running:
    clock.tick(FPS)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if game_state == "LV_MENU":
        # --- 選單邏輯 ---
        for event in events:
            selected_lv = lv_selector.handle_input(event)
            if selected_lv:
                load_lv(selected_lv)
        lv_selector.draw()

    elif game_state == "PLAYING":
        # --- 遊戲邏輯 ---
        for event in events:
            if event.type == pygame.KEYDOWN:
                # 通關後按 Enter 返回
                if lv_cleared and event.key == pygame.K_RETURN:
                    game_state = "LV_MENU"
                # 遊戲中按 R 手動重製
                if event.key == pygame.K_r:
                    reset_lv_data()
                if event.key == pygame.K_m:
                    DEBUG_MODE = not DEBUG_MODE
                    print(f"偵錯模式: {'開啟' if DEBUG_MODE else '關閉'}")

        if not lv_cleared:
            # 1. 計時器與視野 Lerp
            if shield_timer > 0: shield_timer -= 1
            if torch_timer > 0:
                torch_timer -= 1
                target_radius = base_radius * 5
            else:
                target_radius = base_radius
            
            current_radius += (target_radius - current_radius) * lerp_speed

            # 2. 更新精靈
            all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)
            enemies.update(map_handler.walls)

            # 3. 碰撞檢查
            if player.is_dead:
                reset_lv_data()
                continue

            if pygame.sprite.spritecollideany(player, dest_group):
                lv_cleared = True

            # 道具碰撞
            p_hits = pygame.sprite.spritecollide(player, props_group, True)
            for p in p_hits:
                if p.prop_type == 1: player.vel.y = -12.0
                elif p.prop_type == 2: has_anti_explosion = True
                elif p.prop_type == 3: shield_timer = 5 * FPS
                elif p.prop_type == 4: torch_timer = 2 * FPS

            # 敵人碰撞
            e_hits = pygame.sprite.spritecollide(player, enemies, False)
            if e_hits:
                should_die = True
                for e in e_hits:
                    if shield_timer > 0 or has_anti_explosion:
                        if hasattr(e, 'explode'): e.explode()
                        else: e.kill()
                        has_anti_explosion = False
                        should_die = False
                if should_die:
                    reset_lv_data()
                    continue

        # --- 4. 繪製 ---
        screen.fill((0, 0, 0))
        screen.blit(map_handler.map_surface, (0, 0))
        
        # 視覺回饋
        if shield_timer > 0: player.image.set_alpha(150)
        else: player.image.set_alpha(255)

        all_sprites.draw(screen)

        # 光照
        if not lv_cleared:
            light_manager.draw(screen, player.rect, current_radius)

        # debug
        if DEBUG_MODE:
            Debugger.draw_hitboxes(screen, player, enemies, props_group, dest_group, map_handler)

        # 通關 UI
        if lv_cleared:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            txt = font.render("MISSION ACCOMPLISHED", True, (0, 255, 0))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
            sub = font.render("Press 'ENTER' to Menu", True, (200, 200, 200))
            screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))

    pygame.display.flip()

pygame.quit()