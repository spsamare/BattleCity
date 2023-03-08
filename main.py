from objectClasses import *
from init import *
from map_builder import MapBuilder
import numpy as np

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print('block size', BLOCK_SIZE)
    game_area = pg.Rect(0, 0, BLOCK_SIZE * 26, BLOCK_SIZE * 26)
    game_area_color = pg.Color('aquamarine2')
    clock = pg.time.Clock()

    done_game = False
    is_paused = False
    stage_num = 0
    player_data = [
        [3, 3],  # lives
        [0, 0],  # level
        [0, 0]  # points
    ]

    while not done_game:
        #
        done_stage = False
        timer_next_stage = 0
        #
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
        enemy_order = []
        # Add environment elements
        ocean_group = pg.sprite.Group()
        brick_group = pg.sprite.Group()
        forest_group = pg.sprite.Group()
        ice_group = pg.sprite.Group()
        steel_group = pg.sprite.Group()
        map_generator = MapBuilder(oceans=ocean_group, bricks=brick_group, forests=forest_group,
                                   ice=ice_group, steel=steel_group, spawn_order=enemy_order)
        map_generator.get_map(map_num=stage_num)
        obstacle_group.add(ocean_group)
        obstacle_group.add(brick_group)
        obstacle_group.add(steel_group)
        #
        bird = Bird(pos=(2 * 6 * BLOCK_SIZE, 2 * 12 * BLOCK_SIZE))
        this_round = Round()
        bird.round = this_round
        for this_obstacle in pg.sprite.spritecollide(bird, obstacle_group, dokill=True):
            this_obstacle.kill()
        obstacle_group.add(bird)
        countdown_start = TIMERS['enemy_spawn_delay']

        # add obstacles
        all_sprites.add(obstacle_group)

        agent1 = Player(pos=(8 * BLOCK_SIZE, 24 * BLOCK_SIZE), game_area_=game_area,
                        images=image_library[player1_sprite_start:player1_sprite_end],
                        level=player_data[1][0])
        agent1.lives = player_data[0][0]
        agent1.points = [player_data[2][0]]
        all_sprites.add(agent1)

        agent2 = Player(pos=(16 * BLOCK_SIZE, 24 * BLOCK_SIZE), game_area_=game_area, key_set=KEYS2,
                        images=image_library[player2_sprite_start:player2_sprite_end],
                        level=player_data[1][1])
        agent2.lives = player_data[0][1]
        agent2.points = [player_data[2][1]]
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
                                         obstacle_group, ocean_group, ice_group,
                                         world_bullet_list, all_rewards,
                                         enemy_order)

        # update teams
        for player in player_group:
            player.partners = player_group
            player.opponents = enemy_group
            player.obstacles = obstacle_group  # player.obstacles.add(obstacle_group)
            player.bullet_exceptions.add(ocean_group)
            player.bullet_list = world_bullet_list
            player.rewards = all_rewards
            player.ice_areas = ice_group

        temp_count = 0
        stat_board = StatBoard(player1=agent1, player2=agent2, enemy_generator=enemy_generator)
        status_display = StatusDisplay()
        #
        # get all obstacle around the bird
        dummy_tile = pg.sprite.Sprite()
        dummy_tile.rect = pg.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
        timer_fortify = 0
        state_fortify = False
        reward_fortify_picked = False
        #
        for player in player_group:
            if player.lives == 0:
                player.is_alive = False
        #
        while not done_stage:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done_stage = True
                    done_game = True

            if enemy_generator.enemies_remaining == 0 and len(enemy_group) == 0:
                this_round.completed()

            if agent1.lives + agent2.lives == 0:
                this_round.failed()
                done_game = True

            if not this_round.finished and countdown_start == 0:
                pressed_keys = pg.key.get_pressed()
                if pressed_keys[pg.K_DELETE] == 1:
                    done_game = True
                    done_stage = True
                    break
                if pressed_keys[pg.K_ESCAPE] == 1 and not this_round.finished:
                    status_display.draw(game_state=STATES['paused'], stage=str(stage_num + 1).zfill(3))
                    pg.display.flip()
                    for _ in range(2 * FPS):
                        clock.tick(FPS)
                    if this_round.state == STATES['paused']:
                        this_round.state = STATES['ongoing']
                    else:
                        this_round.state = STATES['paused']
                else:
                    agent1.control(pressed_keys)
                    agent2.control(pressed_keys)
            else:
                countdown_start = np.maximum(0, countdown_start - 1)

            if not this_round.state == STATES['paused']:
                all_sprites.update()
                all_rewards.update()
                # stat_board.update()
                # ocean_group.update()
                enemy_generator.update()

                # Fortify
                for player in player_group:
                    if player.reward_fortify_picked is True:
                        reward_fortify_picked = True
                        player.reward_fortify_picked = False
                #
                if reward_fortify_picked is True:
                    for i in range(8):
                        dummy_tile.rect.topleft = GUARD['locations'][i]
                        existing_tile = pg.sprite.spritecollideany(dummy_tile, obstacle_group)
                        if existing_tile is not None:
                            existing_tile.kill()
                        obstacle_group.add(Steel(pos=GUARD['locations'][i]))
                    state_fortify = True
                    timer_fortify = TIMERS['fortify_duration']
                    reward_fortify_picked = False
                    all_sprites.add(obstacle_group)
                #
                if state_fortify is True:
                    if timer_fortify < 1:
                        state_fortify = False
                        for i in range(8):
                            dummy_tile.rect.topleft = GUARD['locations'][i]
                            existing_tile = pg.sprite.spritecollideany(dummy_tile, obstacle_group)
                            if existing_tile is not None:
                                existing_tile.kill()
                            obstacle_group.add(Brick(pos=GUARD['locations'][i]))
                        all_sprites.add(obstacle_group)
                    timer_fortify -= 1
            # print(enemy_generator.enemies_remaining)

            SCREEN.fill(COLORS["static"])
            pg.draw.rect(SCREEN, COLORS["background"], game_area)
            #
            ice_group.draw(SCREEN)
            ocean_group.draw(SCREEN)
            all_sprites.draw(SCREEN)
            forest_group.draw(SCREEN)
            all_rewards.draw(SCREEN)
            stat_board.draw()
            #
            if countdown_start > 0 or this_round.finished or this_round.state == STATES['paused']:
                status_display.draw(game_state=this_round.state, stage=str(stage_num + 1).zfill(3))

            if this_round.finished:
                if timer_next_stage < TIMERS['delay_next_stage']:
                    timer_next_stage += 1
                else:
                    done_stage = True
                    player_data[0] = [agent1.lives, agent2.lives]
                    player_data[1] = [agent1.level, agent2.level]
                    player_data[2] = [sum(agent1.points), sum(agent2.points)]
                    if this_round.state == STATES['loose']:
                        done_game = True
                    # print(done_game)
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
        #
        stage_num += 1
        if stage_num >= MAP_COUNT:
            done_game = True

    print('Game Ended...!')
    pg.quit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
