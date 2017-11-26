import world
import numpy as np

class Generator:
    def __init__(self):
        self.rgen = np.random.RandomState()
        self.toff = self.rgen.uniform(0, 6.283)
    def __call__(self, chunk_coords, chunk_size):
        x, y = chunk_coords
        w, h = chunk_size
        res = np.empty(chunk_size, np.int8)
        for xo in range(w):
            X = x * chunk_size[0] + xo
            for yo in range(h):
                Y = -y * chunk_size[1] - yo
                res[xo][yo] = 0 if 10*np.sin(self.toff+X/30) < Y else 9
        return res