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
from core.pause import PauseMenu

# --- 1. Init ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ink Ninja - Remastered")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 64, bold=True)

# --- 2. Globals & Groups ---
game_state = "LV_MENU" # States: LV_MENU / PLAYING / PAUSED
lv_selector = LvSelect(screen)
pause_menu = PauseMenu(screen)
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

# View radius
base_radius = PLAYER_LIGHT_RADIUS
current_radius = base_radius
target_radius = base_radius
lerp_speed = 0.08

def load_lv(lv_num):
    """Load level by number."""
    global map_handler, game_state
    settings.TMX_FILE = f"assets/map/lv{lv_num}.tmx"
    try:
        map_handler = TiledMap(settings.TMX_FILE)
        reset_lv_data()
        game_state = "PLAYING"
    except Exception as e:
        print(f"Load failed: {e}")

def reset_lv_data():
    """Reset current level data."""
    global player, shield_timer, torch_timer, has_anti_explosion, lv_cleared
    global current_radius, target_radius
    
    # Clear groups
    all_sprites.empty()
    enemies.empty()
    props_group.empty()
    dest_group.empty()
    
    # Reset state
    lv_cleared = False
    shield_timer = 0
    torch_timer = 0
    has_anti_explosion = False
    current_radius = base_radius
    target_radius = base_radius

    # Load map data
    lv_id = settings.TMX_FILE.split('/')[-1].split('.')[0]
    p_spawn, d_pos, e_list, p_list = map_handler._load_level_data(lv_id)

    # 1. Destination
    if d_pos:
        goal = Destination(d_pos[0], d_pos[1])
        dest_group.add(goal)
        all_sprites.add(goal)

    # 2. Player
    player = Player(p_spawn[0], p_spawn[1])
    all_sprites.add(player)

    # 3. Enemies
    for e in e_list:
        new_enemy = Enemy(e["start_pos"][0], e["start_pos"][1], e["move_range"], e["speed"])
        enemies.add(new_enemy)
        all_sprites.add(new_enemy)

    # 4. Props
    for p in p_list:
        new_prop = Prop(p["pos"][0], p["pos"][1], p["type"])
        props_group.add(new_prop)
        all_sprites.add(new_prop)
    
    print(f"--- {lv_id} Reset Complete ---")

# Init light system
light_manager = LightManager(base_radius)

# --- 3. Main Loop ---
running = True
while running:
    clock.tick(FPS)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if game_state == "LV_MENU":
        # --- Menu Logic ---
        for event in events:
            selected_lv = lv_selector.handle_input(event)
            if selected_lv:
                load_lv(selected_lv)
        lv_selector.draw()

    elif game_state == "PLAYING":
        # --- Game Logic ---
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Return to menu after clear
                if lv_cleared and event.key == pygame.K_RETURN:
                    game_state = "LV_MENU"
                # Manual reset
                if event.key == pygame.K_r:
                    reset_lv_data()
                # Toggle debug
                if event.key == pygame.K_m:
                    DEBUG_MODE = not DEBUG_MODE
                    print(f"Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
                # Pause
                if event.key == pygame.K_ESCAPE and not lv_cleared:
                    game_state = "PAUSED"

        if not lv_cleared:
            # 1. Timers & Radius Lerp
            if shield_timer > 0: shield_timer -= 1
            if torch_timer > 0:
                torch_timer -= 1
                target_radius = base_radius * 5
            else:
                target_radius = base_radius
            
            current_radius += (target_radius - current_radius) * lerp_speed

            # 2. Update Sprites
            all_sprites.update(map_handler.walls, map_handler.hazards, map_handler.bouncers, shield_timer)
            enemies.update(map_handler.walls)

            # 3. Collisions
            if player.is_dead:
                reset_lv_data()
                continue

            if pygame.sprite.spritecollideany(player, dest_group):
                lv_cleared = True

            # Prop collisions
            p_hits = pygame.sprite.spritecollide(player, props_group, True)
            for p in p_hits:
                if p.prop_type == 1: player.vel.y = -12.0
                elif p.prop_type == 2: has_anti_explosion = True
                elif p.prop_type == 3: shield_timer = 5 * FPS
                elif p.prop_type == 4: torch_timer = 2 * FPS

            # Enemy collisions
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

        # --- 4. Draw ---
        screen.fill((0, 0, 0))
        screen.blit(map_handler.map_surface, (0, 0))
        
        # Visual feedback
        if shield_timer > 0: player.image.set_alpha(150)
        else: player.image.set_alpha(255)

        all_sprites.draw(screen)

        # Lighting
        if not lv_cleared:
            light_manager.draw(screen, player.rect, current_radius)

        # Debug
        if DEBUG_MODE:
            Debugger.draw_hitboxes(screen, player, enemies, props_group, dest_group, map_handler)

        # Clear UI
        if lv_cleared:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            txt = font.render("MISSION ACCOMPLISHED", True, (0, 255, 0))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
            sub = font.render("Press 'ENTER' to Menu", True, (200, 200, 200))
            screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))

    elif game_state == "PAUSED":
        # Draw last frame
        screen.fill((0, 0, 0))
        screen.blit(map_handler.map_surface, (0, 0))
        all_sprites.draw(screen)

        # Draw pause menu
        pause_menu.draw()

        # Handle pause input
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "PLAYING"

            action = pause_menu.handle_input(event)
            if action == "RESUME":
                game_state = "PLAYING"
            elif action == "MAIN_MENU":
                game_state = "LV_MENU"

    pygame.display.flip()

pygame.quit()