import world
from common import Region, debugPrint, regionDiff, TileRegistry

class Camera:
    def __init__(self, world, coords = (0, 0), centerin = (0, 0)):
        self.world = world
        self.x, self.y = (coords[0] - centerin[0]//2, coords[1] - centerin[1]//2)
        self.buf = None
        self.bufdirty = {}
        self.watch = None
    def move_x(self, offset):
        self.x += offset
    def move_y(self, offset):
        self.y += offset
    def draw_to(self, surf):
        w, h = surf.get_size()
        tile_w, tile_h = self.world.tile_size
        tile, offset = zip(divmod(self.x, tile_w),
                           divmod(self.y, tile_h))
        observer = self.world.observe
        vreg = Region(*tile, w // tile_w + 1, h // tile_h + 1)
        if self.buf == None:
            for val, (x, y) in observer(vreg).cells():
                surf.blit(TileRegistry[val].img, ((x - tile[0]) * tile_w - offset[0], 
                                                  (y - tile[1]) * tile_h - offset[1]))
        else:
            bx, by, bs, breg = self.buf
            surf.blit(bs, (bx - self.x, by - self.y))
            
            for reg in regionDiff(vreg, breg):
                for val, (x, y) in observer(reg).cells():
                    surf.blit(TileRegistry[val].img, ((x - tile[0]) * tile_w - offset[0], 
                                                      (y - tile[1]) * tile_h - offset[1]))
            for (x, y), val in self.bufdirty.items():
                surf.blit(TileRegistry[val].img, ((x - tile[0]) * tile_w - offset[0], 
                                                  (y - tile[1]) * tile_h - offset[1]))
        self.bufdirty = {}
        bufreg = Region(vreg.x + 1, vreg.y + 1, vreg.w-2, vreg.h-2)
        watchreg = Region(vreg.x - 3, vreg.y - 3, vreg.w + 5, vreg.h + 5)
        if self.watch: self.world.unregister_watch(self.watch)
        self.watch = self.world.register_watch(watchreg, self.dirty_buf_cb)
        self.buf = (self.x, self.y, surf, bufreg)
    def dirty_buf_cb(self, x, y, newval):
        self.bufdirty[(x, y)] = newval
    def get_load_requests(self):
        if self.buf == None: return set()
        loadrad = 66
        w, h = self.buf[2].get_size()
        tile_w, tile_h = self.world.tile_size
        (minx, maxx), (miny, maxy) = self.world.chunk_region(
            Region((self.buf[0] - loadrad) // tile_w,
                   (self.buf[1] - loadrad) // tile_h,
                   (w + 2*loadrad) // tile_w,
                   (h + 2*loadrad) // tile_h))
        toload = []
        for x in range(minx, maxx):
            for y in range(minx, maxx):
                if not self.world.is_loaded((x, y)):
                    toload.append((x, y))
                if len(toload) > 3:
                    return {self.world.aload(chunk) for chunk in toload}
        return {self.world.aload(chunk) for chunk in toload}