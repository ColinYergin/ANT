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

def regionHasAny(reg):
    return reg.w > 0 and reg.h > 0

def regionDiff(r1, r2):
    x, y, w, h = [*r2]
    left, right, top, bottom = x, x + w, y, y + h
    regs = [Region(r1.x, r1.y, r1.w, top - r1.y),
            Region(r1.x, top, left - r1.x, h),
            Region(r1.x, bottom, r1.w, r1.y + r1.h - bottom),
            Region(right, top, r1.x + r1.w - right, h)]
    return [reg for reg in regs if regionHasAny(reg)]