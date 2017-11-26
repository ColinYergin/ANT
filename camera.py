import world
from common import Region, debugPrint

class Camera:
    def __init__(self, world, imgs, coords = (0, 0), centerin = (0, 0)):
        self.world = world
        self.imgs = imgs
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
            for row in observer(vreg).rows():
                for val, (x, y) in row.cells():
                    surf.blit(self.imgs[val], ((x - tile[0]) * tile_w - offset[0], 
                                               (y - tile[1]) * tile_h - offset[1]))
        else:
            bx, by, bs, breg = self.buf
            surf.blit(bs, (bx - self.x, by - self.y))
            
            for row in observer(vreg, ignoring = breg).rows():
                for val, (x, y) in row.cells():
                    surf.blit(self.imgs[val], ((x - tile[0]) * tile_w - offset[0], 
                                               (y - tile[1]) * tile_h - offset[1]))
            for (x, y), val in self.bufdirty.items():
                surf.blit(self.imgs[val], ((x - tile[0]) * tile_w - offset[0], 
                                           (y - tile[1]) * tile_h - offset[1]))
        self.bufdirty = {}
        screenreg = Region(vreg.x, vreg.y, vreg.w-1, vreg.h-1)
        if self.watch: self.world.unregister_watch(self.watch)
        self.watch = self.world.register_watch(screenreg, self.dirty_buf_cb)
        self.buf = (self.x, self.y, surf.copy(), screenreg)
    def dirty_buf_cb(self, x, y, newval):
        self.bufdirty[(x, y)] = newval