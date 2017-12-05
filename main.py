import sys, pygame, math, asyncio, time
from world import World
from gen import Generator
from camera import Camera
from controls import Controls
from agent import FallingSandAgent, RunnerAgent
from common import debugPrint, tilesize
pygame.init()

size = width, height = 1280, 960
screen = pygame.display.set_mode(size, pygame.RESIZABLE)

world = World(Generator(), tilesize)
cam = Camera(world, (0, 0), size)
cam_speed = 7
frames_per_tick = 15

running = True
def shutdown(event = None):
    global running
    running = False
def window_resize(event):
    global screen
    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

controls = Controls()
controls.on_event(pygame.QUIT, shutdown)
controls.on_event(pygame.VIDEORESIZE, window_resize)
controls.while_pressed(pygame.K_UP, lambda: cam.move_y(-cam_speed))
controls.while_pressed(pygame.K_DOWN, lambda: cam.move_y(cam_speed))
controls.while_pressed(pygame.K_LEFT, lambda: cam.move_x(-cam_speed))
controls.while_pressed(pygame.K_RIGHT, lambda: cam.move_x(cam_speed))
controls.while_pressed(pygame.K_ESCAPE, shutdown)

for i in range(20, 50):
    idler = FallingSandAgent.build(y = -i)
    world.add(idler)

worker = RunnerAgent(x = -30, y = -10)
world.add(worker)

class AdaptiveSleeper:
    def __init__(self):
        self.est_error = 0
    def _sleep(self, curtime, duration):
        duration = duration - 2 * self.est_error
        if duration < 0: return curtime
        time.sleep(duration)
        endtime = time.time()
        self.est_error = self.est_error * .9 + (endtime - curtime) * .1
        return endtime
    def __call__(self, timeout):
        if timeout < 0: return
        curtime = start = time.time()
        curtime = self._sleep(curtime, timeout - (curtime - start))
        while curtime - start < timeout * .98:
            curtime = time.time()
        
        
def adaptive_sleep(timeout):
    curtime = start = time.time()
    while curtime - start < timeout - 2 * est_error:
        time.sleep

async def gameloop():
    global running
    global screen
    frame = 0
    camdraw_tott = 0
    lastframe = time.time()
    done = set()
    pending = set()
    required = set()
    sleeper = AdaptiveSleeper()
    while running:
        # Control Stage
        controls.run()
        
        # World Step Stage
        frame += 1
        if frame % frames_per_tick == 0:
            if any(r in pending for r in required):
                pending -= required
                done, _ = await asyncio.wait(required, timeout = None)
                required = set()
            world.step()
            required = {world.prepare_step()}
            pending |= required
        
        # Extra Jobs Stage
        pending |= cam.get_load_requests()
        target_time = 1 / 60 - camdraw_tott / frame
        timeout = target_time - (time.time() - lastframe) - .1/60
        if len(pending) > 0 and timeout > 0:
            startt = time.time()
            done, pending = await asyncio.wait(pending, timeout = timeout)
            if timeout - (time.time() - startt) < -.005:
                print("Over time:", time.time() - startt - timeout)
        
        # Render Stage
        camdraw_startt = time.time()
        cam.draw_to(screen)
        camdraw_tott += time.time() - camdraw_startt
        
        # Wait and display phase
        sleeper(1 / 60 - (time.time() - lastframe))
        
        curtime = time.time()
        framerate = 1 / (curtime - lastframe)
        lastframe = curtime
        if framerate < 50 or framerate > 70: debugPrint(framerate)
        pygame.display.flip()
    if len(pending) > 0:
        await asyncio.wait(pending, timeout = None)
loop = asyncio.get_event_loop()
loop.run_until_complete(gameloop())
loop.close()