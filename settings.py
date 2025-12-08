import pygame as pg

# 遊戲配置
TITLE = "Ink Ninja"
FPS = 120
GRID_WIDTH = 80
GRID_HEIGHT = 60
TILE_SIZE = 10

WIDTH = GRID_WIDTH * TILE_SIZE    # 80 * 16 = 800 px
HEIGHT = GRID_HEIGHT * TILE_SIZE  # 60 * 16 = 600 px

TMX_FILE = 'assets/map/lv1.tmx'

# 玩家屬性
PLAYER_SPEED = 5
PLAYER_JUMP_VELOCITY = 15
GRAVITY = 1