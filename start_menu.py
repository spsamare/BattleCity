from init import *
import numpy as np

title_x = 5 * BLOCK_SIZE
title_y = 2 * BLOCK_SIZE

start_x = 7
start_y = 12
stage_plus = ((start_x + 7) * BLOCK_SIZE, start_y * BLOCK_SIZE)
stage_x = start_x + 8
stage_y = start_y
stage_minus = ((start_x + 11) * BLOCK_SIZE, start_y * BLOCK_SIZE)
stage_ok = ((start_x + 13) * BLOCK_SIZE, start_y * BLOCK_SIZE)

diff_one = (start_x * BLOCK_SIZE, (start_y + 2) * BLOCK_SIZE)
diff_easy = ((start_x + 7) * BLOCK_SIZE, (start_y + 2) * BLOCK_SIZE)
diff_two = ((start_x + 8) * BLOCK_SIZE, (start_y + 2) * BLOCK_SIZE)
diff_hard = ((start_x + 14) * BLOCK_SIZE, (start_y + 2) * BLOCK_SIZE)
diff_three = ((start_x + 15) * BLOCK_SIZE, (start_y + 2) * BLOCK_SIZE)

boost_one = (start_x * BLOCK_SIZE, (start_y + 4) * BLOCK_SIZE)
boost_no = ((start_x + 7) * BLOCK_SIZE, (start_y + 4) * BLOCK_SIZE)
boost_two = ((start_x + 8) * BLOCK_SIZE, (start_y + 4) * BLOCK_SIZE)
boost_yes = ((start_x + 14) * BLOCK_SIZE, (start_y + 4) * BLOCK_SIZE)
boost_three = ((start_x + 15) * BLOCK_SIZE, (start_y + 4) * BLOCK_SIZE)

info_x = 9 * BLOCK_SIZE
info_y = (start_y + 7) * BLOCK_SIZE


class StartMenu:
    def __init__(self, max_stages=1):
        self.numbers = image_library[stat_num_sprite_start:stat_num_sprite_end]
        self.plus = image_library[display_fourth_start]
        self.minus = image_library[display_fourth_start + 1]
        self.ok = image_library[display_fourth_start + 2]
        self.selectors = pg.sprite.Group()
        self.done = False
        #
        self.title_sprite = image_library[display_title]
        self.title_holder = self.title_sprite.get_rect(topleft=(title_x, title_y))
        self.info_sprite = image_library[display_title + 1]
        self.info_holder = self.info_sprite.get_rect(topleft=(info_x, info_y))
        #
        self.stage = 1
        self.stage_max = max_stages
        self.stage_fixed_pallet_image = [
            image_library[display_first_start],  # stage
            self.plus,
            self.minus,
            self.ok
        ]
        self.stage_pallet = [
            self.stage_fixed_pallet_image[0].get_rect(topleft=(start_x * BLOCK_SIZE, start_y * BLOCK_SIZE)),
            self.plus.get_rect(topleft=stage_plus),
            self.minus.get_rect(topleft=stage_minus),
            self.ok.get_rect(topleft=stage_ok)
        ]
        self.stage_num_pallet = [
            self.numbers[0].get_rect(topleft=(stage_x * BLOCK_SIZE, stage_y * BLOCK_SIZE)),
            self.numbers[0].get_rect(topleft=((stage_x + 1) * BLOCK_SIZE, stage_y * BLOCK_SIZE)),
            self.numbers[0].get_rect(topleft=((stage_x + 2) * BLOCK_SIZE, stage_y * BLOCK_SIZE))
        ]
        self.stage_done = False
        self.stage_select = Selector(xy_vals=[stage_plus, stage_minus, stage_ok], default_pos=2)
        self.selectors.add(self.stage_select)
        #
        self.is_difficult = False
        self.difficult_pallet_image = [
            image_library[display_third_start + 1],
            self.ok,
            image_library[display_third_start + 2],
            self.ok,
            image_library[display_third_start + 3]
        ]
        self.difficult_pallet = [
            self.difficult_pallet_image[0].get_rect(topleft=diff_one),
            self.ok.get_rect(topleft=diff_easy),
            self.difficult_pallet_image[1].get_rect(topleft=diff_two),
            self.ok.get_rect(topleft=diff_hard),
            self.difficult_pallet_image[2].get_rect(topleft=diff_three)
        ]
        self.difficult_select = None
        self.difficult_done = False
        #
        self.is_boost = False
        self.boost_pallet_image = [
            image_library[display_third_start],
            self.ok,
            image_library[display_third_start + 2],
            self.ok,
            image_library[display_third_start + 3]
        ]
        self.boost_pallet = [
            self.boost_pallet_image[0].get_rect(topleft=boost_one),
            self.ok.get_rect(topleft=boost_no),
            self.boost_pallet_image[1].get_rect(topleft=boost_two),
            self.ok.get_rect(topleft=boost_yes),
            self.boost_pallet_image[2].get_rect(topleft=boost_three)
        ]
        self.boost_select = None
        self.boost_done = False

    def update(self, e=None):
        if not self.stage_done:
            pos_change = 0
            if e == 'R':
                pos_change = 1
            if e == 'L':
                pos_change = -1
            if e == 'E':
                if self.stage_select.pos == 0:
                    self.stage = np.minimum(self.stage + 1, self.stage_max)
                elif self.stage_select.pos == 1:
                    self.stage = np.maximum(self.stage - 1, 1)
                else:
                    self.stage_done = True
                    self.difficult_select = Selector(xy_vals=[diff_easy, diff_hard], default_pos=0)
                    self.selectors.add(self.difficult_select)
            self.stage_select.update(pos_change=pos_change)
        elif not self.difficult_done:
            pos_change = 0
            if e == 'R':
                pos_change = 1
            if e == 'L':
                pos_change = -1
            if e == 'E':
                self.is_difficult = True if self.difficult_select.pos == 0 else False
                self.difficult_done = True
                self.boost_select = Selector(xy_vals=[boost_no, boost_yes], default_pos=0)
                self.selectors.add(self.boost_select)
            self.difficult_select.update(pos_change=pos_change)
        elif not self.boost_done:
            pos_change = 0
            if e == 'R':
                pos_change = 1
            if e == 'L':
                pos_change = -1
            if e == 'E':
                self.is_boost = True if self.boost_select.pos == 1 else False
                self.boost_done = True
            self.boost_select.update(pos_change=pos_change)
        else:
            self.done = True

    def draw(self):
        # Title
        SCREEN.blit(self.title_sprite, self.title_holder)
        # Info
        SCREEN.blit(self.info_sprite, self.info_holder)
        # stage
        pg.draw.rect(SCREEN, COLORS['static'],
                     ((start_x - 1) * BLOCK_SIZE, (start_y - 1) * BLOCK_SIZE, 21 * BLOCK_SIZE, 7 * BLOCK_SIZE), 0)
        for i in range(4):
            SCREEN.blit(self.stage_fixed_pallet_image[i], self.stage_pallet[i])
        this_stage = [int(dig) for dig in str(self.stage).zfill(3)]
        for i in range(3):
            SCREEN.blit(self.numbers[this_stage[i]], self.stage_num_pallet[i])
        # difficulty
        for i in range(5):
            SCREEN.blit(self.difficult_pallet_image[i], self.difficult_pallet[i])
        # boost
        for i in range(5):
            SCREEN.blit(self.boost_pallet_image[i], self.boost_pallet[i])
        self.selectors.draw(SCREEN)


class Selector(pg.sprite.Sprite):
    def __init__(self, xy_vals, default_pos=0):
        super().__init__()
        self.images = image_library[display_fourth_start + 3: display_fourth_start + 5]
        self.positions = [
            xy for xy in xy_vals
        ]
        self.pos = default_pos
        self.rect = self.images[0].get_rect(topleft=self.positions[self.pos])
        self.is_blinking = True
        self.state = 0
        self.image = self.images[self.state]
        self.blink_count_max = FPS // 2
        self.blink_count = 0

    def update(self, pos_change=0):
        if self.is_blinking:
            self.pos = np.maximum(np.minimum(self.pos + pos_change, len(self.positions) - 1), 0)
            self.rect.topleft = self.positions[self.pos]
            if self.blink_count < self.blink_count_max:
                self.blink_count += 1
            else:
                self.blink_count = 0
                self.state = 1 - self.state
                self.image = self.images[self.state]

    def done(self):
        self.is_blinking = False
        self.image = self.images[0]
