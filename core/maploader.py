import pygame
import pytmx
import json
from settings import *
from typing import List

class TiledMap:
    def __init__(self, filename):
        # 1. 載入 TMX 資料
        try:
            self.tmx_data = pytmx.load_pygame(filename, force_colorkey=(0, 0, 0))
        except FileNotFoundError:
            raise FileNotFoundError(f"無法找到 TMX 檔案: {filename}。請檢查路徑是否正確。")

        # 2. 計算地圖的總像素尺寸
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        # 3. 預渲染地圖 Surface (視覺部分)
        self.map_surface = self._make_map_surface()

        # 4. 載入靜態牆壁/地面 (所有物件都是實體碰撞)
        self.walls = self._load_objects_from_layer("Collision")

        # 5. 載入致命障礙物 (所有物件都會 GG)
        self.hazards = self._load_objects_from_layer("Hazards")

        # 6. 載入彈跳床物件 (所有物件都會彈跳)
        self.bouncers = self._load_objects_from_layer("Bouncers")

        # 7. 載入關卡特定數據 (新增)
        # 從 TMX 檔案名中提取關卡 ID，例如 'assets/map/lv1.tmx' -> 'lv1'
        level_id = filename.split('/')[-1].split('.')[0]
        self.player_spawn, self.enemy_data_list = self._load_level_data(level_id)

    def _make_map_surface(self):
        """將 TMX 中的所有瓦片圖層合併到一個 Pygame Surface 上。"""
        temp_surface = pygame.Surface((self.width, self.height))
        # 遍歷所有可見的瓦片圖層並 Blit 到 Surface 上
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        pos_x = x * self.tmx_data.tilewidth
                        pos_y = y * self.tmx_data.tileheight
                        temp_surface.blit(tile_image, (pos_x, pos_y))
        return temp_surface

    def _load_objects_from_layer(self, layer_name) -> List[pygame.Rect]:
        """通用方法：載入指定圖層中所有物件的邊界 Rect，不檢查任何屬性。"""
        rect_list = []
        try:
            obj_layer = self.tmx_data.get_layer_by_name(layer_name)

            for obj in obj_layer:
                # 無論是矩形、多邊形還是折線，pytmx 都會提供基礎的邊界矩形 (x, y, width, height)
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                rect_list.append(rect)

            print(f"地圖載入成功：提取了 {len(rect_list)} 個 {layer_name} 類型物件。")
        except ValueError:
            print(f"警告：地圖中未找到名為 '{layer_name}' 的物件圖層。")
        except Exception as e:
            print(f"載入 {layer_name} 時發生錯誤: {e}")

        return rect_list

    def _load_level_data(self, level_id):
        """從 JSON 檔案中讀取特定關卡的數據。"""
        try:
            with open(LEVEL_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            level_data = data.get(level_id)
            if not level_data:
                raise ValueError(f"JSON 檔案中未找到關卡ID: {level_id}")

            player_spawn = level_data.get("player_spawn", [0, 0])
            enemies = level_data.get("enemies", [])

            print(f"成功載入關卡 {level_id}：玩家起始點 {player_spawn}, 敵人數量 {len(enemies)}")
            return player_spawn, enemies

        except FileNotFoundError:
            print(f"錯誤：找不到關卡數據檔案: {LEVEL_DATA_PATH}")
            return [0, 0], []
        except json.JSONDecodeError:
            print(f"錯誤：解析關卡數據檔案 {LEVEL_DATA_PATH} 失敗，請檢查 JSON 格式。")
            return [0, 0], []
        except Exception as e:
            print(f"載入關卡數據時發生未知錯誤: {e}")
            return [0, 0], []