# core/maploader.py
import pygame
import pytmx
import json
from settings import WIDTH, HEIGHT, TMX_FILE, LEVEL_DATA_PATH  # 確保這些已在 settings 定義
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

        # 4. 載入碰撞與功能圖層
        self.walls = self._load_objects_from_layer("Collision")
        self.hazards = self._load_objects_from_layer("Hazards")
        self.bouncers = self._load_objects_from_layer("Bouncers")

        # 5. 載入關卡 JSON 數據
        # 取得檔名作為 ID，例如 'assets/map/lv1.tmx' -> 'lv1'
        level_id = filename.split('/')[-1].split('.')[0]

        # 🚨 接收三個回傳值：玩家點、敵人列表、道具列表
        spawn, enemies, props = self._load_level_data(level_id)

        self.player_spawn = spawn
        self.enemy_data_list = enemies
        self.prop_data_list = props  # 儲存道具資料供 main.py 使用

    def _make_map_surface(self):
        """將 TMX 中的所有瓦片圖層合併到一個 Pygame Surface 上。"""
        temp_surface = pygame.Surface((self.width, self.height))
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
        """從物件圖層提取 Rect 列表。"""
        rect_list = []
        try:
            obj_layer = self.tmx_data.get_layer_by_name(layer_name)
            for obj in obj_layer:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                rect_list.append(rect)
            print(f"地圖載入成功：提取了 {len(rect_list)} 個 {layer_name} 物件。")
        except ValueError:
            print(f"警告：圖層 '{layer_name}' 未找到。")
        return rect_list

    def _load_level_data(self, level_id):
        """從 JSON 檔案讀取關卡配置。"""
        try:
            with open(LEVEL_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            level_data = data.get(level_id)
            if not level_data:
                raise ValueError(f"JSON 中找不到關卡: {level_id}")

            player_spawn = level_data.get("player_spawn", [0, 0])
            enemies = level_data.get("enemies", [])
            props = level_data.get("props", [])  # 修正原本的 // 錯誤註釋

            print(f"成功載入關卡 {level_id} 設定。")
            return player_spawn, enemies, props

        except FileNotFoundError:
            print(f"錯誤：找不到 JSON 檔案 {LEVEL_DATA_PATH}")
            return [0, 0], [], []
        except Exception as e:
            print(f"JSON 載入錯誤: {e}")
            return [0, 0], [], []