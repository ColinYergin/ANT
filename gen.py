from collections import namedtuple
import world

class QNode(namedtuple('QNode', ['ul', 'ur', 'dl', 'dr', 'x', 'y', 'w', 'h'])):
	def __init__(self, x, y, w, h, data = {}):
		self.x, self.y, self.w, self.h = x, y, w, h
		for coords, val in data:
			self.insert(coords, val)
		self.fix_down()
	def insert(coords, is_right, is_down, val):
		self[(1 if coords[0] < self.x + self.w / 2 else 0) + (2 if coords[1] < self.y + self.h / 2 else 0)][coords] = val
	def fix_down(self):
		for i in range(4):
			if type(self[i]) == QNode:
				self[i].fix_down()
			else:
				if len(self[i]) > 12:
					self[i] = QNode(self.x, self.y, self.w, self.h, self[i])
					self[i].fix_down()
	def region(x, y, w, h):
		if x < self.x
		for xc in range(2):
			for yc in range(2):
				if x + xc


def buildQNode(x, y, w, h, coord_dict):
	if len(coord_dict) > 12:
		dicts = [[{}, {}], [{}, {}]]
		for (xc, yc), val in coord_dict:
			dicts[1 if xc > x + w / 2 else 0][1 if yc > y + w / 2 else 0][(xc, yc)] = val
		return QNode(buildQNode(x        , y        , w / 2, h / 2, dicts[0][0]),
			         buildQNode(x + w / 2, y        , w / 2, h / 2, dicts[1][0]),
			         buildQNode(x        , y + h / 2, w / 2, h / 2, dicts[0][1]),
			         buildQNode(x + w / 2, y + h / 2, w / 2, h / 2, dicts[1][1]))
	return coord_dict

def addQNodeFeature(qnode, x, y, feature):
	if isinstance(qnode, QNode):


class Generator:
	def __init__(self):
		self.features = {}
	def add_feature(self, x, y, feature):
		addQNodeFeature(self.features, x, y, feature)
