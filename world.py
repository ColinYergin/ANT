from common import Region, debugPrint
import time, asyncio

class World:
    def __init__(self, generator, tile_size = (16, 16), chunk_size = (8, 8), chunk_cache_size = 512):
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
        del self.loaded[chunk]
    def is_loaded(self, chunk):
        return chunk in self.loaded
    def fix_cache_size(self):
        while len(self.loaded) >= self.chunk_cache_size:
            oldest = (float('inf'), None)
            for k, (timestamp, data) in self.loaded.items():
                oldest = min(oldest, (timestamp, k))
            self.unload(oldest[1])
    async def aload(self, chunk):
        return self.load(chunk)
    def preload(self, chunk):
        self.loaded[chunk] = time.clock(), self.gen(chunk, self.chunk_size)
    def load(self, chunk):
        try:
            return self.loaded[chunk][1]
        except:
            pass
        self.preload(chunk)
        self.fix_cache_size()
        return self.loaded[chunk][1]
    class RowView:
        def __init__(self, row, yc, reg_view):
            self.row = row
            self.yc = yc
            self.xc_range = reg_view.xc_range
            self.x_range = reg_view.region.x, reg_view.region.x + reg_view.region.w
            self.world = reg_view.world
        def cells(self):
            chunk_w, chunk_h = self.world.chunk_size
            realy = self.row % chunk_h
            loader = self.world.load
            
            leftxc = self.xc_range[0]
            chunk_x = leftxc * chunk_w
            for x in range(self.x_range[0], min(self.x_range[1], chunk_x + chunk_w)):
                realx = x % chunk_w
                yield loader((leftxc, self.yc))[realx][realy], (x, self.row)
            
            rightxc = self.xc_range[1] - 1
            if rightxc > leftxc:
                chunk_x = rightxc * chunk_w
                for x in range(max(self.x_range[0], chunk_x), self.x_range[1]):
                    realx = x % chunk_w
                    yield loader((rightxc, self.yc))[realx][realy], (x, self.row)
                
            for xc in range(self.xc_range[0] + 1, self.xc_range[1] - 1):
                chunk_x = xc * chunk_w
                for x in range(chunk_x, chunk_x + chunk_w):
                    realx = x % chunk_w
                    yield loader((xc, self.yc))[realx][realy], (x, self.row)
    class RegionView:
        def __init__(self, region, world):
            self.world = world
            self.xc_range, self.yc_range = world.chunk_region(region)
            self.region = region
        def rows(self):
            chunk_w, chunk_h = self.world.chunk_size
            for yc in range(*self.yc_range):
                chunk_y = yc * chunk_h
                for y in range(max(chunk_y, self.region.y),
                               min(chunk_y + chunk_h, self.region.y + self.region.h)):
                    yield World.RowView(y, yc, self)
    def observe(self, region):
        return World.RegionView(region, self)
    def register_watch(self, region, cb):
        self.watches[region] = cb
        return region
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
    async def prepare_step(self):
        coroutines = [agent.prepare_step(self) for agent in self.agents]
        completed, pending = await asyncio.wait(coroutines)
    def tile_flash(self, x, y, i):
        for region, cb in self.watches.items():
            if region.x < x < region.x + region.w and region.y < y < region.y + region.h:
                cb(x, y, i)
        self.flashed[(x, y)] = i