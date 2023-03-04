import pygame as pg
import os


def my_path(filename):
    sound_path = 'res/sounds/'
    return pg.mixer.Sound(os.path.join(sound_path, filename))


pg.mixer.init()

s_fire = pg.mixer.Sound(my_path('fire_player.wav'))
# s_fire.set_volume(1.0)
#
s_hit_steel = pg.mixer.Sound(my_path('hit_steel.wav'))
# s_hit_steel.set_volume(1.0)
#
s_hit_brick = pg.mixer.Sound(my_path('hit_brick.wav'))
# s_hit_brick.set_volume(1.0)
#
s_hit_enemy = [
    pg.mixer.Sound(my_path('hit_1.wav')),
    pg.mixer.Sound(my_path('hit_2.wav')),
    pg.mixer.Sound(my_path('hit_3.wav'))
    ]
#
s_e_destroy = pg.mixer.Sound(my_path('destroy_enemy.wav'))
s_p_destroy = pg.mixer.Sound(my_path('destroy_player.wav'))
#
s_reward_appear = pg.mixer.Sound(my_path('reward_appear.wav'))
s_reward_life = pg.mixer.Sound(my_path('reward_life.wav'))
s_reward_star = pg.mixer.Sound(my_path('reward_star.wav'))
s_reward_fortify = pg.mixer.Sound(my_path('reward_1000.wav'))
# s_hit_steel.set_volume(1.0)
#
s_idle = pg.mixer.Sound(my_path('player_idle.wav'))
# s_idle.set_volume(.5)
#
s_move = pg.mixer.Sound(my_path('player_move.wav'))
# s_move.set_volume(.5)
#
