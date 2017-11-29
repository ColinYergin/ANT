from world import World
from common import Region
import random

class Agent:
	def __init__(self, x = 0, y = 0, tile_num = 5):
		self.x = x
		self.y = y
		self.old_x = x
		self.old_y = y
		self.tile_num = tile_num
	def flash(self, world):
		world.tile_flash(self.x, self.y, self.tile_num)
	def step(self, world):
		self.old_x = self.x
		self.old_y = self.y
		self.flash(world)
	async def prepare_step(self, world):
		pass
	def is_dead(self):
		return False

class DummyAgent(Agent):
	async def prepare_step(self, world):
		self.x += random.choice([-1, 0, 1])
		self.y += random.choice([-1, 0, 1])
		if random.randint(0, 60) == 0:
			pass #world.add(DummyAgent(self.x, self.y))

class WorkerAgent(Agent):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	async def prepare_step(self, world):
		region = []
		for row in world.observe(Region(self.x - 1, self.y - 1, 3, 3)).rows():
			region.append([])
			for tile, coords in row.cells():
				region[-1].append(tile)
		if not any(t == 9 for t in region[2]):
			self.y += 1
			return
		if region[1][2] == 0:
			self.x += 1
			return
		self.y -= 1