import os
import pygame
import pytmx
import json
from settings import WIDTH, HEIGHT, LEVEL_DATA_PATH, resource_path
from typing import List

class TiledMap:
    def __init__(self, filename):
        try:
            # Load TMX data (supports PyInstaller temp path)
            tmx_path = resource_path(filename)
            self.tmx_data = pytmx.load_pygame(tmx_path, force_colorkey=(0, 0, 0))
        except Exception as e:
            raise FileNotFoundError(f"TMX load failed: {e}")

        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        # 1. Pre-render map surface
        self.map_surface = self._make_map_surface()

        # 2. Extract functional objects (Collision, Hazards...)
        self.walls = self._load_objects_from_layer("Collision")
        self.hazards = self._load_objects_from_layer("Hazards")
        self.bouncers = self._load_objects_from_layer("Bouncers")

        # 3. Load JSON config
        level_id = os.path.basename(filename).split('.')[0]
        spawn, dest, enemies, props = self._load_level_data(level_id)

        self.player_spawn = spawn
        self.destination_pos = dest
        self.enemy_data_list = enemies
        self.prop_data_list = props

    def _make_map_surface(self):
        """Core map rendering: Adds background grid."""
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # --- [New] Draw background grid ---
        grid_size = 32  # Adjust based on TILE_SIZE
        grid_color = (40, 40, 40)  # Dark gray

        # Vertical lines
        for x in range(0, self.width, grid_size):
            pygame.draw.line(temp_surface, grid_color, (x, 0), (x, self.height), 1)
        # Horizontal lines
        for y in range(0, self.height, grid_size):
            pygame.draw.line(temp_surface, grid_color, (0, y), (self.width, y), 1)
        # ---------------------------

        for layer in self.tmx_data.layers:
            # 1. Tile layers
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        temp_surface.blit(tile, (x * self.tmx_data.tilewidth,
                                                 y * self.tmx_data.tileheight))

            # 2. Object layers
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    content = obj.properties.get('value')
                    if content:
                        self._draw_text_from_value(temp_surface, obj, content)

        return temp_surface

    def _draw_text_from_value(self, surface, obj, content):
        """Draw text based on TMX object properties."""
        try:
            # Color and font size (can be adjusted or fetched from properties)
            color = (85, 255, 255) # #55ffff
            size = 20
            
            font = pygame.font.SysFont("Arial", size, bold=True)
            text_surf = font.render(str(content), True, color)
            
            # Draw to map surface
            surface.blit(text_surf, (obj.x, obj.y))
            print(f"✅ [ID {obj.id}] Text rendered: {content}")
            
        except Exception as e:
            print(f"❌ [ID {obj.id}] Render failed: {e}")

    def _load_objects_from_layer(self, layer_name):
        rect_list = []
        try:
            obj_layer = self.tmx_data.get_layer_by_name(layer_name)
            for obj in obj_layer:
                rect_list.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        except:
            pass
        return rect_list

    def _load_level_data(self, level_id):
        try:
            with open(resource_path(LEVEL_DATA_PATH), 'r', encoding='utf-8') as f:
                data = json.load(f)
            lv = data.get(level_id, {})
            return lv.get("player_spawn", [0,0]), lv.get("destination"), lv.get("enemies", []), lv.get("props", [])
        except Exception:
            return [0,0], None, [], []