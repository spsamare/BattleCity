class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, game_area_, id_=0, images=image_library[enemy1_sprite_start:enemy2_sprite_end]):
        super().__init__()
        self.rect = pg.Rect(0, 0, 2 * BLOCK_SIZE, 2 * BLOCK_SIZE)
        # for i in range(len(images)):
        #     images[i] = pg.transform.scale(images[i], (2 * BLOCK_SIZE, 2 * BLOCK_SIZE))
        self.image_state = True
        #
        self.start_pos = pos
        self.rect.topleft = pos
        self.direction = DIRECTION["S"]
        self.game_area = game_area_
        self.speed = BLOCK_SIZE / 2
        self.move_count = 0
        self.move_count_max = 10
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.speed_x = 0.
        self.speed_y = 0.
        #
        self.images = images
        self.image = images[self.direction]
        #
        self.obstacles = pg.sprite.Group()
        self.bullet_exceptions = pg.sprite.Group()
        self.level = 0
        #
        self.shoot_count = 0
        self.shoot_count_max = FPS
        self.shoot_speed = 1.0
        #
        self.hit_by = None
        self.lives = 1
        self.is_alive = True
        self.respawn_counter = 0
        #
        self.id = id_
        self.is_player = False
        self.immortal_timer = 5 * FPS
        self.immortal = True
        self.has_shield = False
        #
        self.partners = pg.sprite.Group()
        self.opponents = pg.sprite.Group()
        #
        self.probability = [
            [.2, .4, .4],  # stay [0], continue [1], change [2]
            [.2, .8, .0]
        ]
        self.inertia_state = 0
        self.shoot_probability = .5

    def update(self):
        if self.is_alive:
            if self.hit_by is None:
                if self.shoot_count > 0:
                    self.shoot_count = (self.shoot_count + 1) % self.shoot_count_max
                if self.level == 3 and self.shoot_count == 10:
                    self.groups()[0].add(Bullet(self, self.game_area))
                #
                if self.immortal_timer > 0:
                    self.immortal = True
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
        if not self.game_area.contains(self.rect) or \
                pg.sprite.spritecollideany(self, self.obstacles) is not None or \
                pg.sprite.spritecollideany(self, self.partners) is not None or \
                pg.sprite.spritecollideany(self, self.opponents) is not None:
            status = False

            # pass
        self.rect.center = old_position
        return status

    def level_change(self, change):
        if change > 0:
            self.level = min(self.level + 1, 3)
        else:
            self.level = max(self.level - 1, 0)
        print(self.level)
        self.image = self.images[self.level * 8 + self.direction]
        if self.level == 3:
            self.shoot_count_max = FPS // 2
            self.shoot_speed = 1.5
        elif self.level == 2:
            self.shoot_count_max = FPS // 2
            self.shoot_speed = 1.5
        elif self.level == 1:
            self.shoot_count_max = FPS // 2
            self.shoot_speed = 1.0
        else:
            self.shoot_count_max = FPS
            self.shoot_speed = 1.0
        # print(self.level)

    def shoot(self):
        if self.shoot_count == 0:
            self.groups()[0].add(Bullet(self, self.game_area))
            self.shoot_count += 1

    def blast(self):
        self.is_alive = False
        self.hit_by = None
        self.lives = max(self.lives - 1, 0)
        self.respawn_counter = FPS
        self.image = self.images[-1]
        self.groups()[0].add(Blast(self, self.game_area))

    def spawn(self):
        self.rect.topleft = self.start_pos
        self.direction = DIRECTION["S"]
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


class Player(pg.sprite.Sprite):

    def __init__(self, pos, images, game_area_, key_set=KEYS1, id_=0):
        super().__init__()
        self.rect = pg.Rect(0, 0, 2 * BLOCK_SIZE, 2 * BLOCK_SIZE)
        # for i in range(len(images)):
        #     images[i] = pg.transform.scale(images[i], (2 * BLOCK_SIZE, 2 * BLOCK_SIZE))
        self.images = images
        self.image = images[0]
        self.image_state = True
        #
        self.start_pos = pos
        self.rect.topleft = pos
        self.direction = DIRECTION["N"]
        self.game_area = game_area_
        self.speed = BLOCK_SIZE / 2
        self.move_count = 0
        self.move_count_max = 10
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.speed_x = 0.
        self.speed_y = 0.
        #
        self.obstacles = pg.sprite.Group()
        self.bullet_exceptions = pg.sprite.Group()
        self.level = 0
        #
        self.shoot_count = 0
        self.shoot_count_max = FPS
        self.shoot_speed = 1.0
        #
        self.hit_by = None
        self.lives = 3
        self.is_alive = True
        self.respawn_counter = 0
        #
        self.id = id_
        self.is_player = True
        self.immortal_timer = 5 * FPS
        self.immortal = True
        self.has_shield = False
        self.keys = key_set
        #
        self.partners = pg.sprite.Group()
        self.opponents = pg.sprite.Group()

    def update(self):
        if self.is_alive:
            if self.hit_by is None:
                if self.shoot_count > 0:
                    self.shoot_count = (self.shoot_count + 1) % self.shoot_count_max
                if self.level == 3 and self.shoot_count == 10:
                    self.groups()[0].add(Bullet(self, self.game_area))
                #
                if self.immortal_timer > 0:
                    self.immortal = True
                    if not self.has_shield:
                        self.groups()[0].add(Shield(self, self.game_area))
                        self.has_shield = True
                    self.immortal_timer -= 1
                else:
                    self.immortal = False
                    self.has_shield = False
            else:
                self.blast()
        else:
            if self.lives > 0:
                self.respawn_counter -= 1
                if self.respawn_counter == 0:
                    self.spawn()
            else:
                self.kill()

    def control(self, key):
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
        if not self.game_area.contains(self.rect) or \
                pg.sprite.spritecollideany(self, self.obstacles) is not None or \
                pg.sprite.spritecollideany(self, self.partners) is not None or \
                pg.sprite.spritecollideany(self, self.opponents) is not None:
            status = False

            # pass
        self.rect.center = old_position
        return status

    def level_change(self, change):
        if change > 0:
            self.level = min(self.level + 1, 3)
        else:
            self.level = max(self.level - 1, 0)
        print(self.level)
        self.image = self.images[self.level * 8 + self.direction]
        if self.level == 3:
            self.shoot_count_max = FPS // 2
            self.shoot_speed = 1.5
        elif self.level == 2:
            self.shoot_count_max = FPS // 2
            self.shoot_speed = 1.5
        elif self.level == 1:
            self.shoot_count_max = FPS // 2
            self.shoot_speed = 1.0
        else:
            self.shoot_count_max = FPS
            self.shoot_speed = 1.0
        # print(self.level)

    def shoot(self):
        if self.shoot_count == 0:
            self.groups()[0].add(Bullet(self, self.game_area))
            self.shoot_count += 1

    def blast(self):
        self.is_alive = False
        self.hit_by = None
        self.lives = max(self.lives - 1, 0)
        self.respawn_counter = FPS
        self.image = self.images[-1]
        self.groups()[0].add(Blast(self, self.game_area))

    def spawn(self):
        self.image = self.images[0]
        self.rect.topleft = self.start_pos
        self.direction = DIRECTION["N"]
        #
        self.move_count = 0
        self.shoot_count = 0
        self.is_alive = True
        self.respawn_counter = 0
        #
        self.immortal_timer = 5 * FPS
        self.immortal = True
        self.has_shield = False
