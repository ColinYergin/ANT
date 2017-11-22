from collections import namedtuple
import numpy as np
import time

Region = namedtuple('Region', ['x', 'y', 'w', 'h'])

class World:
	def __init__(self, generator, chunk_size = (32, 32), chunk_cache_size = 256):
		self.gen = generator
		self.loaded = {}
		self.chunk_size = chunk_size
		self.chunk_cache_size = chunk_cache_size
	def to_chunk(self, x, y):
		return x // chunk_size[0], y // chunk_size[1]
	def to_chunk_offset(self, x, y):
		return x % chunk_size[0], y % chunk_size[1]
	def load(self, chunk):
		try:
			return self.loaded[chunk][1]
		except:
			pass
		while len(self.loaded) >= self.chunk_cache_size:
			oldest = (float('inf'), None)
			for k, (timestamp, data) in self.loaded.items():
				oldest = max(oldest, (timestamp, k))
			del self.loaded[oldest[1]]
		self.loaded[chunk] = time.clock(), self.gen(chunk, self.chunk_size)
		return self.loaded[chunk][1]
	class RowView:
		def __init__(self, row, xc_range, x_range, world):
			self.row = row
			self.xc_range = xc_range
			self.x_range = x_range
			self.world = world
		def rows(self):
			for xc in range(*self.xc_range):
				for x in range(max(xc * self.world.chunk_size[0], self.x_range[0]),
					           min(xc * self.world.chunk_size[0] + self.world.chunk_size[0], self.x_range[1])):
					yield self.load(chunk)[x % self.world.chunk_size[0]]
										  [y % self.world.chunk_size[1]]
	class RegionView:
		def __init__(self, region, world):
			self.world = world
			self.xc_range, self.yc_range = chunk_region(region)
			self.region = region
		def rows(self):
			for yc in range(*self.yc_range):
				for y in range(max(yc * self.world.chunk_size[1], self.region.y),
					           min(yc * self.world.chunk_size[1] + self.world.chunk_size[1], self.region.y + self.region.h)):
					yield RowView(y, self.xc_range, (self.region.x, self.region.x + self.region.w), self.world)
	def observe(self, region):
		return RegionView(region, self)