from world import World
from common import Region, Tile, TileRegistry, debugPrint
from gen import SkyTile, GroundTile
import random
from copy import copy

class Agent:
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	def flash(self, world):
		world.tile_flash(self.x, self.y, type(self).num)
	def step(self, world):
		self.flash(world)
	def dup_add(self, world, **kwargs):
		w = copy(self)
		for kw, val in kwargs.items():
			w.__dict__[kw] = val
		world.add(w)
		return w
	async def prepare_step(self, world):
		pass
	def claim(self, world, priority, xo = 0, yo = 0):
		world.claim(self.x+xo, self.y+yo, self, priority)
		return self
	def claim_if_empty(self, world, priority, xo = 0, yo = 0):
		if world.look_at(self.x+xo, self.y+yo) == SkyTile.num:
			world.claim(self.x+xo, self.y+yo, self, priority)
		return self
	def has_claim(self, world, xo = 0, yo = 0):
		return world.has_claim(self.x+xo, self.y+yo, self)
	@classmethod
	def wake(cls, world, x, y):
		world.add(cls(x, y))
	def get_neighborhood(self, world, xoff = 0, yoff = 0):
		region = [[None, None, None], [None, None, None], [None, None, None]]
		xo, yo = self.x - 1 + xoff, self.y - 1 + yoff
		observer = world.observe(Region(xo, yo, 3, 3))
		for val, (x, y) in observer.cells():
			region[y - yo][x - xo] = val
		for x in range(3):
			for y in range(3):
				val = world.agents.get((x+xo, y+yo), None)
				if val != None:
					region[y][x] = val
		return region
	def ncheck_empty(self, neighborhood, x, y):
		return not isinstance(neighborhood[y][x], Agent) and neighborhood[y][x] == SkyTile.num

class DummyAgent(Agent, Tile):
	color = 89, 43, 233
	async def prepare_step(self, world):
		if random.randint(0, 60) == 0:
			world.add(DummyAgent(self.x, self.y))
		world.add(DummyAgent(self.x + random.choice([-1, 0, 1]),
							 self.y + random.choice([-1, 0, 1])))

class RunnerAgent(Agent, Tile):
	color = 127, 49, 117
	async def prepare_step(self, world):
		region = self.get_neighborhood(world)
		if all(self.ncheck_empty(region, x, 2) for x in range(3)):
			self.dup_add(world, y = self.y + 1)
		elif self.ncheck_empty(region, 2, 1):
			self.dup_add(world, x = self.x + 1)
		else:
			self.dup_add(world, y = self.y - 1)

class WormAgent(Agent, Tile):
	color = 47, 172, 70
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tail = []
		self.dx, self.dy = 0, 1
	async def prepare_step(self, world):
		region = self.get_neighborhood(world)
		self.tail.append((self.x, self.y))
		self.x += self.dx
		self.y += self.dy
		opts = [(self.dy, -self.dx, 1), (self.dx, self.dy, 4), (-self.dy, self.dx, 1)]
		opts = [o for o in opts if TileRegistry[region[1+o[1]][1+o[0]]].matches(GroundTile)]
		tot = sum(f for x, y, f in opts)
		r = tot * random.random()
		for x, y, f in opts:
			r -= f
			if r < 0:
				self.dx, self.dy = x, y
				break
		if len(self.tail) > 8:
			self.tail = self.tail[-8:]
		self.dup_add(world, x = self.x, y = self.y, tail = self.tail)
	def step(self, world):
		world.set_tile(self.x, self.y, SkyTile)
		world.tile_flash(self.x, self.y, type(self).num)
		for x, y in self.tail:
			world.tile_flash(x, y, type(self).num)

class FallingSandAgent(Tile, Agent):
	awaken=[(-1,1), (0,1), (1,1)]
	@staticmethod
	def build(*args, **kwargs):
		return random.choice([FallingSandAgent1, FallingSandAgent2])(*args, **kwargs)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.stop = False
	async def prepare_step(self, world):
		if self.stop: return
		child = self.dup_add(world)
		child.claim(world, 1.0)
		child.claim_if_empty(world, 0.2, yo = 1)
	def step(self, world):
		if self.has_claim(world, yo = 1):
			self.y += 1
			self.flash(world)
		elif self.has_claim(world):
			world.set_tile(self.x, self.y, type(self))
			self.stop = True
class FallingSandAgent1(FallingSandAgent):
    color = 200, 175, 115
class FallingSandAgent2(FallingSandAgent):
    color = 213, 189, 138