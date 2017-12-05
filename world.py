from common import Region, TileRegistry, debugPrint
import time, asyncio

class World:
    def __init__(self, generator, tile_size, chunk_size = (8, 8), chunk_cache_size = 512):
        self.gen = generator
        self.loaded = {}
        self.tile_size = tile_size
        self.chunk_size = chunk_size
        self.chunk_cache_size = chunk_cache_size
        self.watches = {}
        self.agents = {}
        self.pending_agents = []
        self.flashed = {}
        self.claims = {}
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
    def look_at(self, x, y):
        ox, oy = self.to_chunk_offset(x, y)
        return self.load(self.to_chunk(x, y))[ox][oy]
    class RegionView:
        def __init__(self, region, world):
            self.world = world
            self.xc_range, self.yc_range = world.chunk_region(region)
            self.region = region
        def cells(self):
            chunk_w, chunk_h = self.world.chunk_size
            loader = self.world.load
            for yc in range(*self.yc_range):
                chunk_y = yc * chunk_h
                y_range = max(chunk_y, self.region.y), min(chunk_y + chunk_h, self.region.y + self.region.h)
                for xc in range(*self.xc_range):
                    chunk_x = xc * chunk_w
                    x_range = max(self.region.x, chunk_x), min(chunk_x + chunk_w, self.region.x + self.region.w)
                    chunk_data = loader((xc, yc))
                    for x in range(*x_range):
                        col = chunk_data[x % chunk_w]
                        for y in range(*y_range):
                            yield col[y % chunk_h], (x, y)
    def observe(self, region):
        return World.RegionView(region, self)
    def set_tile(self, x, y, tile):
        chunk = self.to_chunk(x, y)
        ox, oy = self.to_chunk_offset(x, y)
        self.load(chunk)[ox][oy] = tile.num
        self.tile_flash(x, y, tile.num)
        self.wake_around(x, y)
    def register_watch(self, region, cb):
        self.watches[region] = cb
        return region
    def unregister_watch(self, region):
        del self.watches[region]
    def add(self, agent):
        self.pending_agents.append(agent)
    def step(self):
        for x, y in self.flashed: self.wake_around(x, y)
        for region, cb in self.watches.items():
            for (x, y), i in self.flashed.items():
                if region.x < x < region.x + region.w and region.y < y < region.y + region.h:
                    offx, offy = self.to_chunk_offset(x, y)
                    cb(x, y, i)
        num_agents_pending = len(self.pending_agents)
        self.agents, self.pending_agents = {(a.x, a.y):a for a in self.pending_agents}, []
        if num_agents_pending != len(self.agents):
            debugPrint("Agent overlap, {} lost".format(num_agents_pending - len(self.agents)))
        for agent in self.agents.values():
            agent.step(self)
        self.claims = {}
    async def prepare_step(self):
        coroutines = [agent.prepare_step(self) for agent in self.agents.values()]
        completed, pending = await asyncio.wait(coroutines)
    def tile_flash(self, x, y, i, with_unflash = True):
        for region, cb in self.watches.items():
            if region.x < x < region.x + region.w and region.y < y < region.y + region.h:
                cb(x, y, i)
        offx, offy = self.to_chunk_offset(x, y)
        if with_unflash:
            self.flashed[(x, y)] = self.load(self.to_chunk(x, y))[offx][offy]
        self.wake_around(x, y)
    def claim(self, x, y, owner, priority):
        coords = x, y
        self.claims[coords] = max((priority, owner), self.claims.get(coords, (-float('inf'), None)))
    def has_claim(self, x, y, owner):
        return self.claims.get((x, y), (None, None))[1] == owner
    def wake_around(self, x, y):
        for val, (rx, ry) in self.observe(Region(x-1, y-1, 3, 3)).cells():
            cls = TileRegistry[val]
            if cls in TileRegistry.wake[(rx-x, ry-y)]:
                cls.wake(self, rx, ry)