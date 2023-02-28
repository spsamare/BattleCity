from init import *
import numpy as np

TIMERS = {
    'player_immortal': 5 * FPS,
    'enemy_immortal': 2 * FPS,
    'reward_immortal': 10 * FPS,
    'freeze': 10 * FPS,
    'reward_duration': 15 * FPS,
    'blink': FPS // 2,
    'enemy_respawn_normal': 10 * FPS,
    'enemy_respawn_urgent': 3 * FPS,
    'enemy_spawn_delay': 2 * FPS,
    'fortify_duration': 20 * FPS,
    'delay_next_stage': 5 * FPS
}

SPEED = {
    'move': BLOCK_SIZE / 2,
    'move_delay': 10,
    'bullet': BLOCK_SIZE,
    'bullet_delay': 5,
    'bullet_interval': 2 * FPS
}

STATES = {
    'ongoing': 0,
    'win': 1,
    'loose': 2,
    'paused': 3
}

GUARD = {
    'locations': [
        (11 * BLOCK_SIZE, 25 * BLOCK_SIZE), (11 * BLOCK_SIZE, 24 * BLOCK_SIZE),
        (11 * BLOCK_SIZE, 23 * BLOCK_SIZE), (12 * BLOCK_SIZE, 23 * BLOCK_SIZE),
        (13 * BLOCK_SIZE, 23 * BLOCK_SIZE), (14 * BLOCK_SIZE, 23 * BLOCK_SIZE),
        (14 * BLOCK_SIZE, 24 * BLOCK_SIZE), (14 * BLOCK_SIZE, 25 * BLOCK_SIZE),
    ]
}


class Tank(pg.sprite.Sprite):
    def __init__(self, pos, game_area_, images, level=0):
        super().__init__()
        self.rect = pg.Rect(0, 0, 2 * BLOCK_SIZE, 2 * BLOCK_SIZE)
        self.image_state = True
        #
        self.start_pos = pos
        self.rect.topleft = pos
        self.direction = DIRECTION["N"]
        self.game_area = game_area_
        self.speed = SPEED['move']
        self.move_count = 0
        self.move_count_max = SPEED['move_delay']
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.speed_x = 0.
        self.speed_y = 0.
        #
        self.images = images
        self.image = images[self.direction]
        #
        self.obstacles = None  # pg.sprite.Group()
        self.bullet_exceptions = pg.sprite.Group()
        self.bullet_list = None
        #
        self.shoot_count = 0
        self.shoot_count_max = SPEED['bullet_interval']
        self.shoot_speed = 1.0
        #
        self.hit_by = None
        self.lives = 1
        self.is_alive = True
        self.respawn_counter = 0
        #
        self.is_player = False
        self.immortal_timer = TIMERS['enemy_immortal']
        self.immortal = True
        self.has_shield = False
        #
        self.partners = None
        self.opponents = None
        #
        self.rewards = None
        self.reward_eligible = False
        self.frozen = False
        self.frozen_counter = 0
        #
        self.ice_areas = None
        self.reward_fortify_picked = False
        #
        if level > 0:
            self.level = level - 1
            self.level_change(1)
        else:
            self.level = 0

    def update(self):
        if self.is_alive:
            if self.hit_by is None or self.immortal is True:
                if self.shoot_count > 0:
                    self.shoot_count = (self.shoot_count + 1) % self.shoot_count_max
                if self.level == 3 and self.shoot_count == 10:
                    bullet_ = Bullet(self, self.game_area)
                    self.groups()[0].add(bullet_)
                    # self.obstacles.add(bullet_)
                #
                if self.immortal_timer > 0:
                    self.immortal = True
                    self.hit_by = None
                    if not self.has_shield:
                        self.groups()[0].add(Shield(self, self.game_area))
                        self.has_shield = True
                    self.immortal_timer -= 1
                else:
                    self.immortal = False
                    self.has_shield = False
                self.automate()
            else:
                self.blast()
        else:
            if self.lives > 0:
                self.respawn_counter -= 1
                if self.respawn_counter == 0:
                    self.spawn()
            else:
                self.kill()

    def automate(self):
        pass

    def move(self):
        if self.move_count == 0:
            self.x = self.rect.centerx
            self.y = self.rect.centery
        self.rect.centery = self.y + self.speed_y * (self.move_count + 1) / self.move_count_max
        self.rect.centerx = self.x + self.speed_x * (self.move_count + 1) / self.move_count_max
        self.move_count += 1
        if self.move_count == self.move_count_max:
            self.move_count = 0

    def animate(self):
        self.image = self.images[self.level * 8 + self.direction + 4 * self.image_state]
        self.image_state = not self.image_state

    def can_move(self, x, y):
        status = True
        old_position = self.rect.center
        self.rect.centery += y
        self.rect.centerx += x
        # len(pg.sprite.spritecollide(self, self.partners, dokill=False)) > 1 or \
        if not self.game_area.contains(self.rect) or \
                pg.sprite.spritecollideany(self, self.obstacles) is not None or \
                len(pg.sprite.spritecollide(self, self.partners, dokill=False)) > 1 or \
                pg.sprite.spritecollideany(self, self.opponents) is not None:
            status = False
        elif self.reward_eligible is True:
            reward_ = pg.sprite.spritecollide(self, self.rewards, dokill=True)
            if len(reward_) > 0:
                self.grant_reward(reward_[0].name)
        self.rect.center = old_position
        return status

    def level_change(self, change=1):
        if change > 0:
            self.level = min(self.level + 1, 3)
        else:
            self.level = max(self.level - 1, 0)
        # print(self.level)
        self.image = self.images[self.level * 8 + self.direction]
        if self.level == 3:
            self.shoot_count_max = SPEED['bullet_interval'] // 2
            self.shoot_speed = 1.0
            self.move_count_max = SPEED['move_delay'] - 2
        elif self.level == 2:
            self.shoot_count_max = SPEED['bullet_interval'] // 2
            self.shoot_speed = 1.0
            self.move_count_max = SPEED['move_delay'] - 2
        elif self.level == 1:
            self.shoot_count_max = 3 * SPEED['bullet_interval'] // 4
            self.shoot_speed = 1.0
            self.move_count_max = SPEED['move_delay']
        else:
            self.shoot_count_max = SPEED['bullet_interval']
            self.shoot_speed = 1.0
            self.move_count_max = SPEED['move_delay']
        # print(self.level)

    def shoot(self):
        if self.shoot_count == 0:
            bullet_ = Bullet(self, self.game_area)
            self.groups()[0].add(bullet_)
            self.bullet_list.add(bullet_)
            self.shoot_count += 1

    def blast(self):
        self.hit_by = None
        if self.level > 0:
            self.level_change(change=0)
        else:
            self.is_alive = False
            self.lives = max(self.lives - 1, 0)
            self.respawn_counter = FPS
            self.image = self.images[-1]
            self.groups()[0].add(Blast(self, self.game_area))

    def spawn(self, direction=DIRECTION["N"]):
        self.rect.topleft = self.start_pos
        self.direction = direction
        self.image = self.images[self.direction]
        #
        self.move_count = 0
        self.shoot_count = 0
        self.is_alive = True
        self.respawn_counter = 0
        #
        self.immortal_timer = 5 * FPS
        self.immortal = True
        self.has_shield = False

    def grant_reward(self, reward_name):
        if reward_name == 'shield':
            self.immortal = True
            self.immortal_timer = TIMERS['reward_immortal']
        elif reward_name == 'upgrade':
            self.level_change()
        elif reward_name == 'life':
            self.lives += 1
        elif reward_name == 'freeze':
            for opponent in self.opponents:
                opponent.frozen = True
        elif reward_name == 'blast':
            for opponent in self.opponents:
                opponent.hit_by = self
        else:  # fortify
            self.reward_fortify_picked = True


class Enemy(Tank):
    def __init__(self, pos, game_area_, images=image_library[enemy1_sprite_start:enemy1_sprite_end],
                 level=0):
        super().__init__(pos, game_area_, images, level)
        #
        self.direction = DIRECTION["S"]
        self.image = images[self.direction]
        #
        self.level = level
        #
        self.probability = [
            [.2, .4, .4],  # stay [0], continue [1], change [2]
            [.2, .8, .0]
        ]
        self.inertia_state = 0
        self.shoot_probability = .5
        #
        # if shine is True:
        #    self.start_countdown = TIMERS['enemy_spawn_delay']
        #    self.groups()[0].add(Shine(self, self.game_area))

    def update(self):
        if self.is_alive:
            if self.hit_by is None or self.immortal is True:
                if self.shoot_count > 0:
                    self.shoot_count = (self.shoot_count + 1) % self.shoot_count_max
                if self.level == 3 and self.shoot_count == 10:
                    bullet_ = Bullet(self, self.game_area)
                    self.groups()[0].add(bullet_)
                    # self.obstacles.add(bullet_)
                #
                if self.immortal_timer > 0:
                    self.immortal = True
                    self.hit_by = None
                    if not self.has_shield:
                        self.groups()[0].add(Shine(self, self.game_area))
                        self.has_shield = True
                    self.immortal_timer -= 1
                    self.image = self.images[-1]
                else:
                    self.immortal = False
                    self.has_shield = False
                    self.automate()
            else:
                self.blast()
        else:
            if self.lives > 0:
                self.respawn_counter -= 1
                if self.respawn_counter == 0:
                    self.spawn()
            else:
                self.kill()

    def automate(self):
        if self.frozen is True:
            self.frozen_counter += 1
            if self.frozen_counter >= TIMERS['freeze']:
                self.frozen = False
                self.frozen_counter = 0
        else:
            old_direction = self.direction
            key_pressed = False
            if self.move_count == 0:
                self.speed_y = 0
                self.speed_x = 0
                mobility_choice = np.random.choice(3, 1,
                                                   p=self.probability[np.minimum(self.inertia_state, 1)])
                if mobility_choice[0] > 0:
                    if mobility_choice[0] == 2:  # change the current course
                        self.direction = (self.direction + np.random.randint(1, 4)) % 4
                        self.inertia_state = 10
                    else:
                        self.inertia_state = np.maximum(self.inertia_state - 1, 0)
                    #
                    if self.direction == DIRECTION["N"]:
                        self.speed_y = -1 * self.speed
                        key_pressed = True
                    elif self.direction == DIRECTION["S"]:
                        self.speed_y = self.speed
                        key_pressed = True
                    elif self.direction == DIRECTION["E"]:
                        self.speed_x = self.speed
                        key_pressed = True
                    elif self.direction == DIRECTION["W"]:
                        self.speed_x = -1 * self.speed
                        key_pressed = True
                #
                if np.random.random(1) < self.shoot_probability:
                    self.shoot()

            if old_direction == self.direction:
                if key_pressed:
                    self.animate()
                    if self.can_move(self.speed_x, self.speed_y):
                        self.move()
                elif self.move_count > 0:
                    self.move()
                    self.animate()
            else:
                self.image = self.images[self.level * 8 + self.direction]

    def spawn(self, direction=DIRECTION["S"]):
        super().spawn(direction)


class EnemySpecial(Enemy):
    def __init__(self, pos, game_area_, images=image_library[enemy1_sprite_start:enemy1_sprite_end], level=0):
        super().__init__(pos, game_area_, images, level)
        self.image_sets = [
            image_library[enemy1_sprite_start:enemy1_sprite_end],
            image_library[enemy2_sprite_start:enemy2_sprite_end]
        ]
        self.image_blink = 0
        self.image_blink_counter = 0
        self.move_count_max = SPEED['move_delay'] - 4

    def update(self):
        super().update()
        if self.image_blink_counter < TIMERS['blink']:
            self.image_blink_counter += 1
        else:
            self.image_blink_counter = 0
            self.image_blink = 1 - self.image_blink
            self.images = self.image_sets[self.image_blink]

    def blast(self):
        super().blast()
        this_choice = np.random.choice(range(6), 1, p=REWARD_PROBABILITY)[0]
        this_x = np.random.randint(0, 13, 1)[0]
        this_y = np.random.randint(1, 12, 1)[0]
        # print(this_choice, this_x, this_y)
        if this_choice == 0:
            self.rewards.add(RewardShield(pos=(2 * this_x * BLOCK_SIZE, 2 * this_y * BLOCK_SIZE)))
        elif this_choice == 1:
            self.rewards.add(RewardFreeze(pos=(2 * this_x * BLOCK_SIZE, 2 * this_y * BLOCK_SIZE)))
        elif this_choice == 2:
            self.rewards.add(RewardFortify(pos=(2 * this_x * BLOCK_SIZE, 2 * this_y * BLOCK_SIZE)))
        elif this_choice == 3:
            self.rewards.add(RewardUpgrade(pos=(2 * this_x * BLOCK_SIZE, 2 * this_y * BLOCK_SIZE)))
        elif this_choice == 4:
            self.rewards.add(RewardBlast(pos=(2 * this_x * BLOCK_SIZE, 2 * this_y * BLOCK_SIZE)))
        else:
            self.rewards.add(RewardLife(pos=(2 * this_x * BLOCK_SIZE, 2 * this_y * BLOCK_SIZE)))


class Player(Tank):
    def __init__(self, pos, game_area_, images, level=0, key_set=KEYS1):
        super().__init__(pos, game_area_, images, level)
        #
        self.direction = DIRECTION["N"]
        self.image = images[self.direction]
        #
        self.lives = 2
        self.immortal_timer = TIMERS['player_immortal']
        #
        self.is_player = True
        self.keys = key_set
        #
        self.reward_eligible = True

    def control(self, key):
        if self.frozen is True:
            self.frozen_counter += 1
            if self.frozen_counter >= TIMERS['freeze']:
                self.frozen = False
                self.frozen_counter = 0
        else:
            if self.is_alive:
                old_direction = self.direction
                key_pressed = False
                if self.move_count == 0:
                    self.speed_y = 0
                    self.speed_x = 0
                    if key[self.keys["N"]] == 1:
                        self.direction = DIRECTION["N"]
                        self.speed_y = -1 * self.speed
                        key_pressed = True
                    elif key[self.keys["S"]] == 1:
                        self.direction = DIRECTION["S"]
                        self.speed_y = self.speed
                        key_pressed = True
                    elif key[self.keys["E"]] == 1:
                        self.direction = DIRECTION["E"]
                        self.speed_x = self.speed
                        key_pressed = True
                    elif key[self.keys["W"]] == 1:
                        self.direction = DIRECTION["W"]
                        self.speed_x = -1 * self.speed
                        key_pressed = True
                #
                if key[self.keys["F"]] == 1:
                    self.shoot()

                if old_direction == self.direction:
                    if key_pressed:
                        self.animate()
                        if self.can_move(self.speed_x, self.speed_y):
                            self.move()
                    elif self.move_count > 0:
                        self.move()
                        self.animate()
                else:
                    self.image = self.images[self.level * 8 + self.direction]

    def spawn(self, direction=DIRECTION["N"]):
        super().spawn(direction)
        self.immortal_timer = TIMERS['player_immortal']


class Obstacle(pg.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        if isinstance(image, list):
            self.image = image[0]
        else:
            self.image = image
        self.rect = self.image.get_rect(topleft=pos)


class Brick(Obstacle):
    def __init__(self, pos, image=image_library[obstacle_brick_sprite_start:obstacle_brick_sprite_end], num=0):
        super().__init__(pos, image)
        self.images = image
        self.image = self.images[num]
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_by = None
        if num > 0:
            self.hit_direction = num - 1
            self.number = 0
            self.brick_break()
        else:
            self.hit_direction = None
            self.number = num

    def update(self):
        if self.hit_by is not None:
            self.hit_direction = (self.hit_by.direction + 2) % 4  # translate into self PoV
            self.brick_break()

    def brick_break(self):
        if self.number == 0:  # First hit
            self.number = self.hit_direction + 1
            self.image = self.images[self.number]
            if self.hit_direction == DIRECTION['N']:
                self.rect.update(self.rect.left, self.rect.top + BLOCK_SIZE / 2,
                                 self.rect.width, self.rect.height / 2)
            elif self.hit_direction == DIRECTION['W']:
                self.rect.update(self.rect.left + BLOCK_SIZE / 2, self.rect.top,
                                 self.rect.width / 2, self.rect.height)
            elif self.hit_direction == DIRECTION['S']:
                self.rect.update(self.rect.left, self.rect.top,
                                 self.rect.width, self.rect.height / 2)
            else:
                self.rect.update(self.rect.left, self.rect.top,
                                 self.rect.width / 2, self.rect.height)
            self.hit_direction = None
            self.hit_by = None
        else:
            self.kill()


class Bird(Obstacle):
    def __init__(self, pos, image=image_library[bird_sprite_start:bird_sprite_end]):
        super().__init__(pos, image)
        self.images = image
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_by = None
        self.round = None

    def update(self):
        if self.hit_by is not None:
            self.image = self.images[1]
            self.round.failed()


class Steel(Obstacle):
    def __init__(self, pos, image=image_library[obstacle_steel_sprite]):
        super().__init__(pos, image)


class Forest(Obstacle):
    def __init__(self, pos, image=image_library[obstacle_forest_sprite]):
        super().__init__(pos, image)


class Ice(Obstacle):
    def __init__(self, pos, image=image_library[obstacle_ice_sprite]):
        super().__init__(pos, image)


class Ocean(Obstacle):
    def __init__(self, pos, image=image_library[obstacle_ocean_sprite_start:obstacle_ocean_sprite_end]):
        super().__init__(pos, image)
        self.images = image
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.anim_count = 0

    def update(self):
        self.anim_count = (self.anim_count + 1) % (2 * FPS)
        self.image = self.images[self.anim_count // FPS]


class Bullet(pg.sprite.Sprite):
    def __init__(self, owner, game_area_, images=image_library[bullet_sprite_start:bullet_sprite_end]):
        super().__init__()
        self.rect = pg.Rect(0, 0, .75 * BLOCK_SIZE, .75 * BLOCK_SIZE)
        self.images = images
        self.image = self.images[owner.direction]
        self.alive = True
        self.rect.center = owner.rect.center
        self.direction = owner.direction
        self.game_area = game_area_
        self.speed = owner.shoot_speed * SPEED['bullet']
        self.move_count = 0
        self.move_count_max = SPEED['bullet_delay']
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.speed_x = 0.
        self.speed_y = 0.
        self.set_speed()
        self.obstacles = owner.obstacles.copy()
        self.bullet_list = owner.bullet_list
        # self.obstacles.add(owner.partners.copy())
        self.obstacles.add(owner.opponents)
        self.obstacles.remove(owner.bullet_exceptions)
        self.hit_by = None

    def set_speed(self):
        if self.direction == DIRECTION["N"]:
            self.speed_y = -1.0
        elif self.direction == DIRECTION["S"]:
            self.speed_y = 1.0
        elif self.direction == DIRECTION["E"]:
            self.speed_x = 1.0
        else:
            self.speed_x = -1.0
        self.rect.centerx += self.speed_x * self.speed
        self.rect.centery += self.speed_y * self.speed

    def update(self):
        if self.alive:
            if self.move_count == 0:
                self.x = self.rect.centerx
                self.y = self.rect.centery
            self.rect.centery = self.y + self.speed_y * self.speed * (self.move_count + 1) / self.move_count_max
            self.rect.centerx = self.x + self.speed_x * self.speed * (self.move_count + 1) / self.move_count_max
            self.move_count += 1
            if self.move_count == self.move_count_max:
                self.move_count = 0
            if not self.game_area.contains(self.rect):
                self.kill_animate()
            else:
                collided_sprite = pg.sprite.spritecollideany(self, self.obstacles)
                if collided_sprite is not None:
                    # collided_sprite.hit_direction = (self.direction + 2) % 4
                    collided_sprite.hit_by = self
                    self.kill_animate()
                collided_bullet = pg.sprite.spritecollide(self, self.bullet_list, dokill=False)
                if len(collided_bullet) > 1:
                    for bullets in collided_bullet:
                        bullets.hit_by = self
                    self.disappear()
                if self.hit_by is not None:
                    self.disappear()
        else:
            if self.move_count == self.move_count_max:
                self.kill()
            else:
                self.move_count += 1
                self.image = self.images[4 + 2 * self.move_count // self.move_count_max]

    def kill_animate(self):
        old_position = self.rect.center
        self.rect = pg.Rect(0, 0, 2 * BLOCK_SIZE, 2 * BLOCK_SIZE)
        self.rect.center = old_position
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.image = self.images[4]
        self.speed_y = 0.
        self.speed_x = 0.
        self.move_count = 0
        self.alive = False

    def disappear(self):
        self.kill()


class Shield(pg.sprite.Sprite):
    def __init__(self, owner, game_area_, images=image_library[shield_sprite_start:shield_sprite_end]):
        super().__init__()
        self.rect = pg.Rect(0, 0, 2 * BLOCK_SIZE, 2 * BLOCK_SIZE)
        self.images = images
        self.image_count = 0
        self.image = self.images[self.image_count]
        self.owner = owner
        self.rect.center = owner.rect.center
        self.game_area = game_area_

    def update(self):
        if self.owner.immortal_timer > 0:
            self.rect.center = self.owner.rect.center
            if (10 * self.owner.immortal_timer) % FPS == 0:
                self.image_count = (self.image_count + 1) % 2
            self.image = self.images[self.image_count]
        else:
            self.kill()


class Shine(pg.sprite.Sprite):
    def __init__(self, owner, game_area_, images=image_library[shine_sprite_start:shine_sprite_end]):
        super().__init__()
        self.images = images
        self.image_count = 0
        self.image = self.images[self.image_count]
        self.rect = self.image.get_rect()
        self.owner = owner
        self.rect.center = owner.rect.center
        self.game_area = game_area_
        self.timer = TIMERS['enemy_spawn_delay']
        self.order = [0, 1, 2, 3, 2, 1]

    def update(self):
        if self.timer > 0:
            self.rect.center = self.owner.rect.center
            if (12 * self.timer) % FPS == 0:
                self.image_count = (self.image_count + 1) % 6
            self.image = self.images[self.order[self.image_count]]
            self.timer -= 1
        else:
            self.kill()


class Blast(pg.sprite.Sprite):
    def __init__(self, owner, game_area_, images=image_library[blast_sprite_start:blast_sprite_end]):
        super().__init__()
        self.rect = pg.Rect(0, 0, 4 * BLOCK_SIZE, 4 * BLOCK_SIZE)
        self.images = images
        self.anim_count = 0
        self.image = self.images[0]
        self.rect.center = owner.rect.center
        self.game_area = game_area_

    def update(self):
        self.anim_count += 1
        if self.anim_count == FPS // 4:
            self.image = self.images[1]
        if self.anim_count == FPS // 2:
            self.kill()


class Reward(pg.sprite.Sprite):
    def __init__(self, pos, images, name):
        super().__init__()
        self.images = images
        self.image_status = 0
        self.image = self.images[self.image_status]
        self.rect = self.image.get_rect(topleft=pos)
        self.name = name
        self.counter = 0

    def update(self):
        if self.counter < TIMERS['reward_duration']:
            self.counter += 1
            if self.counter % (FPS // 5) == 0:
                self.image_status = 1 - self.image_status
                self.image = self.images[self.image_status]
        else:
            self.kill()


class RewardShield(Reward):
    def __init__(self, pos, images=list(image_library[i] for i in [reward_shield_sprite, reward_empty_sprite]),
                 name='shield'):
        super().__init__(pos, images, name)


class RewardFreeze(Reward):
    def __init__(self, pos, images=list(image_library[i] for i in [reward_freeze_sprite, reward_empty_sprite]),
                 name='freeze'):
        super().__init__(pos, images, name)


class RewardFortify(Reward):
    def __init__(self, pos, images=list(image_library[i] for i in [reward_fortify_sprite, reward_empty_sprite]),
                 name='fortify'):
        super().__init__(pos, images, name)


class RewardUpgrade(Reward):
    def __init__(self, pos, images=list(image_library[i] for i in [reward_upgrade_sprite, reward_empty_sprite]),
                 name='upgrade'):
        super().__init__(pos, images, name)


class RewardBlast(Reward):
    def __init__(self, pos, images=list(image_library[i] for i in [reward_blast_sprite, reward_empty_sprite]),
                 name='blast'):
        super().__init__(pos, images, name)


class RewardLife(Reward):
    def __init__(self, pos, images=list(image_library[i] for i in [reward_life_sprite, reward_empty_sprite]),
                 name='life'):
        super().__init__(pos, images, name)


class Round:
    def __init__(self):
        self.finished = False
        self.state = STATES['ongoing']

    def completed(self):
        self.finished = True
        self.state = STATES['win']

    def failed(self):
        self.finished = True
        self.state = STATES['loose']


class StatBoard:
    def __init__(self, player1, player2, enemy_generator):
        self.images_stat_pallet = image_library[stat_pallet_sprite]
        self.stat_pallet = self.images_stat_pallet.get_rect(topleft=(27 * BLOCK_SIZE, 15 * BLOCK_SIZE))

        self.images_enemy = image_library[stat_enemy_sprite]
        self.images_numbers = image_library[stat_num_sprite_start:stat_num_sprite_end]

        self.player1 = player1
        self.player1_pallet = self.images_numbers[0].get_rect(topleft=(28 * BLOCK_SIZE, 16 * BLOCK_SIZE))

        self.player2 = player2
        self.player2_pallet = self.images_numbers[0].get_rect(topleft=(28 * BLOCK_SIZE, 19 * BLOCK_SIZE))

        self.enemy_generator = enemy_generator
        self.enemy_pallet = self.images_enemy.get_rect()

    def update(self):
        pass

    def draw(self):
        SCREEN.blit(self.images_stat_pallet, self.stat_pallet)
        SCREEN.blit(self.images_numbers[self.player1.lives], self.player1_pallet)
        SCREEN.blit(self.images_numbers[self.player2.lives], self.player2_pallet)
        #
        # print(self.enemy_generator.enemies_remaining)
        for e in range(self.enemy_generator.enemies_remaining):
            self.enemy_pallet.topleft = ((27 + e % 2) * BLOCK_SIZE, (1 + e // 2) * BLOCK_SIZE)
            SCREEN.blit(self.images_enemy, self.enemy_pallet)


class EnemyGenerator:
    def __init__(self, game_area, all_sprites,
                 enemy_group, player_group,
                 obstacle_group, ocean_group,
                 world_bullet_list, all_rewards):
        self.spawn_locations = [
            (0 * BLOCK_SIZE, 0 * BLOCK_SIZE),
            (12 * BLOCK_SIZE, 0 * BLOCK_SIZE),
            (24 * BLOCK_SIZE, 0 * BLOCK_SIZE)
        ]
        self.game_area = game_area
        self.all_sprites = all_sprites
        #
        self.enemy_group = enemy_group
        self.enemies_remaining = ENEMY_COUNT - 3
        self.enemies_active_max = 6
        # self.enemies_active_group = None
        #
        self.player_group = player_group
        self.obstacle_group = obstacle_group
        self.ocean_group = ocean_group
        self.bullet_list = world_bullet_list
        self.rewards = all_rewards
        #
        self.respawn_counter = TIMERS['enemy_respawn_normal']
        #
        enemy1 = Enemy(pos=self.spawn_locations[0], game_area_=self.game_area)
        enemy2 = EnemySpecial(pos=self.spawn_locations[1], game_area_=self.game_area)
        enemy3 = Enemy(pos=self.spawn_locations[2], game_area_=self.game_area)
        self.all_sprites.add(enemy1)
        self.all_sprites.add(enemy2)
        self.all_sprites.add(enemy3)
        #
        self.enemy_group.add(enemy1)
        self.enemy_group.add(enemy2)
        self.enemy_group.add(enemy3)

        for enemy in self.enemy_group:
            enemy.partners = self.enemy_group
            enemy.opponents = self.player_group
            enemy.obstacles = self.obstacle_group  # enemy.obstacles.add(obstacle_group)
            enemy.bullet_exceptions.add(self.ocean_group)
            enemy.bullet_list = self.bullet_list
            enemy.rewards = self.rewards

    def update(self):
        active_number = len(self.enemy_group)
        if self.enemies_remaining > 0:
            if active_number < 3:
                self.respawn_counter = np.minimum(self.respawn_counter - 1, TIMERS['enemy_respawn_urgent'])
            elif active_number < self.enemies_active_max:
                self.respawn_counter = np.minimum(self.respawn_counter - 1,
                                                  np.random.randint(TIMERS['enemy_respawn_urgent'],
                                                                    TIMERS['enemy_respawn_normal']))
            self.spawn(
                level=np.random.choice([0, 1, 2, 3], 1, p=[.5, .3, .15, .05])[0],
                is_special=self.enemies_remaining % 5 == 0
            )

    def spawn(self, level=0, is_special=False, location=None):
        # print(self.respawn_counter)
        if self.respawn_counter < 1:
            if location is None:
                location = np.random.randint(3)
            placeholder = pg.sprite.Sprite()
            placeholder.rect = pg.Rect(self.spawn_locations[location], (2 * BLOCK_SIZE, 2 * BLOCK_SIZE))
            if pg.sprite.spritecollideany(placeholder, self.enemy_group) is None and \
                    pg.sprite.spritecollideany(placeholder, self.player_group) is None:
                enemy = EnemySpecial(pos=self.spawn_locations[location], game_area_=self.game_area, level=level) \
                    if is_special else Enemy(pos=self.spawn_locations[location], game_area_=self.game_area, level=level)
                self.all_sprites.add(enemy)
                self.enemy_group.add(enemy)
                enemy.partners = self.enemy_group
                enemy.opponents = self.player_group
                enemy.obstacles = self.obstacle_group  # enemy.obstacles.add(obstacle_group)
                enemy.bullet_exceptions.add(self.ocean_group)
                enemy.bullet_list = self.bullet_list
                enemy.rewards = self.rewards
                #
                self.enemies_remaining -= 1
                self.respawn_counter = TIMERS['enemy_respawn_normal']
            else:
                self.respawn_counter += FPS // 2
            placeholder.kill()


class StatusDisplay:
    def __init__(self):
        self.text_first_images = image_library[display_first_start:display_second_start]
        self.text_second_images = image_library[display_second_start:display_end]
        self.num_images = image_library[stat_num_sprite_start:stat_num_sprite_end]

        self.back_pallet = pg.Rect((8 * BLOCK_SIZE, 12 * BLOCK_SIZE), (11 * BLOCK_SIZE, 3 * BLOCK_SIZE))
        self.first_pallet = self.text_first_images[0].get_rect(topleft=(9 * BLOCK_SIZE, 13 * BLOCK_SIZE))
        self.second_pallet = [
            self.text_second_images[0].get_rect(topleft=(14 * BLOCK_SIZE, 13 * BLOCK_SIZE)),
            self.text_second_images[0].get_rect(topleft=(15 * BLOCK_SIZE, 13 * BLOCK_SIZE)),
            self.text_second_images[0].get_rect(topleft=(16 * BLOCK_SIZE, 13 * BLOCK_SIZE)),
            self.text_second_images[0].get_rect(topleft=(17 * BLOCK_SIZE, 13 * BLOCK_SIZE))
        ]

    def draw(self, game_state, stage='000'):
        if game_state == STATES['ongoing']:
            # print('test')
            pg.draw.rect(SCREEN, COLORS['static'], self.back_pallet)
            SCREEN.blit(self.text_first_images[0], self.first_pallet)
            for i in range(3):
                SCREEN.blit(self.num_images[int(stage[i])], self.second_pallet[i + 1])
        elif game_state == STATES['win']:
            pg.draw.rect(SCREEN, COLORS['static'], self.back_pallet)
            SCREEN.blit(self.text_first_images[0], self.first_pallet)
            for i in range(2):
                SCREEN.blit(self.text_second_images[int(i - 2)], self.second_pallet[i + 2])
        elif game_state == STATES['loose']:
            pg.draw.rect(SCREEN, COLORS['static'], self.back_pallet)
            SCREEN.blit(self.text_first_images[-1], self.first_pallet)
            for i in range(4):
                SCREEN.blit(self.text_second_images[i], self.second_pallet[i])
        else:
            SCREEN.blit(self.text_first_images[1], self.first_pallet)
