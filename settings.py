import pygame as pg

# 遊戲配置
TITLE = "Ink Ninja"
FPS = 120
GRID_WIDTH = 40
GRID_HEIGHT = 30
TILE_SIZE = 32

WIDTH = GRID_WIDTH * TILE_SIZE    # 40 x 32 = 1280 px
HEIGHT = GRID_HEIGHT * TILE_SIZE  # 30 x 32 = 960 px

# 檔案路徑
TMX_FILE = 'assets/map/lv5.tmx'
LEVEL_DATA_PATH = 'assets/map/lvsetting.json'

# 玩家屬性
PLAYER_SPEED = 5
PLAYER_JUMP_VELOCITY = 15
GRAVITY = 1
PLAYER_LIGHT_RADIUS = 96 # 玩家視野半徑 (直徑 64 像素)


# effects
SMOOTH_LIGHTING_ENABLED = True