from pycogame import Display, Clock, color565, XglcdFont, Fonts, Sound, Input
from urandom import randint


CLR_BLACK = color565(0,0,0)
CLR_WATER = color565(0,112,255)


class Tux():
    def __init__(self, display, input, x, y):
        self.display = display
        self.input = input
        self.x = x
        self.y = y
        self.vspeed = 0
        self.img_tux = (Display.load_sprite('./img/tux0.raw', 16, 16),
                        Display.load_sprite('./img/tux1.raw', 16, 16))
        self.img_tux_left = (Display.load_sprite('./img/tux0_l1.raw', 15, 16),
                             Display.load_sprite('./img/tux0_l2.raw', 14, 16),
                             Display.load_sprite('./img/tux0_l3.raw', 13, 16),
                             Display.load_sprite('./img/tux0_l4.raw', 12, 16),
                             Display.load_sprite('./img/tux0_l5.raw', 11, 16),
                             Display.load_sprite('./img/tux0_l6.raw', 10, 16),
                             Display.load_sprite('./img/tux0_l7.raw', 9, 16),
                             Display.load_sprite('./img/tux0_l8.raw', 8, 16),
                             Display.load_sprite('./img/tux0_l9.raw', 7, 16),
                             Display.load_sprite('./img/tux0_l10.raw', 6, 16),
                             Display.load_sprite('./img/tux0_l11.raw', 5, 16),
                             Display.load_sprite('./img/tux0_l12.raw', 4, 16),
                             Display.load_sprite('./img/tux0_l13.raw', 3, 16),
                             Display.load_sprite('./img/tux0_l14.raw', 2, 16),
                             Display.load_sprite('./img/tux0_l15.raw', 1, 16))
        self.img_tux_right = (Display.load_sprite('./img/tux0_r1.raw', 15, 16),
                              Display.load_sprite('./img/tux0_r2.raw', 14, 16),
                              Display.load_sprite('./img/tux0_r3.raw', 13, 16),
                              Display.load_sprite('./img/tux0_r4.raw', 12, 16),
                              Display.load_sprite('./img/tux0_r5.raw', 11, 16),
                              Display.load_sprite('./img/tux0_r6.raw', 10, 16),
                              Display.load_sprite('./img/tux0_r7.raw', 9, 16),
                              Display.load_sprite('./img/tux0_r8.raw', 8, 16),
                              Display.load_sprite('./img/tux0_r9.raw', 7, 16),
                              Display.load_sprite('./img/tux0_r10.raw', 6, 16),
                              Display.load_sprite('./img/tux0_r11.raw', 5, 16),
                              Display.load_sprite('./img/tux0_r12.raw', 4, 16),
                              Display.load_sprite('./img/tux0_r13.raw', 3, 16),
                              Display.load_sprite('./img/tux0_r14.raw', 2, 16),
                              Display.load_sprite('./img/tux0_r15.raw', 1, 16))
        self.anim = 0
        self.anim_timer = 0
        self.def_col = (16, 239)
        self.col = self.def_col
        self.col_timer = 0
        self.score = 0

    def calc_x(self, offset, x=None):
        if x is None:
            x = self.x
        if x+320-offset > 320:
            return x-offset
        else:
            return x+320-offset

    def clear(self, offset, speed):
        self.display.fill_rect(0, int(self.y), 16, 16, CLR_WATER)
        self.display.fill_rect(self.calc_x(offset+speed), int(self.y), 16+speed, 16, CLR_WATER)

    def update(self, dt, offset, walls):
        # Animation
        self.anim_timer += dt
        if self.anim_timer > 220:
            self.anim_timer = 0
            self.anim = abs(self.anim-1)

        # Physics
        self.vspeed -= 0.4
        if self.input.a_pressed:
            self.vspeed += 6
        self.y = self.y - self.vspeed

        # Draw tux
        # Calculate tux x position
        x = self.calc_x(offset)
        # Calculate tux image crop
        crop = -320+(x+14)
        if crop < 0:
            # No crop, draw animated tux
            self.display.draw_sprite(self.img_tux[self.anim],x, int(self.y))
        else:
            # Draw split to avoid drawing offscreen
            self.display.draw_sprite(self.img_tux_right[crop], x-1, int(self.y))
            self.display.draw_sprite(self.img_tux_left[14-crop], 0, int(self.y))

        # Collisions
        x = self.calc_x(offset, self.x+16)
        col = None
        for wall in walls:
            if wall is not None and wall[0] == x:
                col = wall[1]
        if col is not None:
            self.col_timer = 32
            self.col = col
        elif self.col_timer == 0:
            self.col = self.def_col
        if self.col_timer > 0:
            self.col_timer -= 1
            if self.col_timer == 0:
                self.score += 1

        if self.y+16 > self.col[1] or self.y < self.col[0]:
            return True
        return False


class Walls():
    def __init__(self, display):
        self.display = display
        self.img_ice_tl = Display.load_sprite('./img/ice_tl.raw', 16, 32)
        self.img_ice_tr = Display.load_sprite('./img/ice_tr.raw', 16, 32)
        self.img_ice_m = Display.load_sprite('./img/ice_m.raw', 16, 32)
        self.img_ice_bl = Display.load_sprite('./img/ice_bl.raw', 16, 16)
        self.img_ice_br = Display.load_sprite('./img/ice_br.raw', 16, 16)
        self.img_rock_tl = Display.load_sprite('./img/rock_tl.raw', 16, 16)
        self.img_rock_tr = Display.load_sprite('./img/rock_tr.raw', 16, 16)
        self.img_rock_m = Display.load_sprite('./img/rock_m.raw', 16, 32)

        self.counter = 6
        self.draw_right = False
        self.last_ypos = 0
        self.walls = [None]

    def update(self, offset):
        self.counter += 1
        if self.counter == 7:
            ypos = randint(0, 4)
            y = ypos
            x = 320-offset

            self.last_ypos = ypos
            self.draw_right = True
            self.counter = 0
            
            display.draw_sprite(self.img_ice_tl, x, 0)
            for y in range(1,ypos+1):
                display.draw_sprite(self.img_ice_m, x, 32*y)
            display.draw_sprite(self.img_ice_bl, x, 32*(y+1))

            top_y = 32*(y+1)+16
            bot_y = 224-32*(4-y)

            display.draw_sprite(self.img_rock_tl, x, 224-32*(4-y)) 
            for y in range(1,(4-ypos+1)):
                display.draw_sprite(self.img_rock_m, x, 240-32*y)

            self.walls.append((x, (top_y, bot_y)))
            if len(self.walls) > 3:
                self.walls.pop(0)

        elif self.draw_right:
            self.draw_right = False
            ypos = self.last_ypos
            y = ypos
            x = 320-offset
            
            display.draw_sprite(self.img_ice_tr, x, 0)
            for y in range(1,ypos+1):
                display.draw_sprite(self.img_ice_m, x, 32*y)
            display.draw_sprite(self.img_ice_br, x, 32*(y+1))
            
            display.draw_sprite(self.img_rock_tr, x, 224-32*(4-y)) 
            for y in range(1,(4-ypos+1)):
                display.draw_sprite(self.img_rock_m, x, 240-32*y)


# Load sprites
img_wave = Display.load_sprite('./img/wave.raw', 16, 16)

display = Display()
clock = Clock()
sound = Sound()
input = Input()

# load fonts
medium_font = XglcdFont(Fonts.medium)
large_font = XglcdFont(Fonts.large)

def draw_waves():
    for x in range(20):
        display.draw_sprite(img_wave, 16*x, 0)

def play():
    display.clear(CLR_WATER)
    draw_waves()
    tux = Tux(display, input, 80, 112)
    walls = Walls(display)
    offset = 320
    speed = 1

    clock.tick()
    while True:
        dt = clock.tick()
        sound.update(dt)
        input.get_inputs(dt)

        tux.clear(offset, speed)

        offset -= speed
        if offset == 0:
            offset = 320
        
        if tux.update(dt, offset, walls.walls):
            break

        if offset%16 == 0:
            display.fill_rect(320-offset, 0, 16, 240, CLR_WATER)
            display.draw_sprite(img_wave, 320-offset, 0)
            walls.update(offset)

        display.scroll(offset)

    display.scroll(0)
    display.text(100,100,'GAME OVER', large_font, CLR_BLACK, CLR_WATER)
    display.text(130,130,'Score: '+str(tux.score), medium_font, CLR_BLACK, CLR_WATER)

# Game restart loop
end = False
while True:
    if not end:
        play()
        clock.sleep(1)
        end = True

    dt = clock.tick()
    input.get_inputs(dt)
    if input.a_pressed:
        end = False
