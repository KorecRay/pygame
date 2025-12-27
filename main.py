import pygame
import sys
from settings import *
from core.maploader import TiledMap
from sprites.player import Player
from sprites.enemy import Enemy
from sprites.prop import Prop
from sprites.dest import Destination
from core.light_manager import LightManager

# --- 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("墨影忍者 - 重構版")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 64, bold=True)

# --- 全域變數 ---
map_handler = TiledMap(TMX_FILE)
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
props_group = pygame.sprite.Group()
dest_group = pygame.sprite.Group()

player = None
shield_timer = 0
torch_timer = 0
has_anti_explosion = False
level_cleared = False

def reset_level():
    """徹底清空並重製關卡物件"""
    global player, shield_timer, torch_timer, has_anti_explosion, level_cleared
    
    # 1. 清空所有舊數據
    all_sprites.empty()
    enemies.empty()
    props_group.empty()
    dest_group.empty()
    
    shield_timer = 0
    torch_timer = 0
    has_anti_explosion = False
    level_cleared = False

    # 2. 取得關卡配置 (對應 maploader 的 4 個回傳值)
    level_id = TMX_FILE.split('/')[-1].split('.')[0]
    p_spawn, d_pos, e_list, p_list = map_handler._load_level_data(level_id)

    # 3. 重新生成物件
    # 終點
    if d_pos:
        goal = Destination(d_pos[0], d_pos[1])
        dest_group.add(goal)
        all_sprites.add(goal)

    # 玩家 (確保 Player 類別內的 __init__ 會重新載入動畫)
    player = Player(p_spawn[0], p_spawn[1])
    all_sprites.add(player)

    # 敵人
    for e in e_list:
        new_enemy = Enemy(e["start_pos"][0], e["start_pos"][1], e["move_range"], e["speed"])
        enemies.add(new_enemy)
        all_sprites.add(new_enemy)

    # 道具
    for p in p_list:
        new_prop = Prop(p["pos"][0], p["pos"][1], p["type"])
        props_group.add(new_prop)
        all_sprites.add(new_prop)

# 啟動遊戲
reset_level()
light_manager = LightManager(PLAYER_LIGHT_RADIUS)

# --- 主迴圈 ---
running = True
while running:
    clock.tick(FPS)

    # 1. 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and level_cleared:
            if event.key == pygame.K_r: # 通關後按 R 重玩
                reset_level()

    if not level_cleared:
        # 2. 更新邏輯
        if shield_timer > 0: shield_timer -= 1
        if torch_timer > 0: torch_timer -= 1

        all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)
        enemies.update(map_handler.walls)

        # 3. 碰撞檢查
        # A. 死亡檢查 (標記死亡或掉落)
        if player.is_dead:
            reset_level()
            continue

        # B. 終點檢查
        if pygame.sprite.spritecollideany(player, dest_group):
            level_cleared = True

        # C. 道具檢查
        p_hits = pygame.sprite.spritecollide(player, props_group, True)
        for p in p_hits:
            if p.prop_type == 1: player.vel.y = -12.0 # 跳躍
            elif p.prop_type == 2: has_anti_explosion = True
            elif p.prop_type == 3: shield_timer = 5 * FPS
            elif p.prop_type == 4: torch_timer = 2 * FPS

        # D. 敵人檢查
        e_hits = pygame.sprite.spritecollide(player, enemies, False)
        if e_hits:
            should_die = True
            for e in e_hits:
                if shield_timer > 0 or has_anti_explosion:
                    e.explode()
                    has_anti_explosion = False
                    should_die = False
            if should_die:
                reset_level()
                continue

    # 4. 繪製邏輯
    screen.fill((0, 0, 0))
    screen.blit(map_handler.map_surface, (0, 0))
    
    # 視覺反饋：護盾時透明度
    if shield_timer > 0: player.image.set_alpha(150)
    else: player.image.set_alpha(255)

    all_sprites.draw(screen)

    # 光照處理
    if not level_cleared and torch_timer <= 0:
        light_manager.draw(screen, player.rect)

    # 通關文字
    if level_cleared:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        txt = font.render("MISSION ACCOMPLISHED", True, (0, 255, 0))
        screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
        sub_txt = font.render("Press 'R' to Restart", True, (200, 200, 200))
        screen.blit(sub_txt, sub_txt.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))

    pygame.display.flip()

pygame.quit()
sys.exit()