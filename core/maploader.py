# map.py
import pygame
import pytmx
from settings import *
# 導入常數


class TiledMap:
    def __init__(self, filename):
        # 1. 載入 TMX 資料
        # 尋找檔案位置：assets/map/lv1.tmx
        try:
            self.tmx_data = pytmx.load_pygame(filename, force_colorkey=(0, 0, 0))
        except FileNotFoundError:
            raise FileNotFoundError(f"無法找到 TMX 檔案: {filename}。請檢查路徑是否正確。")

        # 2. 計算地圖的總像素尺寸
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        # 3. 預渲染地圖 Surface (視覺部分)
        self.map_surface = self._make_map_surface()

        # 4. 載入碰撞 Rects (邏輯部分)
        self.walls = self._load_collision_objects()

    def _make_map_surface(self):
        """將 TMX 中的所有瓦片圖層合併到一個 Pygame Surface 上。"""
        temp_surface = pygame.Surface((self.width, self.height))

        # 遍歷所有可見的瓦片圖層並 Blit 到 Surface 上
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        # 繪製位置計算
                        pos_x = x * self.tmx_data.tilewidth
                        pos_y = y * self.tmx_data.tileheight
                        temp_surface.blit(tile_image, (pos_x, pos_y))

        return temp_surface

    def _load_collision_objects(self):
        """從名為 'Collision' 的物件圖層中提取 Rect 列表。"""
        walls = []

        # 查找名為 'Collision' 的物件圖層
        try:
            collision_layer = self.tmx_data.get_layer_by_name("Collision")

            for obj in collision_layer:
                # Tiled 物件 (x, y, w, h) 直接轉換為 Pygame.Rect
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                walls.append(rect)

            print(f"地圖載入成功，提取了 {len(walls)} 個碰撞物件。")
        except ValueError:
            print("警告：地圖中未找到名為 'Collision' 的物件圖層。")

        return walls