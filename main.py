import sys, pygame, math, asyncio, time
from world import World
from gen import Generator
from camera import Camera
from controls import Controls
from agent import DummyAgent, WorkerAgent
from common import debugPrint
pygame.init()

size = width, height = 1280, 960
screen = pygame.display.set_mode(size, pygame.RESIZABLE)

world = World(Generator())
imgs = [pygame.Surface(world.tile_size) for i in range(10)]
img_rects = [surf.fill((int(255 - 20 * n), 20 * n, 100),) for n, surf in enumerate(imgs)]
cam = Camera(world, imgs, (0, 0), size)
cam_speed = 7
frames_per_tick = 4

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

idler = DummyAgent()
world.add(idler)

worker = WorkerAgent(y = -10, tile_num = 7)
world.add(worker)

async def gameloop():
    global running
    global screen
    frame = 0
    drawtime = 0
    lastframe = time.time()
    done = set()
    pending = set()
    required = set()
    while running:
        controls.run()
        pending |= cam.get_load_requests()
        frame += 1
        if frame % frames_per_tick == 0:
            if any(r in pending for r in required):
                pending -= required
                done, _ = await asyncio.wait(required, timeout = None)
                required = set()
            world.step()
            required = {world.prepare_step()}
            pending |= required
        
        target_time = 1 / 60 - drawtime / frame
        timeout = target_time - (time.time() - lastframe) - .1/60
        if len(pending) > 0 and timeout > 0:
            startt = time.time()
            done, pending = await asyncio.wait(pending, timeout = timeout)
            if timeout - (time.time() - startt) < -.005:
                print("Over time:", time.time() - startt - timeout)
        timeout = target_time - (time.time() - lastframe)
        while timeout > 0:
            time.sleep(timeout / 2)
            timeout = (target_time - (time.time() - lastframe)) / 2
        predraw_time = time.time()
        cam.draw_to(screen) # TODO SWAP THIS WITH THE TIME SLEEP AND FIX TIMING STUFF
        pygame.display.flip()
        curtime = time.time()
        framerate = 1 / (curtime - lastframe)
        if framerate < 50 or framerate > 70: debugPrint(framerate)
        lastframe = curtime
        drawtime += lastframe - predraw_time
    if len(pending) > 0:
        await asyncio.wait(pending, timeout = None)
loop = asyncio.get_event_loop()
loop.run_until_complete(gameloop())
loop.close()