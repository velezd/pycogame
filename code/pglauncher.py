from pycogame import Display, Clock, color565, XglcdFont, Fonts, Sound, Input
from machine import ADC, Pin, SPI
from sdcard import SDCard
import os
import sys


CLR_BLACK = color565(0,0,0)
CLR_WHITE = color565(255,255,255)
CLR_GRAY = color565(88,88,88)


class Battery():
    """ Battery indicator """
    def __init__(self, display):
        self.display = display
        self.sen_voltage = ADC(29)
        self.img_0 = Display.load_sprite('/bat/0.raw', 31, 15)
        self.img_25 = Display.load_sprite('/bat/25.raw', 31, 15)
        self.img_50 = Display.load_sprite('/bat/50.raw', 31, 15)
        self.img_75 = Display.load_sprite('/bat/75.raw', 31, 15)
        self.img_100 = Display.load_sprite('/bat/100.raw', 31, 15)
        self.timer = 1000

    def update(self, dt, x=285, y=4):
        self.timer += dt
        if self.timer > 1000:
            value = self.sen_voltage.read_u16()
            if value > 24000:   # > ~4.0V
                self.display.draw_sprite(self.img_100, x, y)
            elif value > 21000: # > ~3.6V
                self.display.draw_sprite(self.img_75, x, y)
            elif value > 18000: # > ~3.2V
                self.display.draw_sprite(self.img_50, x, y)
            elif value > 16000: # > ~3.0V
                self.display.draw_sprite(self.img_25, x, y)
            else:
                self.display.draw_sprite(self.img_0, x, y)
            self.timer = 0


class Menu():
    """ Main menu class """
    def __init__(self, display, font, path='/sd', x=0, y=23):
        self.x = x
        self.y = y
        self.path = path
        self.font = font
        self.display = display
        self.selected = 1
        self.page = 0
        self.selected_text = ''
        self.menu_items = []
        for f in os.ilistdir(path):
            # Check if file is dorectory and contains exec_file
            if f[1] == 0x4000:
                try:
                    os.stat('/'.join([self.path, f[0], 'game.py']))
                except OSError:
                    continue
                else:
                    self.menu_items.append(f[0])
        self.menu_len = len(self.menu_items)
        self.draw_background()
        self.show_items()

    def draw_background(self):
        self.display.fill_rect(0,24,320,192, CLR_BLACK)
        for ln in range(1,10):
            if ln == 1 or ln == 9:
                self.display.line(0,24*ln,319,24*ln, CLR_WHITE)
            else:
                self.display.line(0,24*ln,319,24*ln, CLR_GRAY)

    def show_items(self):
        first_item = self.page*8
        last_item = self.menu_len
        if first_item+8 < last_item:
            last_item = first_item+8

        counter = 1
        for item in self.menu_items[first_item:last_item]:
            if counter == self.selected:
                self.selected_text = item
                color = CLR_WHITE
            else:
                color = CLR_GRAY
            self.display.text(10,24*counter+6, item, self.font, color, CLR_BLACK)
            counter += 1

    def next_item(self):
        if self.selected == 8:
            return
        first_item = self.page*8
        try:
            new_item = self.menu_items[(first_item + self.selected)]
        except IndexError:
            return

        self.display.text(10,24*self.selected+6, self.selected_text,
                          self.font, CLR_GRAY, CLR_BLACK)
        self.selected += 1
        self.display.text(10,24*self.selected+6, new_item,
                          self.font, CLR_WHITE, CLR_BLACK)
        self.selected_text = new_item

    def prev_item(self):
        if self.selected == 1:
            return
        self.display.text(10,24*self.selected+6, self.selected_text,
                          self.font, CLR_GRAY, CLR_BLACK)
        self.selected -= 1
        first_item = self.page*8
        new_item = self.menu_items[(first_item + self.selected)-1]
        self.display.text(10,24*self.selected+6, new_item,
                          self.font, CLR_WHITE, CLR_BLACK)
        self.selected_text = new_item

    def next_page(self):
        if self.page+1 > self.menu_len/8:
            return
        self.page += 1
        self.selected = 1
        self.draw_background()
        self.show_items()

    def prev_page(self):
        if self.page-1 < 0:
            return
        self.page -= 1
        self.selected = 1
        self.draw_background()
        self.show_items()

    def select(self):
        if self.selected_text != '':
            path = '/'.join([self.path, self.selected_text])
            print('Starting: ', path)
            sys.path.append(path)
            os.chdir(path)
            return True
        return False

class PGLauncher():
    def __init__(self):
        self.display = Display()
        self.game_clock = Clock()
        self.sound = Sound()
        self.input = Input()
        self.small_font = XglcdFont(Fonts.small)
        self.medium_font = XglcdFont(Fonts.medium)

        # Show startup logo
        self.display.clear()
        self.display.draw_image('/logo.raw', 51, 97, 218, 19)
        self.sound.play_effect([0, [(80,50),(1400,150)]])
        self.game_clock.tick()
        delay=1000
        while delay > 0:
            dt = self.game_clock.tick()
            self.sound.update(dt)
            delay -= dt

        # Mount sd card
        try:
            sd_spi = SPI(0, baudrate=500000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
            sd = SDCard(sd_spi, Pin(17))
            os.mount(sd, '/sd', readonly=True)
        except OSError as e:
            print(e)
            self.display.text(115, 140, 'NO SD CARD', self.medium_font)
            sys.exit()

        # Start menu
        self.display.clear()
        self.battery = Battery(self.display)
        self.menu = Menu(self.display, self.medium_font)
        self.draw_help()

    def loop(self):
        # Main loop
        while True:
            dt = self.game_clock.tick()
            self.sound.update(dt)
            self.input.get_inputs(dt)
            self.battery.update(dt)

            if self.input.down_pressed:
                if self.input.menu_on:
                    self.sound.off()
                else:
                    self.menu.next_item()
                self.play_btn_sound()
            if self.input.up_pressed:
                if self.input.menu_on:
                    self.sound.on()
                else:
                    self.menu.prev_item()
                self.play_btn_sound()
            if self.input.left_pressed:
                self.menu.prev_page()
                self.play_btn_sound()
            if self.input.right_pressed:
                self.menu.next_page()
                self.play_btn_sound()
            if self.input.a_pressed:
                if self.menu.select():
                    break

    def play_btn_sound(self):
        self.sound.play_effect([20, [(200,10)]])

    def draw_help(self, y=221):
        """ Draws help bar at the bottom of the screen """
        up = '/keys/up.raw'
        down = '/keys/down.raw'
        left = '/keys/left.raw'
        right = '/keys/right.raw'
        a = '/keys/a.raw'
        b = '/keys/b.raw'
        menu = '/keys/menu.raw'
        plus = '/keys/plus.raw'

        self.display.draw_image(up, 5,y, 15,15)
        self.display.draw_image(down, 22,y, 15,15)
        x = self.display.text(41,y+4, 'Game', self.small_font, CLR_WHITE, CLR_BLACK)
        self.display.draw_image(left, x+9,y, 15,15)
        self.display.draw_image(right, x+26,y, 15,15)
        x = self.display.text(x+45,y+4, 'Page', self.small_font, CLR_WHITE, CLR_BLACK)
        self.display.draw_image(a, x+9,y, 15,15)
        x = self.display.text(x+28,y+4, 'Play', self.small_font, CLR_WHITE, CLR_BLACK)
        self.display.draw_image(menu, x+9,y, 30,15)
        self.display.draw_image(plus, x+40,y, 7,15)
        self.display.draw_image(up, x+48,y, 15,15)
        self.display.draw_image(down, x+65,y, 15,15)
        self.display.text(x+84,y+4, 'Sound', self.small_font, CLR_WHITE, CLR_BLACK)
