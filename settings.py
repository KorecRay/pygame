import os
import sys
import pygame as pg

# Game Config
TITLE = "Ink Ninja"
FPS = 120
GRID_WIDTH = 40
GRID_HEIGHT = 30
TILE_SIZE = 32

WIDTH = GRID_WIDTH * TILE_SIZE    # 40 x 32 = 1280 px
HEIGHT = GRID_HEIGHT * TILE_SIZE  # 30 x 32 = 960 px

# File Paths
TMX_FILE = 'assets/map/lv5.tmx'
LEVEL_DATA_PATH = 'assets/map/lvsetting.json'

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Player Attributes
PLAYER_SPEED = 3.0
GRAVITY = 0.2
JUMP_STRENGTH = -7.0
BOOST_JUMP_STRENGTH = -12.0
PLAYER_LIGHT_RADIUS = 128  # Player view radius (pixels)

# Effects
SMOOTH_LIGHTING_ENABLED = True

# Debug
DEBUG_MODE = False