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
pygame.display.set_caption("墨影忍者 - 光影重製版")
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

# --- 視野縮放變數 ---
base_radius = PLAYER_LIGHT_RADIUS
current_radius = base_radius
target_radius = base_radius
lerp_speed = 0.08  # 數值越小，擴散與收縮越平滑

def reset_level():
    """徹底清空並重製關卡物件"""
    global player, shield_timer, torch_timer, has_anti_explosion, level_cleared
    global current_radius, target_radius
    
    all_sprites.empty()
    enemies.empty()
    props_group.empty()
    dest_group.empty()
    
    shield_timer = 0
    torch_timer = 0
    has_anti_explosion = False
    level_cleared = False
    
    # 重置視野
    current_radius = base_radius
    target_radius = base_radius

    level_id = TMX_FILE.split('/')[-1].split('.')[0]
    p_spawn, d_pos, e_list, p_list = map_handler._load_level_data(level_id)

    if d_pos:
        goal = Destination(d_pos[0], d_pos[1])
        dest_group.add(goal)
        all_sprites.add(goal)

    player = Player(p_spawn[0], p_spawn[1])
    all_sprites.add(player)

    for e in e_list:
        new_enemy = Enemy(e["start_pos"][0], e["start_pos"][1], e["move_range"], e["speed"])
        enemies.add(new_enemy); all_sprites.add(new_enemy)

    for p in p_list:
        new_prop = Prop(p["pos"][0], p["pos"][1], p["type"])
        props_group.add(new_prop); all_sprites.add(new_prop)

reset_level()
light_manager = LightManager(base_radius)

# --- 主迴圈 ---
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and level_cleared:
            if event.key == pygame.K_r:
                reset_level()

    if not level_cleared:
        # 1. 計時器與視野目標設定
        if shield_timer > 0: shield_timer -= 1
        if torch_timer > 0: 
            torch_timer -= 1
            target_radius = base_radius * 5 # 火把效果：5 倍視野
        else:
            target_radius = base_radius     # 結束：回復原始視野

        # 2. 視野平滑縮放 (Lerp)
        # 讓當前半徑慢慢靠近目標半徑
        current_radius += (target_radius - current_radius) * lerp_speed

        # 3. 更新所有精靈
        all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers)
        enemies.update(map_handler.walls)

        # 4. 碰撞檢查
        if player.is_dead:
            reset_level()
            continue

        if pygame.sprite.spritecollideany(player, dest_group):
            level_cleared = True

        p_hits = pygame.sprite.spritecollide(player, props_group, True)
        for p in p_hits:
            if p.prop_type == 1: player.vel.y = -12.0
            elif p.prop_type == 2: has_anti_explosion = True
            elif p.prop_type == 3: shield_timer = 5 * FPS
            elif p.prop_type == 4: torch_timer = 2 * FPS # 觸發火把

        e_hits = pygame.sprite.spritecollide(player, enemies, False)
        if e_hits:
            should_die = True
            for e in e_hits:
                if shield_timer > 0 or has_anti_explosion:
                    e.explode(); has_anti_explosion = False; should_die = False
            if should_die:
                reset_level()
                continue

    # --- 繪製 ---
    screen.fill((0, 0, 0))
    screen.blit(map_handler.map_surface, (0, 0))
    
    # 護盾視覺
    if shield_timer > 0: player.image.set_alpha(150)
    else: player.image.set_alpha(255)

    all_sprites.draw(screen)

    # 動態光照繪製
    if not level_cleared:
        light_manager.draw(screen, player.rect, current_radius)

    # 通關畫面
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