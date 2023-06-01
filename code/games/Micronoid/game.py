from pycogame import Display, Clock, color565, XglcdFont, Fonts, Sound, Input
from urandom import randint
from gc import collect, mem_free
from uos import listdir

CLR_BLACK = color565(0,0,0)
CLR_WHITE = color565(255,255,255)


def draw_walls(display, l, r):
    for y in range(12):
        display.draw_image('./img/wl.raw', l, 20*y, 10, 20)
        display.draw_image('./img/wr.raw', r, 20*y, 10, 20)

def list_levels(path='./levels'):
    lvls = []
    for lvl in listdir(path):
        lvls.append((lvl, path + '/' + lvl))
    return lvls

def load_music(name, rtl_file='./music.rtl'):
    with open(rtl_file, 'r') as fo:
        for line in fo:
            if line.split(':',1)[0] == name:
                return line


class Ball():
    def __init__(self, game, x, y, img=None, clr_img=None):
        self.game = game
        self.display = game.display
        self.level = game.level
        self.x = x
        self.w = 5
        self.y = y
        self.h = 5
        self.sx = 0.05
        self.sy = -0.05
        self.min_s = -0.025
        self.max_s = -0.075
        if img is None:
            self.img = Display.load_sprite('./img/ball.raw', 5, 5)
        else:
            self.img = img
        if clr_img is None:
            self.clr_img = Display.load_sprite('./img/clr_ball.raw', 5, 5)
        else:
            self.clr_img = clr_img

    def bonk(self, high=False):
        if high:
            self.game.sound.play_effect([10,[(800,10)]])
        else:
            self.game.sound.play_effect([10,[(500,10)]])

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.sx = 0.05
        self.sy = -0.05        

    def update(self, dt):
        x = self.x + self.sx * dt
        y = self.y + self.sy * dt
        min_x = self.game.pa_xs
        max_x = self.game.pa_xe-self.w
        min_y = self.game.pa_ys
        max_y = self.game.pa_ye-self.h
        brick_h = self.level.brick_h
        brick_w = self.level.brick_w
        level = self.level.level

        # TODO: brick colision is not working perfectly it can go through if it hits the edge
        #       or it can bounce from top of a brick when it hits it from side
        #       or it can bounce from top or side of a brick but doesn't remove it

        # Check if ball penetrates line of bricks
        try: # check line at bottom edge of ball
            by = int((y+self.h-min_y)/brick_h)
            level[by]
            bx = int((x+self.w-min_x)/brick_w) # brick at right edge of ball
            brick_at_ball = level[by][bx]
            if brick_at_ball is None:
                bx = int((x-min_x)/brick_w) # brick at left edge of ball
                brick_at_ball = level[by][bx]
        except:
            brick_at_ball = None

        if brick_at_ball is None: # if brick was not found
            try: # check line at top edge of ball
                by = int((y-min_y)/brick_h)
                level[by]
                bx = int((x+self.w-min_x)/brick_w) # brick at right edge of ball
                brick_at_ball = level[by][bx]
                if brick_at_ball is None:
                    bx = int((x-min_x)/brick_w) # brick at left edge of ball
                    brick_at_ball = level[by][bx]
            except:
                brick_at_ball = None

        if brick_at_ball is not None:
            # Check if the ball was on the previous frame on the same height as the brick - it hit it from a side
            # bottom edge was inside brick or top edge was inside brick
            br_top = (by)*brick_h
            br_bot = (by+1)*brick_h
            from_side = ((self.y < br_bot and self.y > br_top) or
                         (self.y+self.h < br_bot and self.y+self.h > br_top))
            # Update the brick that the ball cloided with
            self.level.update(bx, by)

        # calculate y position and speed
        # roof colision
        if min_y > y:
            new_y = min_y
            self.sy = self.sy * -1
            self.bonk()
        # floor colision
        elif max_y < y: 
            #new_y = max_y
            #self.sy = self.sy * -1
            self.game.mod_lives(-1)
            self.game.reset()
            return
        # brick colision
        elif brick_at_ball is not None and not from_side:
            if self.sy > 0: # going down
                new_y = by * brick_h - self.h + min_y
            else:           # going up
                new_y = by * brick_h + brick_h + min_y
            self.sy = self.sy * -1
            self.bonk(True)
        # paddle colision
        elif (y + self.h > self.game.paddle.y and 
              (x+self.w >= self.game.paddle.left and x <= self.game.paddle.right)):
            new_y = self.game.paddle.y - self.h
            self.sy = self.sy * -1
            # adjust speed based on where it hit the paddle
            adjx = (x + 2 - self.game.paddle.x)*0.001
            # if speed x will increase -> decrease speed x
            if (self.sx < 0 and adjx < 0) or (self.sx > 0 and adjx > 0):
                if self.sy+abs(adjx) > self.min_s: # limit adjusment based on min y speed
                    adj = self.sy - self.min_s
                    # keep adjx positive if it was positive
                    if adjx > 0: adjx = adj*-1
                    else: adjx = adj
                self.sy += abs(adjx)
            # else speed x will decrease -> increase speed y
            else:
                if self.sy-abs(adjx) < self.max_s: # limit adjusment based on max y speed
                    adj = self.sy - self.max_s
                    # keep adjx negative if it was negative
                    if adjx < 0: adjx = adj*-1
                    else: adjx = adj
                self.sy -= abs(adjx)
            self.sx += adjx
            self.bonk()
        # no colision
        else:
            new_y = y

        # calculate x position and speed
        # wall colison
        if min_x > x:
            new_x = min_x
            self.sx = self.sx * -1
            self.bonk()
        # wall colison
        elif max_x < x:
            new_x = max_x
            self.sx = self.sx * -1
            self.bonk()
        # brick colision
        elif brick_at_ball is not None and from_side:
            if self.sx > 0: # going right
                new_x = bx * brick_w - self.w + min_x
            else:           # going left
                new_x = bx * brick_w + brick_w + min_x
            self.sx = self.sx * -1
            self.bonk(True)
        # no colision
        else:
            new_x = x

        # re-draw
        display.draw_sprite(self.clr_img, int(self.x), int(self.y))
        self.x = new_x
        self.y = new_y
        display.draw_sprite(self.img, int(self.x), int(self.y))

class Items():
    def __init__(self, game):
        self.game = game
        self.display = game.display
        self.sy = 0.05
        self.max = 2
        self.items = []
        self.w = 10
        self.h = 5
        self.chance = 1
        self.max_y = self.game.pa_ye-self.h
        self.img_g = self.display.load_sprite('./img/ig.raw', self.w, self.h)
        self.img_b = self.display.load_sprite('./img/ib.raw', self.w, self.h)
        self.img_r = self.display.load_sprite('./img/ir.raw', self.w, self.h)
        self.clr_img = self.display.load_sprite('./img/ic.raw', self.w, self.h)
        self.good_effects = [self._b_pad]
        self.bad_effects = [self._s_pad]
        self.rand_effects = [self._b_pad, self._s_pad]

    def reset(self):
        self.items = []

    def update(self, dt):
        tmp_list = []
        for item in self.items:
            x = item[0]
            old_y = item[1]
            y = old_y + self.sy * dt
            self.display.draw_sprite(self.clr_img, x, int(old_y))
            # floor colision
            if self.max_y < y: 
                continue
            # paddle colision
            if (y + self.h > self.game.paddle.y and 
                (x+self.w >= self.game.paddle.left and x <= self.game.paddle.right)):
                if item[2] == 'g':
                    self.good_effects[randint(0, len(self.good_effects)-1)]()
                if item[2] == 'b':
                    self.bad_effects[randint(0, len(self.bad_effects)-1)]()
                if item[2] == 'r':
                    self.rand_effects[randint(0, len(self.rand_effects)-1)]()
                continue
            # no colision
            item[1] = y
            if item[2] == 'g':
                self.display.draw_sprite(self.img_g, x, int(y))
            if item[2] == 'b':
                self.display.draw_sprite(self.img_b, x, int(y))
            if item[2] == 'r':
                self.display.draw_sprite(self.img_r, x, int(y))
            tmp_list.append(item)
        self.items = tmp_list

    def add(self, x, y):
        if not 0 == randint(0,self.chance):
            return
        if len(self.items) < self.max:
            self.items.append([x, y, ['g','b','r'][randint(0,2)]])

    def _b_pad(self):
        if not self.game.paddle.seg_increase():
            self.game.mod_lives(1)
    def _s_pad(self):
        if not self.game.paddle.seg_decrease():
            self.game.mod_lives(-1)

class Level():
    def __init__(self, game):
        self.game = game
        self.display = game.display
        self.brick_w = 16
        self.brick_h = 7
        self.clr_img = self.display.load_sprite('./img/clr_b.raw', self.brick_w, self.brick_h)
        # load bricks
        self.bricks = [display.load_sprite('./img/b0.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b1.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b2.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b3.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b4.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b5.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b6.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b70.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b71.raw', self.brick_w, self.brick_h),
                       display.load_sprite('./img/b72.raw', self.brick_w, self.brick_h)]

    def load(self, lvl_id, score):
        # load level
        with open(list_levels()[lvl_id][1], 'r') as lvl_file:
            lines = lvl_file.readlines()
        self.level = []
        self.max_score = score
        y = 0
        for line in lines:
            x = 0
            self.level.append([])
            for char in line:
                if char in ['\n', '\r']:
                    break
                if char == ' ':
                    self.level[y].append(None)
                else:
                    brick = int(char)
                    self.level[y].append(brick)
                    self.display.draw_sprite(self.bricks[brick],
                                             self.brick_w*x+self.game.pa_xs,
                                             self.brick_h*y+self.game.pa_ys)
                    # Calculate maximum score
                    if brick in range(0,6):
                        self.max_score += 10*brick
                    elif brick == 7:
                        self.max_score += 100
                x += 1
            y += 1

    def update(self, x, y):
        brick = self.level[y][x]
        # Standard bricks
        if brick in range(0,6):
            self.level[y][x] = None
            self.game.mod_score(10*brick)
            lcd_x = self.brick_w*x+self.game.pa_xs
            lcd_y = self.brick_h*y+self.game.pa_ys
            self.display.draw_sprite(self.clr_img, lcd_x, lcd_y)
            
            # Try to spawn item
            clis = True # Clear line of sight to floor
            for b in self.level[y:-1]:
                if b[x] is not None:
                    clis = False
            if clis:
                self.game.items.add(lcd_x, lcd_y)

        # Ice bricks
        if brick == 7:
            self.level[y][x] = 71
            self.display.draw_sprite(self.bricks[8],
                                     self.brick_w*x+self.game.pa_xs,
                                     self.brick_h*y+self.game.pa_ys)
        if brick == 71:
            self.level[y][x] = 72
            self.display.draw_sprite(self.bricks[9],
                                     self.brick_w*x+self.game.pa_xs,
                                     self.brick_h*y+self.game.pa_ys)
        if brick == 72:
            self.level[y][x] = None
            self.game.mod_score(100)
            self.display.draw_sprite(self.clr_img,
                                     self.brick_w*x+self.game.pa_xs,
                                     self.brick_h*y+self.game.pa_ys)

class Paddle():
    def __init__(self, game):
        self.game = game
        self.display = game.display
        self.input = game.input
        self.segments = 6
        self.seg_s = 7
        self.y = 230
        self.speed = 0.1
        self.x = int(self.game.pa_xs + self.game.pa_xe / 2)
        self.rad = int(self.segments / 2 * self.seg_s)
        self.left = int(self.x - self.rad)
        self.right = int(self.x + self.rad)
        self.img_l = self.display.load_sprite('./img/pl.raw', self.seg_s, self.seg_s)
        self.img_m = self.display.load_sprite('./img/pm.raw', self.seg_s, self.seg_s)
        self.img_r = self.display.load_sprite('./img/pr.raw', self.seg_s, self.seg_s)
    
    def reset(self):
        self.segments = 6
        self.x = int(self.game.pa_xs + self.game.pa_xe / 2)
        self.rad = int(self.segments / 2 * self.seg_s)
        self.left = int(self.x - self.rad)
        self.right = int(self.x + self.rad)

    def seg_decrease(self):
        ok = False
        if self.segments-2 >= 3:
            self.segments -= 2
            ok = True
        else:
            self.segments = 3
        self.rad = int(self.segments / 2 * self.seg_s)
        self.right = int(self.x + self.rad)
        self.left = int(self.x - self.rad)
        # clear segments after decreasing size
        self.display.fill_rect(self.right, self.y, self.seg_s, self.seg_s, CLR_BLACK)
        self.display.fill_rect(self.left-self.seg_s, self.y, self.seg_s, self.seg_s, CLR_BLACK)
        return ok

    def seg_increase(self):
        ok = False
        if self.segments+2 <= 12:
            self.segments += 2
            ok = True
        else:
            self.segments = 12
        self.rad = int(self.segments / 2 * self.seg_s)
        self.right = int(self.x + self.rad)
        self.left = int(self.x - self.rad)
        if self.left < self.game.pa_xs:
            self.x += self.seg_s
            self.right = int(self.x + self.rad)
            self.left = int(self.x - self.rad)
        elif self.right > self.game.pa_xe:
            self.x -= self.seg_s
            self.right = int(self.x + self.rad)
            self.left = int(self.x - self.rad)
        return ok

    def update(self, dt):
        speed = self.speed * dt

        if self.input.left_on:
            x = self.x - speed
            if x - self.rad > self.game.pa_xs:
                self.x = x
                self.right = int(self.x + self.rad)
                self.left = int(self.x - self.rad)
                # Clear paddle
                self.display.fill_rect(self.right, self.y, int(speed)+2, self.seg_s, CLR_BLACK)
            else:
                self.x = self.game.pa_xs + self.rad+1
                self.right = int(self.x + self.rad)
                self.left = int(self.x - self.rad)
                # Clear paddle
                self.display.fill_rect(self.right, self.y, self.seg_s, self.seg_s, CLR_BLACK)

        if self.input.right_on:
            x = self.x + speed
            if x + self.rad < self.game.pa_xe:
                self.x = x
                self.right = int(self.x + self.rad)
                self.left = int(self.x - self.rad)
                # Clear paddle
                self.display.fill_rect(self.left-int(speed)-1, self.y, int(speed)+1, self.seg_s, CLR_BLACK)
            else:
                self.x = self.game.pa_xe - self.rad
                self.right = int(self.x + self.rad)
                self.left = int(self.x - self.rad)
                # Clear paddle
                self.display.fill_rect(self.left-self.seg_s, self.y, self.seg_s, self.seg_s, CLR_BLACK)

        # Draw paddle
        for seg in range(self.segments):
            x = int(self.left + self.seg_s * seg)
            if seg == 0:
                self.display.draw_sprite(self.img_l, x, self.y)
            elif seg == self.segments-1:
                self.display.draw_sprite(self.img_r, x, self.y)
            else:
                self.display.draw_sprite(self.img_m, x, self.y)


class Game():
    def __init__(self, display, clock, sound, input, state):
        self.display = display
        self.clock = clock
        self.sound = sound
        self.input = input
        self.state = state
        self.small_font = XglcdFont(Fonts.small)
        # play area
        self.pa_xs = 10
        self.pa_xe = 249
        self.pa_ys = 0
        self.pa_ye = 239
        # init game
        draw_walls(display, self.pa_xs-10, self.pa_xe+1)
        self.score = state[2]
        self.lives = state[4]
        self.draw_state_text(270)
        self.level = Level(self)
        self.level.load(state[1], self.score)
        self.paddle = Paddle(self)
        self.ball = Ball(self, self.paddle.x, self.paddle.y-5)
        self.items = Items(self)

        self.draw_state(270, lives=self.lives, level=1, score=self.score)

    def draw_state_text(self, x):
        self.display.text(x, 20, 'LEVEL', self.small_font)
        self.display.text(x, 80, 'LIVES', self.small_font)
        self.display.text(x, 140, 'SCORE', self.small_font)
        self.display.text(x, 200, 'FPS', self.small_font)

    def mod_score(self, s):
        self.score += s
        self.draw_state(270, score=self.score)

    def mod_lives(self, l):
        self.lives += l
        self.draw_state(270, lives=self.lives)

    def draw_state(self, x, level=None, lives=None, score=None, fps=None):
        if level is not None:
            self.display.text(x, 30, str(level), self.small_font)
        if lives is not None:
            self.display.text(x, 90, str(lives), self.small_font)
        if score is not None:
            self.display.text(x, 150, str(score), self.small_font)
        if fps is not None:
            self.display.text(x, 210, str(fps), self.small_font)

    def reset(self):
        self.display.fill_rect(self.pa_xs, 220, self.pa_xe-self.pa_xs, 20, CLR_BLACK)
        self.paddle.reset()
        self.ball.reset(self.paddle.x, self.paddle.y-5)
        self.items.reset()
        self.ball.update(0)
        self.paddle.update(0)
        self.items.update(0)
        if self.lives > -1:
            self.clock.sleep(1)
        self.clock.tick()

    def run(self):
        win = False
        self.ball.update(0)
        self.paddle.update(0)
        self.clock.sleep(1)
        self.clock.tick()
        while True:
            dt = self.clock.tick()
            self.sound.update(dt)
            self.input.get_inputs(dt)
            self.draw_state(270, fps=self.clock.get_fps())

            self.ball.update(dt)
            self.paddle.update(dt)
            self.items.update(dt)

            if self.score == self.level.max_score:
                win = True
                break
            if self.lives < 0:
                break
            if self.input.a_pressed:
                break

        # update state
        self.state[0] = win
        self.state[2] = self.score
        return self.state


def menu(display, clock, sound, input, state):
    medium_font = XglcdFont(Fonts.medium)
    small_font = XglcdFont(Fonts.small)
    intro_music = sound.load_song(load_music('micronoid'))
    draw_walls(display, 310, 0)

    lvl = 0
    dif = 1
    lvls_list = list_levels()

    def draw_lvl(lvl):
        display.fill_rect(20,100,280,14, CLR_BLACK)
        x_off = (len(lvls_list[lvl][0]) - 7) * 4
        display.text(100 - x_off,100, ' Level ' + lvls_list[lvl][0], medium_font)

    def draw_dif(dif):
        display.text(100,120, ' Difficulty ' + str(dif), medium_font)

    # Draws help bar at the bottom of the screen
    y = 221
    x = 40
    display.draw_image('/keys/up.raw', x,y, 15,15)
    display.draw_image('/keys/down.raw', x+17,y, 15,15)
    display.text(x+40,y+4, 'Difficulty', small_font, CLR_WHITE, CLR_BLACK)
    x = 195
    display.draw_image('/keys/left.raw', x,y, 15,15)
    display.draw_image('/keys/right.raw', x+17,y, 15,15)
    display.text(x+40,y+4, 'Level', small_font, CLR_WHITE, CLR_BLACK)

    display.draw_image('./img/logo.raw', 110, 40, 109, 19)
    x = display.text(100,180, 'Press ', medium_font)
    display.draw_image('/keys/a.raw', x, 179, 15,15)
    display.text(x+15,180, ' to play', medium_font)

    draw_lvl(lvl)
    draw_dif(dif)

    while True:
        dt = clock.tick()
        sound.update(dt)
        input.get_inputs(dt)

        if not sound.song_playing():
            sound.play_song(intro_music)

        if input.left_pressed:
            if lvl > 0:
                lvl -= 1
            draw_lvl(lvl)
        if input.right_pressed:
            if lvl < len(lvls_list)-1:
                lvl += 1
            draw_lvl(lvl)
        if input.down_pressed:
            if dif > 1:
                dif -= 1
            draw_dif(dif)
        if input.up_pressed:
            if dif < 9:
                dif += 1
            draw_dif(dif)
        if input.a_pressed:
            break
    
    state[1] = lvl
    state[2] = 0 # clear score
    state[3] = dif
    sound.stop_song()
    sound.update(0)
    return state


def transition(display, clock, sound, input, state):
    medium_font = XglcdFont(Fonts.medium)
    large_font = XglcdFont(Fonts.large)
    draw_walls(display, 310, 0)
    win_music = sound.load_song(load_music('win'))
    end_music = sound.load_song(load_music('end'))

    levels = list_levels()
    new_lvl = state[1] + 1
    if new_lvl == len(levels):
        new_lvl = 0 # start from begining
        if state[3] < 9:
            state[3] += 1 # increase difficulty
    state[1] = new_lvl

    display.text(60,100, 'Score  ' + str(state[2]), medium_font)
    x = display.text(90,180, 'Press ', medium_font)
    display.draw_image('/keys/a.raw', x, 179, 15,15)
    display.text(x+15,180, ' continue', medium_font)

    if state[0]:
        display.text(95,40, 'LEVEL DONE', large_font)
        display.text(60,115, 'Lives  ' + str(state[4]), medium_font)
        display.text(60,130, 'Next level  ' + levels[new_lvl][0], medium_font)
        clock.tick()
        sound.play_song(win_music)
    else:
        display.text(100,40, 'GAME OVER', large_font)
        clock.tick()
        sound.play_song(end_music)

    while True:
        dt = clock.tick()
        sound.update(dt)
        input.get_inputs(dt)

        if input.a_pressed:
            break

    return state


# Execution starts here
display = Display()
clock = Clock()
sound = Sound()
input = Input()

# Game state
# [win=bool, level=int, score=int, difficulty=int, lives=int]
state = [False, 0, 0, 1, 3]
print(mem_free())
while True:
    if not state[0]:
        display.clear()
        state = menu(display, clock, sound, input, state)
        collect()
    print(mem_free())
    display.clear()
    state = Game(display, clock, sound, input, state).run()
    collect()
    print(mem_free())
    display.clear()
    state = transition(display, clock, sound, input, state)
    collect()
    print(mem_free())
    