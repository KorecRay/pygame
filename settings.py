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
# 使用專門給玩家的參數，來源：sprites/player.py 的原始常數
PLAYER_SPEED = 3.0
GRAVITY = 0.2
JUMP_STRENGTH = -7.0
BOOST_JUMP_STRENGTH = -12.0
PLAYER_LIGHT_RADIUS = 128  # 玩家視野半徑 (像素，半徑)

# 備註/舊參數
# PLAYER_JUMP_VELOCITY (已棄用，改用 JUMP_STRENGTH)


# effects
SMOOTH_LIGHTING_ENABLED = True

# debug
DEBUG_MODE = False