import world
import numpy as np
from common import Tile

class GroundTile(Tile):
    pass
class GroundTile1(GroundTile):
    color = 172, 132, 47
class GroundTile2(GroundTile):
    color = 166, 122, 27
class SkyTile(Tile):
    color = 135, 206, 235

class RandHelper:
    def __init__(self, worldseed):
        self.r = np.random.RandomState(worldseed)
        self.rstate = self.r.get_state()
    def at(self, x, y):
        self.r.set_state(self.rstate)
        self.r.seed((x % 10000000, y % 10000000))
    def nowhere(self):
        self.r.set_state(self.rstate)
    def bit(self):
        return self.r.bytes(1)[0] % 2

class Generator:
    def __init__(self):
        self.rgen = RandHelper(0)
        self.toff = self.rgen.r.uniform(0, 6.283)
    def __call__(self, chunk_coords, chunk_size):
        x, y = chunk_coords
        w, h = chunk_size
        res = np.empty(chunk_size, np.int8)
        self.rgen.at(x, y)
        for xo in range(w):
            X = x * chunk_size[0] + xo
            for yo in range(h):
                Y = -y * chunk_size[1] - yo
                res[xo][yo] = SkyTile.num if 10*np.sin(self.toff+X/30) < Y else [GroundTile1, GroundTile2][self.rgen.bit()].num
        return res