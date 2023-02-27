# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)

import pygame as pg


class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pg.image.load(filename).convert()
        except pg.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, color_key=None):
        # Loads image from x,y,x+offset,y+offset
        rect = pg.Rect(rectangle)
        if color_key is not None:
            image = pg.Surface(rect.size).convert()
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pg.RLEACCEL)
        else:
            image = pg.Surface(rect.size).convert_alpha()

        # image = pygame.transform.scale(image, (rect.size[0] // 4, rect.size[1] // 4))
        image.blit(self.sheet, (0, 0), rect)
        return image

    # Load images and return them as a list
    def images_at(self, rects, color_key=None):
        # Loads multiple images, supply a list of coordinates
        return [self.image_at(rect, color_key) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, color_key=None):
        # Loads a strip of images and returns them as a list
        tuples = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                  for x in range(image_count)]
        return self.images_at(tuples, color_key)


def load_sprites(block_size, resolution_scale, fullpath='res/tank_res_high.png', color_key=(0, 0, 1)):
    ss = SpriteSheet(fullpath)
    player1_sprite_list = (
        (0, 0, 32, 32), (64, 0, 32, 32), (128, 0, 32, 32), (192, 0, 32, 32),
        (32, 0, 32, 32), (96, 0, 32, 32), (160, 0, 32, 32), (224, 0, 32, 32),
        (0, 32, 32, 32), (64, 32, 32, 32), (128, 32, 32, 32), (192, 32, 32, 32),
        (32, 32, 32, 32), (96, 32, 32, 32), (160, 32, 32, 32), (224, 32, 32, 32),
        (0, 64, 32, 32), (64, 64, 32, 32), (128, 64, 32, 32), (192, 64, 32, 32),
        (32, 64, 32, 32), (96, 64, 32, 32), (160, 64, 32, 32), (224, 64, 32, 32),
        (0, 96, 32, 32), (64, 96, 32, 32), (128, 96, 32, 32), (192, 96, 32, 32),
        (32, 96, 32, 32), (96, 96, 32, 32), (160, 96, 32, 32), (224, 96, 32, 32),
        (576, 288, 32, 32)
    )
    player1_sprite_start = 0
    player1_sprite_end = 33

    player2_sprite_list = (
        (0, 256, 32, 32), (64, 256, 32, 32), (128, 256, 32, 32), (192, 256, 32, 32),
        (32, 256, 32, 32), (96, 256, 32, 32), (160, 256, 32, 32), (224, 256, 32, 32),
        (0, 288, 32, 32), (64, 288, 32, 32), (128, 288, 32, 32), (192, 288, 32, 32),
        (32, 288, 32, 32), (96, 288, 32, 32), (160, 288, 32, 32), (224, 288, 32, 32),
        (0, 320, 32, 32), (64, 320, 32, 32), (128, 320, 32, 32), (192, 320, 32, 32),
        (32, 320, 32, 32), (96, 320, 32, 32), (160, 320, 32, 32), (224, 320, 32, 32),
        (0, 352, 32, 32), (64, 352, 32, 32), (128, 352, 32, 32), (192, 352, 32, 32),
        (32, 352, 32, 32), (96, 352, 32, 32), (160, 352, 32, 32), (224, 352, 32, 32),
        (576, 288, 32, 32)
    )
    player2_sprite_start = player1_sprite_end
    player2_sprite_end = player2_sprite_start + 33

    enemy1_sprite_list = (
        (256 + 0, 256, 32, 32), (256 + 64, 256, 32, 32), (256 + 128, 256, 32, 32), (256 + 192, 256, 32, 32),
        (256 + 32, 256, 32, 32), (256 + 96, 256, 32, 32), (256 + 160, 256, 32, 32), (256 + 224, 256, 32, 32),
        (256 + 0, 288, 32, 32), (256 + 64, 288, 32, 32), (256 + 128, 288, 32, 32), (256 + 192, 288, 32, 32),
        (256 + 32, 288, 32, 32), (256 + 96, 288, 32, 32), (256 + 160, 288, 32, 32), (256 + 224, 288, 32, 32),
        (256 + 0, 320, 32, 32), (256 + 64, 320, 32, 32), (256 + 128, 320, 32, 32), (256 + 192, 320, 32, 32),
        (256 + 32, 320, 32, 32), (256 + 96, 320, 32, 32), (256 + 160, 320, 32, 32), (256 + 224, 320, 32, 32),
        (256 + 0, 352, 32, 32), (256 + 64, 352, 32, 32), (256 + 128, 352, 32, 32), (256 + 192, 352, 32, 32),
        (256 + 32, 352, 32, 32), (256 + 96, 352, 32, 32), (256 + 160, 352, 32, 32), (256 + 224, 352, 32, 32),
        (576, 288, 32, 32)
    )
    enemy1_sprite_start = player2_sprite_end
    enemy1_sprite_end = enemy1_sprite_start + 33

    enemy2_sprite_list = (
        (256 + 0, 0, 32, 32), (256 + 64, 0, 32, 32), (256 + 128, 0, 32, 32), (256 + 192, 0, 32, 32),
        (256 + 32, 0, 32, 32), (256 + 96, 0, 32, 32), (256 + 160, 0, 32, 32), (256 + 224, 0, 32, 32),
        (256 + 0, 32, 32, 32), (256 + 64, 32, 32, 32), (256 + 128, 32, 32, 32), (256 + 192, 32, 32, 32),
        (256 + 32, 32, 32, 32), (256 + 96, 32, 32, 32), (256 + 160, 32, 32, 32), (256 + 224, 32, 32, 32),
        (256 + 0, 64, 32, 32), (256 + 64, 64, 32, 32), (256 + 128, 64, 32, 32), (256 + 192, 64, 32, 32),
        (256 + 32, 64, 32, 32), (256 + 96, 64, 32, 32), (256 + 160, 64, 32, 32), (256 + 224, 64, 32, 32),
        (256 + 0, 96, 32, 32), (256 + 64, 96, 32, 32), (256 + 128, 96, 32, 32), (256 + 192, 96, 32, 32),
        (256 + 32, 96, 32, 32), (256 + 96, 96, 32, 32), (256 + 160, 96, 32, 32), (256 + 224, 96, 32, 32),
        (576, 288, 32, 32)
    )
    enemy2_sprite_start = enemy1_sprite_end
    enemy2_sprite_end = enemy2_sprite_start + 33

    bullet_sprite_list = (
        (644, 204, 8, 8), (660, 204, 8, 8), (676, 204, 8, 8), (692, 204, 8, 8),
        (512, 256, 32, 32), (544, 256, 32, 32), (576, 256, 32, 32)
    )
    bullet_sprite_start = enemy2_sprite_end
    bullet_sprite_end = bullet_sprite_start + 7

    shield_sprite_list = (
        (512, 288, 32, 32), (544, 288, 32, 32)
    )
    shield_sprite_start = bullet_sprite_end
    shield_sprite_end = shield_sprite_start + 2

    blast_sprite_list = (
        (608, 256, 64, 64), (672, 256, 64, 64)
    )
    blast_sprite_start = shield_sprite_end
    blast_sprite_end = blast_sprite_start + 2

    obstacle_start_val_x = 16 * 32
    obstacle_start_val_y = 4 * 32
    obstacle_sprite_list = (
        (512, 128, 16, 16), (544, 136, 16, 8), (536, 128, 8, 16), (576, 128, 16, 8), (560, 128, 8, 16),  # bricks
        (512, 144, 16, 16),  # steel
        (544, 64, 32, 32),  # forest
        (576, 64, 32, 32),  # ice
        (544, 96, 32, 32), (576, 96, 32, 32)  # ocean
    )
    obstacle_brick_sprite_start = blast_sprite_end
    obstacle_brick_sprite_end = obstacle_brick_sprite_start + 5
    obstacle_steel_sprite = obstacle_brick_sprite_end
    obstacle_forest_sprite = obstacle_steel_sprite + 1
    obstacle_ice_sprite = obstacle_forest_sprite + 1
    obstacle_ocean_sprite_start = obstacle_ice_sprite + 1
    obstacle_ocean_sprite_end = obstacle_ocean_sprite_start + 2

    bird_sprite_list = (
        (608, 64, 32, 32), (640, 64, 32, 32)
    )
    bird_sprite_start = obstacle_ocean_sprite_end
    bird_sprite_end = bird_sprite_start + 2

    reward_sprite_list = (
        (512, 222, 32, 32), (544, 222, 32, 32), (576, 222, 32, 32),
        (608, 222, 32, 32), (640, 222, 32, 32), (672, 222, 32, 32),
        (704, 222, 32, 32)
    )
    reward_shield_sprite = bird_sprite_end
    reward_freeze_sprite = reward_shield_sprite + 1
    reward_fortify_sprite = reward_freeze_sprite + 1
    reward_upgrade_sprite = reward_fortify_sprite + 1
    reward_blast_sprite = reward_upgrade_sprite + 1
    reward_life_sprite = reward_blast_sprite + 1
    reward_empty_sprite = reward_life_sprite + 1

    stat_sprite_list = (
        (752, 272, 32, 144), (640, 384, 16, 16),
        (656, 368, 16, 16), (672, 368, 16, 16), (688, 368, 16, 16), (704, 368, 16, 16), (720, 368, 16, 16),
        (656, 384, 16, 16), (672, 384, 16, 16), (688, 384, 16, 16), (704, 384, 16, 16), (720, 384, 16, 16),
    )
    stat_pallet_sprite = reward_empty_sprite + 1
    stat_enemy_sprite = stat_pallet_sprite + 1
    stat_num_sprite_start = stat_enemy_sprite + 1
    stat_num_sprite_end = stat_num_sprite_start + 10

    all_sprite_list = sprite_rescale(
        player1_sprite_list +
        player2_sprite_list +
        enemy1_sprite_list +
        enemy2_sprite_list +
        bullet_sprite_list +
        shield_sprite_list +
        blast_sprite_list +
        obstacle_sprite_list +
        bird_sprite_list +
        reward_sprite_list +
        stat_sprite_list,
        new_scale=resolution_scale
    )

    image_library = ss.images_at(all_sprite_list, color_key=color_key)
    scaling_ratio = block_size / (16 * resolution_scale)
    for i in range(len(image_library)):
        image_library[i] = pg.transform.scale(image_library[i],
                                              (int(scaling_ratio * image_library[i].get_width()),
                                               int(scaling_ratio * image_library[i].get_height())))

    return image_library,\
        player1_sprite_start, player1_sprite_end, \
        player2_sprite_start, player2_sprite_end, \
        enemy1_sprite_start, enemy1_sprite_end, \
        enemy2_sprite_start, enemy2_sprite_end, \
        bullet_sprite_start, bullet_sprite_end, \
        shield_sprite_start, shield_sprite_end, \
        blast_sprite_start, blast_sprite_end, \
        obstacle_brick_sprite_start, obstacle_brick_sprite_end, \
        obstacle_steel_sprite, obstacle_forest_sprite, obstacle_ice_sprite, \
        obstacle_ocean_sprite_start, obstacle_ocean_sprite_end, \
        bird_sprite_start, bird_sprite_end, \
        reward_shield_sprite, reward_freeze_sprite, reward_fortify_sprite, \
        reward_upgrade_sprite, reward_blast_sprite, reward_life_sprite, reward_empty_sprite, \
        stat_pallet_sprite, stat_enemy_sprite, \
        stat_num_sprite_start, stat_num_sprite_end


def sprite_rescale(sprite_list, new_scale):
    new_sprite_list = []
    for item_ in list(sprite_list):
        mod_list = []
        for element_ in list(item_):
            mod_list.append(new_scale * element_)
        new_sprite_list.append(mod_list)
    return tuple(new_sprite_list)
