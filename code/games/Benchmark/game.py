from pycogame import Display, Clock, color565, XglcdFont, Fonts, Input, Sound
from urandom import randint

CLR_BLACK = color565(0,0,0)
CLR_YELLOW = color565(255,255,0)

class Bouncer():
    def __init__(self, display, size, img, del_img):
        self.display = display
        self.size = size
        self.img = img
        self.del_img = del_img
        self.x = randint(0,self.display.width-size)
        self.y = randint(0,self.display.height-size)
        self.sx = 0.1
        self.sy = 0.1
        if randint(0,1) == 0:
            self.sx = self.sx * -1
        if randint(0,1) == 0:
            self.sy = self.sy * -1
        
    def update(self, dt):
        self.display.draw_sprite(self.del_img, self.x, self.y)
        sx = self.sx
        sy = self.sy
        size = self.size
        self.x += int(sx * dt)
        self.y += int(sy * dt)
        if self.x + size > self.display.width or self.x < 0:
            self.x -= int(sx * dt)
            self.sx = sx * -1
        if self.y + size > self.display.height or self.y < 0:
            self.y -= int(sy * dt)
            self.sy = sy * -1
        self.display.draw_sprite(self.img, self.x, self.y)

display = Display()
clock = Clock(240)
sound = Sound()
input = Input()
small_font = XglcdFont(Fonts.small)

s16 = display.load_sprite('./bench/16.raw', 16, 16)
d16 = display.load_sprite('./bench/d16.raw', 16, 16)
s24 = display.load_sprite('./bench/24.raw', 24, 24)
d24 = display.load_sprite('./bench/d24.raw', 24, 24)
s32 = display.load_sprite('./bench/32.raw', 32, 32)
d32 = display.load_sprite('./bench/d32.raw', 32, 32)
s64 = display.load_sprite('./bench/64.raw', 64, 64)
d64 = display.load_sprite('./bench/d64.raw', 64, 64)

scene = 0
mscene = 4
fpst = 0
first = True

display.clear()
while True:
    dt = clock.tick()
    input.get_inputs(dt)
    sound.update(dt)
    fpst += dt    

    if input.a_pressed:
        first = True
        scene += 1
        if scene > mscene:
            scene = 0

    if fpst > 100:
        fpst = 0
        display.text(0,0, str(clock.get_fps()), small_font, CLR_YELLOW, CLR_BLACK)

    if scene == 0:
        if first:
            display.clear()
            bouncers = [ Bouncer(display, 16, s16, d16) for b in range(10) ]
            first = False
        for b in bouncers:
            b.update(dt)

    if scene == 1:
        if first:
            display.clear()
            bouncers = [ Bouncer(display, 24, s24, d24) for b in range(10) ]
            first = False
        for b in bouncers:
            b.update(dt)

    if scene == 2:
        if first:
            display.clear()
            bouncers = [ Bouncer(display, 32, s32, d32) for b in range(10) ]
            first = False
        for b in bouncers:
            b.update(dt)

    if scene == 3:
        if first:
            display.clear()
            bouncers = [ Bouncer(display, 64, s64, d64) for b in range(10) ]
            first = False
        for b in bouncers:
            b.update(dt)

    if scene == 4:
        if first:
            display.clear()
            first = False
        pass