from collections import namedtuple
import sys

Region = namedtuple('Region', ['x', 'y', 'w', 'h'])

def debugPrint(*al, **ad):
    print(*al, **ad)
    sys.stdout.flush()

class Range:
    __slots__ = ('low', 'high')
    def __init__(self, low, high):
        self.low = low
        self.high = high
    def __contains__(self, item):
        return self.low <= item < self.high
    def empty(self):
        return self.low < self.high
    def subtract(self, other):
        res = []
        if self.low < other.low:
            res += Range(self.low, min(other.low, self.high))
        if other.high < self.high:
            res += Range(other.high, self.high)
        return res