"""
Legend
---------------------
0: 4x4
1 - 4: right, down, left, up (1 x 2)
5 - 8: top-right, bottom-right, bottom-left, top-left (1 x 1)
---------------------
00: empty
b(0-8): bricks
s(0-8): steel
o0: ocean
f0: forest
i0: ice
Bird placement is automatic
Spawn areas will be cleared at runtime.
"""

from objectClasses import *


class MapBuilder:
    def __init__(self, oceans, bricks, forests, ice, steel, spawn_order):
        self.directory = 'maps/'
        self.map = None
        self.ocean_group = oceans
        self.brick_group = bricks
        self.forest_group = forests
        self.ice_group = ice
        self.steel_group = steel
        #
        self.spawn_order = spawn_order

    def get_map(self, map_num=0):
        self.map = []
        with open(self.directory + str(map_num).zfill(3) + '.map') as fp:
            for i in range(13):
                line = fp.readline().split(' ')
                self.map.append(line)

            if fp.readline():
                line = fp.readline().split(' ')
                for _ in line:
                    self.spawn_order.append(int(_[0]))

        self.get_tiles(self.ocean_group, Ocean, 'o')
        self.get_tiles(self.brick_group, Brick, 'b')
        self.get_tiles(self.forest_group, Forest, 'f')
        self.get_tiles(self.ice_group, Ice, 'i')
        self.get_tiles(self.steel_group, Steel, 's')

    def get_tiles(self, group, obstacle, sym):
        for i in range(13):
            for j in range(13):
                text = self.map[j][i]
                if text[0] == sym:
                    get_cell(group=group, obstacle=obstacle, location=[i, j], num=int(text[1]))


def get_cell(group, obstacle, location, num=0):
    if num in [0, 1, 4, 5]:
        group.add(obstacle(pos=((2 * location[0] + 1) * BLOCK_SIZE, 2 * location[1] * BLOCK_SIZE)))
    if num in [0, 1, 2, 6]:
        group.add(obstacle(pos=((2 * location[0] + 1) * BLOCK_SIZE, (2 * location[1] + 1) * BLOCK_SIZE)))
    if num in [0, 2, 3, 7]:
        group.add(obstacle(pos=(2 * location[0] * BLOCK_SIZE, (2 * location[1] + 1) * BLOCK_SIZE)))
    if num in [0, 3, 4, 8]:
        group.add(obstacle(pos=(2 * location[0] * BLOCK_SIZE, 2 * location[1] * BLOCK_SIZE)))
