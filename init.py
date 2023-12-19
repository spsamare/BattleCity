import os, glob
from spritesheet import *
from sounds import *

DIRECTION = {
    "N": 0,
    "W": 1,
    "S": 2,
    "E": 3,
    "I": 32,
    "B": 34
}

KEYS2 = {
    "N": pg.K_UP,
    "S": pg.K_DOWN,
    "E": pg.K_RIGHT,
    "W": pg.K_LEFT,
    "F": pg.K_RCTRL
}

KEYS1 = {
    "N": pg.K_w,
    "S": pg.K_s,
    "E": pg.K_d,
    "W": pg.K_a,
    "F": pg.K_LCTRL
}

COLORS = {
    "background": (0, 0, 1),
    "white": (255, 255, 255),
    "key": (0, 0, 1),
    "static": (99, 99, 99)
}

AGENT_SIZE = 2

RES_SCALE = 4

FPS = 120

ENEMY_COUNT = 20

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
aspect_ratio = 3 / 4  # 9/16
WIDTH = 1024  # 1280  # 1024 works well
HEIGHT = int(WIDTH * aspect_ratio)
BLOCK_SIZE = 2 * int(HEIGHT / 52)
SCREEN = pg.display.set_mode((WIDTH, HEIGHT),  pg.FULLSCREEN)

image_library, \
    player1_sprite_start, player1_sprite_end, \
    player2_sprite_start, player2_sprite_end, \
    enemy1_sprite_start, enemy1_sprite_end, \
    enemy2_sprite_start, enemy2_sprite_end, \
    bullet_sprite_start, bullet_sprite_end, \
    shield_sprite_start, shield_sprite_end, \
    shine_sprite_start, shine_sprite_end, \
    blast_sprite_start, blast_sprite_end, \
    obstacle_brick_sprite_start, obstacle_brick_sprite_end, \
    obstacle_steel_sprite, obstacle_forest_sprite, obstacle_ice_sprite, \
    obstacle_ocean_sprite_start, obstacle_ocean_sprite_end, \
    bird_sprite_start, bird_sprite_end, \
    reward_shield_sprite, reward_freeze_sprite, reward_fortify_sprite, \
    reward_upgrade_sprite, reward_blast_sprite, reward_life_sprite, reward_empty_sprite, \
    stat_pallet_sprite, stat_enemy_sprite, \
    stat_num_sprite_start, stat_num_sprite_end, \
    display_first_start, display_second_start, display_third_start, display_fourth_start, display_title, display_end = \
    load_sprites(fullpath='res/tank_res_high.png',
                 color_key=COLORS["key"],
                 block_size=BLOCK_SIZE,
                 resolution_scale=RES_SCALE)

REWARD_PROBABILITY = [
    .2,  # shield
    .2,  # freeze
    .2,  # fortify
    .2,  # upgrade
    .15,  # blast
    .05  # life
]

map_files = [f for f in os.listdir('maps') if f.endswith('.map')]
MAP_COUNT = len(map_files)

sound_library = {
    'p_idle': s_idle,
    'p_move': s_move,
    'p_fire': s_fire,
    'p_destroy': s_p_destroy,
    'h_brick': s_hit_brick,
    'h_steel': s_hit_steel,
    'h_enemy': s_hit_enemy,
    'd_enemy': s_e_destroy,
    'r_': s_reward_appear,
    'r_star': s_reward_star,
    'r_life': s_reward_life,
    'r_fortify': s_reward_fortify
}
