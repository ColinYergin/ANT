from common import Region, debugPrint
import time

class World:
    def __init__(self, generator, tile_size = (16, 16), chunk_size = (32, 32), chunk_cache_size = 256):
        self.gen = generator
        self.loaded = {}
        self.tile_size = tile_size
        self.chunk_size = chunk_size
        self.chunk_cache_size = chunk_cache_size
        self.watches = {}
        self.agents = []
        self.flashed = {}
    def to_chunk(self, x, y):
        return x // self.chunk_size[0], y // self.chunk_size[1]
    def to_chunk_offset(self, x, y):
        return x % self.chunk_size[0], y % self.chunk_size[1]
    def chunk_region(self, region):
        return ((region.x // self.chunk_size[0], (region.x + region.w) // self.chunk_size[0] + 1),
                (region.y // self.chunk_size[1], (region.y + region.h) // self.chunk_size[1] + 1))
    def unload(self, chunk):
        debugPrint('evicted', chunk)
        del self.loaded[chunk]
    def load(self, chunk):
        try:
            return self.loaded[chunk][1]
        except:
            pass
        while len(self.loaded) >= self.chunk_cache_size:
            oldest = (float('inf'), None)
            for k, (timestamp, data) in self.loaded.items():
                oldest = max(oldest, (timestamp, k))
            self.unload(oldest[1])
        debugPrint('loaded', chunk)
        self.loaded[chunk] = time.clock(), self.gen(chunk, self.chunk_size)
        return self.loaded[chunk][1]
    class RowView:
        def __init__(self, row, yc, reg_view):
            self.row = row
            self.yc = yc
            self.xc_range = reg_view.xc_range
            self.x_range = reg_view.region.x, reg_view.region.x + reg_view.region.w
            self.world = reg_view.world
            self.todrop = (0,0) # half open range, (0, 0) means drop none
            if reg_view.dropreg != None:
                if reg_view.dropreg.y < row < reg_view.dropreg.y + reg_view.dropreg.h:
                    self.todrop = reg_view.dropreg.x, reg_view.dropreg.x + reg_view.dropreg.w
        def cells(self):
            chunk_w, chunk_h = self.world.chunk_size
            realy = self.row % chunk_h
            loader = self.world.load
            for xc in range(*self.xc_range):
                chunk_x = xc * chunk_w
                for x in range(max(chunk_x, self.x_range[0]),
                               min(chunk_x + chunk_w, self.x_range[1])):
                    if self.todrop[0] < x < self.todrop[1]: continue
                    realx = x % chunk_w
                    yield loader((xc, self.yc))[realx][realy], (x, self.row)
    class RegionView:
        def __init__(self, region, world, ignoring):
            self.world = world
            self.xc_range, self.yc_range = world.chunk_region(region)
            self.region = region
            self.dropreg = ignoring
        def rows(self):
            chunk_w, chunk_h = self.world.chunk_size
            for yc in range(*self.yc_range):
                chunk_y = yc * chunk_h
                for y in range(max(chunk_y, self.region.y),
                               min(chunk_y + chunk_h, self.region.y + self.region.h)):
                    yield World.RowView(y, yc, self)
    def observe(self, region, *, ignoring = None):
        return World.RegionView(region, self, ignoring)
    def register_watch(self, region, cb):
        self.watches[region] = cb
    def unregister_watch(self, region):
        del self.watches[region]
    def add(self, agent):
        self.agents.append(agent)
    def step(self):
        for region, cb in self.watches.items():
            for (x, y), i in self.flashed.items():
                if region.x < x < region.x + region.w and region.y < y < region.y + region.h:
                    offx, offy = self.to_chunk_offset(x, y)
                    cb(x, y, self.load(self.to_chunk(x, y))[offx][offy])
        newagents = []
        for agent in self.agents:
                newagents.append(agent)
                agent.step(self)
        self.agents = newagents
    def tile_flash(self, x, y, i):
        for region, cb in self.watches.items():
            if region.x < x < region.x + region.w and region.y < y < region.y + region.h:
                cb(x, y, i)
        self.flashed[(x, y)] = i