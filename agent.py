from world import World
import random

class Agent:
	def step(self, world):
		pass
	def is_dead(self):
		return True

class DummyAgent(Agent):
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	def step(self, world):
		world.tile_flash(self.x, self.y, 5)
		self.x += random.choice([-1, 0, 1])
		self.y += random.choice([-1, 0, 1])
		if random.randint(0, 20) == 0:
			world.add(DummyAgent(self.x, self.y))
	def is_dead(self):
		return False