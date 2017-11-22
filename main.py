import sys, pygame, math
pygame.init()

size = width, height = 1280, 960
speed = [2, 2]
black = 0, 0, 0

clock = pygame.time.Clock()

screen = pygame.display.set_mode(size)

rect = pygame.Rect(0, 0, 10, 10)

tile_w, tile_h = 32, 32
imgs = [pygame.Surface((tile_w, tile_h),) for i in range(10)]
img_rects = [surf.fill((int(255 - 20 * n), 20 * n, 100),) for n, surf in enumerate(imgs)]

camera = [0, 0]
cam_speed = 7

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    rect = rect.move(speed)
    if rect.left < 0 or rect.right > width:
        speed[0] = -speed[0]
    if rect.top < 0 or rect.bottom > height:
        speed[1] = -speed[1]

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]: camera[1] -= cam_speed
    if pressed[pygame.K_DOWN]: camera[1] += cam_speed
    if pressed[pygame.K_LEFT]: camera[0] -= cam_speed
    if pressed[pygame.K_RIGHT]: camera[0] += cam_speed
    screen.fill(black)
    cam_tile, cam_offset = zip(divmod(camera[0], tile_w), divmod(camera[1], tile_h))
    for X in range(int(width / tile_w) + 1):
        tile_x = cam_tile[0] + X
        for Y in range(int(height / tile_h) + 1):
            tile_y = cam_tile[1] + Y
            screen.blit(imgs[(tile_x + tile_x*tile_y) % len(imgs)], (X * 32 - cam_offset[0],
                                                                     Y * 32 - cam_offset[1]))
    pygame.draw.rect(screen, pygame.Color('0x0061ff'), rect)
    pygame.display.flip()
    clock.tick(60)