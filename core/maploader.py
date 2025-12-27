import pygame
import pytmx
import json
from settings import WIDTH, HEIGHT, LEVEL_DATA_PATH
from typing import List

class TiledMap:
    def __init__(self, filename):
        try:
            # 載入 TMX 資料
            self.tmx_data = pytmx.load_pygame(filename, force_colorkey=(0, 0, 0))
        except Exception as e:
            raise FileNotFoundError(f"載入 TMX 失敗: {e}")

        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        # 1. 預渲染地圖畫布
        self.map_surface = self._make_map_surface()

        # 2. 提取功能性物件 (Collision, Hazards...)
        self.walls = self._load_objects_from_layer("Collision")
        self.hazards = self._load_objects_from_layer("Hazards")
        self.bouncers = self._load_objects_from_layer("Bouncers")

        # 3. 載入 JSON 配置
        level_id = filename.split('/')[-1].split('.')[0]
        spawn, dest, enemies, props = self._load_level_data(level_id)

        self.player_spawn = spawn
        self.destination_pos = dest
        self.enemy_data_list = enemies
        self.prop_data_list = props

    def _make_map_surface(self):
        """核心地圖渲染：將瓦片與屬性文字合併"""
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for layer in self.tmx_data.layers:
            # 1. 處理磁磚層
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        temp_surface.blit(tile, (x * self.tmx_data.tilewidth, 
                                               y * self.tmx_data.tileheight))
            
            # 2. 處理物件層 (直接針對屬性內的 'value' 進行提取)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    # 🚨 這是你指定的方式：從 properties 字典裡抓取名為 "value" 的屬性
                    content = obj.properties.get('value')
                    
                    if content:
                        self._draw_text_from_value(temp_surface, obj, content)
                        
        return temp_surface

    def _draw_text_from_value(self, surface, obj, content):
        """根據 TMX 物件屬性繪製文字"""
        try:
            # 顏色與字體大小設定 (可視需求調整，或同樣從屬性抓取)
            color = (85, 255, 255) # #55ffff
            size = 20
            
            font = pygame.font.SysFont("Arial", size, bold=True)
            text_surf = font.render(str(content), True, color)
            
            # 繪製到地圖畫布
            surface.blit(text_surf, (obj.x, obj.y))
            print(f"✅ [ID {obj.id}] 成功渲染文字屬性: {content}")
            
        except Exception as e:
            print(f"❌ [ID {obj.id}] 渲染失敗: {e}")

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
            with open(LEVEL_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            lv = data.get(level_id, {})
            return lv.get("player_spawn", [0,0]), lv.get("destination"), lv.get("enemies", []), lv.get("props", [])
        except Exception as e:
            return [0,0], None, [], []