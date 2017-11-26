import sys, pygame, math
from world import World
from gen import Generator
from camera import Camera
from controls import Controls
from agent import DummyAgent
pygame.init()
clock = pygame.time.Clock()

size = width, height = 1280, 960
screen = pygame.display.set_mode(size, pygame.RESIZABLE)

world = World(Generator())
imgs = [pygame.Surface(world.tile_size) for i in range(10)]
img_rects = [surf.fill((int(255 - 20 * n), 20 * n, 100),) for n, surf in enumerate(imgs)]
cam = Camera(world, imgs, (0, 0), size)
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

idler = DummyAgent()
world.add(idler)

frame = 0
while running:
    controls.run()
    frame += 1
    if frame % frames_per_tick == 0:
        world.step()
    cam.draw_to(screen)
    pygame.display.flip()
    clock.tick(60)