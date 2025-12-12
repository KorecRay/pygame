import pygame
import pytmx
from settings import *  # 導入常數


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

        # 4. 載入靜態牆壁/地面 (一般碰撞)
        self.walls = self._load_collision_objects("Collision")

        # 5. 載入致命障礙物 (危險區域)
        self.hazards = self._load_hazard_objects("Hazards")

    def _make_map_surface(self):
        """將 TMX 中的所有瓦片圖層合併到一個 Pygame Surface 上。"""
        temp_surface = pygame.Surface((self.width, self.height))

        # 遍歷所有可見的瓦片圖層並 Blit 到 Surface 上
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                # 這裡的 x, y, gid 迭代是 pytmx 的標準用法
                for x, y, gid in layer:
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        pos_x = x * self.tmx_data.tilewidth
                        pos_y = y * self.tmx_data.tileheight
                        temp_surface.blit(tile_image, (pos_x, pos_y))

        return temp_surface

    def _load_collision_objects(self, layer_name):
        """從指定的物件圖層中提取 Rect 列表 (用於一般牆壁/地面碰撞)。"""
        rect_list = []

        try:
            collision_layer = self.tmx_data.get_layer_by_name(layer_name)

            for obj in collision_layer:
                # 僅提取沒有 is_lethal 屬性或該屬性為 False 的物件（確保不會重複處理）
                if obj.properties.get('is_lethal') != True:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    rect_list.append(rect)

            print(f"地圖載入成功：提取了 {len(rect_list)} 個 {layer_name} 碰撞物件。")
        except ValueError:
            print(f"警告：地圖中未找到名為 '{layer_name}' 的物件圖層。")

        return rect_list

    def _load_hazard_objects(self, layer_name):
        """從指定的物件圖層中提取致命障礙物 (Hazards)。"""
        hazard_rects = []

        try:
            hazard_layer = self.tmx_data.get_layer_by_name(layer_name)

            for obj in hazard_layer:
                # 檢查 Tiled 物件是否有 'is_lethal' 屬性且值為 True
                # if obj.properties.get('is_lethal') == True:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                hazard_rects.append(rect)
                # elif obj.properties.get('is_lethal') == None:
                    # 如果未設定屬性，也可以將其視為致命物，取決於您的設計
                    # 這裡為了嚴謹，只接受明確標記的物件


            print(f"地圖載入成功：提取了 {len(hazard_rects)} 個 {layer_name} 致命障礙。")
        except ValueError:
            # 如果沒有 Hazards 圖層，就返回一個空列表
            print(f"警告：地圖中未找到名為 '{layer_name}' 的物件圖層。")

        return hazard_rects