from objectClasses import *
from init import *
import numpy as np


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('block size', BLOCK_SIZE)

    game_area = pg.Rect(0, 0, BLOCK_SIZE * 26, BLOCK_SIZE * 26)
    game_area_color = pg.Color('aquamarine2')
    clock = pg.time.Clock()

    done = False
    all_sprites = pg.sprite.Group()
    all_rewards = pg.sprite.Group()
    world_bullet_list = pg.sprite.Group()

    """
    obstacle_group = pg.sprite.Group(
        Obstacle((1 * BLOCK_SIZE, 8 * BLOCK_SIZE), image_library[4]),
        Obstacle((2 * BLOCK_SIZE, 8 * BLOCK_SIZE), image_library[4])
    )
    """
    num_obstacles = 30
    xy_list = list(range(2, 40 * 30))
    np.random.shuffle(xy_list)
    obstacle_group = pg.sprite.Group()
    """
    for o in range(num_obstacles):
        x_val = xy_list[o] // 30
        y_val = xy_list[o] % 30
        obstacle_group.add(
            Brick((x_val * BLOCK_SIZE, y_val * BLOCK_SIZE), num=np.random.randint(5))
        )
    """
    # Add environment elements
    ocean_group = pg.sprite.Group()
    for o in range(11):
        ocean_group.add(
            Ocean((2 * (o + 1) * BLOCK_SIZE, 2 * 7 * BLOCK_SIZE))
        )
    obstacle_group.add(ocean_group)

    forest_group = pg.sprite.Group()
    for o in range(11):
        forest_group.add(
            Forest((2 * (o + 1) * BLOCK_SIZE, 2 * 3 * BLOCK_SIZE))
        )

    ice_group = pg.sprite.Group()
    """
    for o in range(11):
        ice_group.add(
            Ice((2 * (o + 1) * BLOCK_SIZE, 2 * 5 * BLOCK_SIZE))
        )
    """

    steel_group = pg.sprite.Group()
    for o in range(6):
        steel_group.add(
            Steel(((o + 10) * BLOCK_SIZE, 2 * 11 * BLOCK_SIZE))
        )
    obstacle_group.add(steel_group)

    bird = Bird(pos=(2 * 6 * BLOCK_SIZE, 2 * 12 * BLOCK_SIZE))
    this_round = Round()
    bird.round = this_round
    obstacle_group.add(bird)
    countdown_start = TIMERS['enemy_spawn_delay']

    # add obstacles
    all_sprites.add(obstacle_group)

    agent1 = Player(pos=(8 * BLOCK_SIZE, 24 * BLOCK_SIZE), game_area_=game_area,
                    images=image_library[player1_sprite_start:player1_sprite_end])
    all_sprites.add(agent1)

    agent2 = Player(pos=(16 * BLOCK_SIZE, 24 * BLOCK_SIZE), game_area_=game_area, key_set=KEYS2,
                    images=image_library[player2_sprite_start:player2_sprite_end])
    all_sprites.add(agent2)

    # agent1.partners.add(agent2)
    # agent2.partners.add(agent1)
    #
    player_group = pg.sprite.Group()
    player_group.add(agent1)
    player_group.add(agent2)

    # Enemies
    enemy_group = pg.sprite.Group()
    enemy_generator = EnemyGenerator(game_area, all_sprites,
                                     enemy_group, player_group,
                                     obstacle_group, ocean_group,
                                     world_bullet_list, all_rewards)

    # update teams
    for player in player_group:
        player.partners = player_group
        player.opponents = enemy_group
        player.obstacles = obstacle_group  # player.obstacles.add(obstacle_group)
        player.bullet_exceptions.add(ocean_group)
        player.bullet_list = world_bullet_list
        player.rewards = all_rewards

    # Tests
    # all_rewards.add(RewardBlast(pos=(4 * BLOCK_SIZE, 24 * BLOCK_SIZE)))
    all_rewards.add(RewardUpgrade(pos=(4 * BLOCK_SIZE, 22 * BLOCK_SIZE)))
    all_rewards.add(RewardUpgrade(pos=(4 * BLOCK_SIZE, 20 * BLOCK_SIZE)))

    """
    enemy1 = Enemy(pos=(0 * BLOCK_SIZE, 0 * BLOCK_SIZE), game_area_=game_area)
    enemy2 = EnemySpecial(pos=(12 * BLOCK_SIZE, 0 * BLOCK_SIZE), game_area_=game_area)
    enemy3 = Enemy(pos=(24 * BLOCK_SIZE, 0 * BLOCK_SIZE), game_area_=game_area)
    all_sprites.add(enemy1)
    all_sprites.add(enemy2)
    all_sprites.add(enemy3)
    #
    enemy_group.add(enemy1)
    enemy_group.add(enemy2)
    enemy_group.add(enemy3)

    for enemy in enemy_group:
        enemy.partners = enemy_group
        enemy.opponents = player_group
        enemy.obstacles = obstacle_group  # enemy.obstacles.add(obstacle_group)
        enemy.bullet_exceptions.add(ocean_group)
        enemy.bullet_list = world_bullet_list
        enemy.rewards = all_rewards
    """

    temp_count = 0
    stat_board = StatBoard(player1=agent1, player2=agent2, enemy_generator=enemy_generator)
    status_display = StatusDisplay()
    # stat_board.enemy_generator = enemy_generator.enemies_remaining
    while not done:
        """
        # print(temp_count)
        temp_count += 1
        """
        """
        if temp_count == 120:
            temp_count = 0
            agent1.level_change(random.randrange(2))
        # """
        """
        if temp_count == 6*FPS:
            temp_count = 0
            all_sprites.add(Blast(agent1, agent1.game_area))
        # """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        if enemy_generator.enemies_remaining == 0 and len(enemy_group) == 0:
            this_round.completed()

        if agent1.lives + agent2.lives == 0:
            this_round.failed()

        if not this_round.finished and countdown_start == 0:
            pressed_keys = pg.key.get_pressed()
            agent1.control(pressed_keys)
            agent2.control(pressed_keys)
        else:
            countdown_start = np.maximum(0, countdown_start - 1)

        all_sprites.update()
        all_rewards.update()
        # stat_board.update()
        # ocean_group.update()
        enemy_generator.update()
        # print(enemy_generator.enemies_remaining)

        SCREEN.fill(COLORS["static"])
        pg.draw.rect(SCREEN, COLORS["background"], game_area)
        #
        ice_group.draw(SCREEN)
        # ocean_group.draw(SCREEN)
        all_sprites.draw(SCREEN)
        forest_group.draw(SCREEN)
        all_rewards.draw(SCREEN)
        stat_board.draw()
        #
        if countdown_start > 0 or this_round.finished:
            status_display.draw(game_state=this_round.state)

        # draw border
        """
        pg.draw.lines(SCREEN, game_area_color, False,
                      [(0, BLOCK_SIZE * 26),
                       (BLOCK_SIZE * 26, BLOCK_SIZE * 26),
                       (BLOCK_SIZE * 26, 0)], 1)
        """
        # pg.draw.rect(SCREEN, game_area_color, (0, 0, 2 * BLOCK_SIZE, 2 * BLOCK_SIZE), 1)
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
