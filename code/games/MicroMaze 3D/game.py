from pycogame import Display, Clock, Sound, Input
from math import sin, cos
#from sdcard import SDCard
#from machine import Pin, SPI
import micropython
#import os
from gc import collect
from maze import generate_maze

#try:
#    sd_spi = SPI(0, baudrate=500000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
#    sd = SDCard(sd_spi, Pin(17))
#   os.mount(sd, '/sd', readonly=True)
#except OSError as e:
#    print(e)

display = Display()
clock = Clock()
sound = Sound()
input = Input()
display.clear()
collect()

########################################################################  Assets
tile_w = 6
tile_h = 200
tiles = [Display.load_sprite('./tiles/0.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/1.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/2.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/3.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/4.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/5.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/6.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/7.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/8.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/9.raw', tile_w,tile_h),
         Display.load_sprite('./tiles/10.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/11.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/12.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/13.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/14.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/15.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/16.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/17.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/18.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/19.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/20.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/21.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/22.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/23.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/24.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/25.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/26.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/27.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/28.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/29.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/30.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/31.raw',tile_w,tile_h),
         Display.load_sprite('./tiles/32.raw',tile_w,tile_h)]

gem = [Display.load_sprite('./gem/0.raw',32,32),
       Display.load_sprite('./gem/1.raw',16,16),
       Display.load_sprite('./gem/2.raw',8,8),
       Display.load_sprite('./gem/3.raw',2,2)]
# Precalculate gem y position on screen
gem_y = (int(tile_h/2-gem[0][2]/2),
         int(tile_h/2-gem[1][2]/2),
         int(tile_h/2-gem[2][2]/2),
         int(tile_h/2-gem[3][2]/2))
collect()
################################################################################

@micropython.native
def raycast(ray_lenght, step, ray_step_size, map_pos, map_w, map_h, gem_pos, gem_scale, map_list):
    hit_wall = False
    distance_wall = 0
    while not hit_wall and distance_wall < depth:
        if ray_lenght[0] < ray_lenght[1]:
            map_pos[0] += step[0]
            distance_wall = ray_lenght[0]
            ray_lenght[0] += ray_step_size[0]
        else:
            map_pos[1] += step[1]
            distance_wall = ray_lenght[1]
            ray_lenght[1] += ray_step_size[1]

        if (map_pos[0] >= 0 and map_pos[0] < map_w and
            map_pos[1] >= 0 and map_pos[1] < map_h):
            # Ray is in bounds so test to see if the ray cell is a wall block
            if map_list[map_pos[1]][map_pos[0]] == '#':
                hit_wall = True
            if map_list[map_pos[1]][map_pos[0]] == 'g':
                if distance_wall < 7:
                    gem_scale = int(distance_wall/2)
                else:
                    gem_scale = 3
                gem_pos.append((n, gem_y[gem_scale]))

    if distance_wall > depth:
        distance_wall = depth

    return (hit_wall, gem_pos, gem_scale, distance_wall)

def sound_tick_delay(max_dist, map_gem, player_x, player_y):
    dist = map_gem[0] * map_gem[1] - player_x * player_y
    return int(dist / max_dist * 2000)

################################################################  Initialization
soundt = 0
menu = True
map_list = []
gem_scale = 0

screen_buffer = [ 32 for _ in range(53) ]
new_buffer = screen_buffer.copy()

fov = 1
view_width = 318
depth = 8
depth_step = depth / 32
v_ray = [0.0, 0.0]
map_pos = [0, 0]
ray_step_size = [0.0, 0.0]

while True:
    if menu:
        # Main menu
        del map_list
        collect()
        display.draw_image('./intro.raw', 0, 0, 320, 200)
        intro_music = sound.load_song('Duke:d=16,o=5,b=180:8c,8d#,8p,8f,4p,8c,8f,8p,8g,4p,8c,8g,8p,8g#,8p,8c,8g#,8f,8d#,4c,8p,4d#,8p,8g,8c,8p')
        while True:
            dt = clock.tick()
            input.get_inputs(dt)
            sound.update(dt)

            if not sound.song_playing():
                sound.play_song(intro_music)

            if input.a_pressed:
                map_cell_w = 7
                map_cell_h = 7
                break
            if input.b_pressed:
                map_cell_w = 15
                map_cell_h = 15
                break

        del intro_music
        display.draw_image('./loading.raw', 100, 78, 112, 34)
        collect()

        # Actual map size
        map_w = map_cell_w * 2 + 1
        map_h = map_cell_h * 2 + 1
        # Generate map
        map_list = generate_maze(map_cell_w, map_cell_h)
        # Add gem to map
        map_gem = (map_w-2, map_h-2)
        map_list[map_gem[0]][map_gem[1]] = 'g'
        gem_max_dist = map_gem[0] * map_gem[1] - 1
        # Init player location
        player_x, player_y, player_angle = (1.1, 1.1, 0.7851)
        menu = False
        collect()

    # Game loop
    dt = clock.tick()
    input.get_inputs(dt)
    sound.update(dt)

    # Controls
    if input.up_on:
        x = player_x + sin(player_angle) * 0.005 * dt
        y = player_y + cos(player_angle) * 0.005 * dt
        if map_list[int(y)][int(x)] != '#':
            player_x = x
            player_y = y
    if input.down_on:
        x = player_x - sin(player_angle) * 0.005 * dt
        y = player_y - cos(player_angle) * 0.005 * dt
        if map_list[int(y)][int(x)] != '#':
            player_x = x
            player_y = y
    if input.left_on:
        player_angle -= 0.002 * dt
    if input.right_on:
        player_angle += 0.002 * dt

    # Found gem
    if int(player_x) == map_w-2 and int(player_y) == map_h-2:
        menu = True

    gem_pos = []
    for n in range(0, view_width, tile_w):
        # For each column calculate the projected ray angle on to world space
        ray_angle = (player_angle - fov / 2) + (n / view_width * fov)
        distance_wall = 0
        hit_wall = False
        # Unit vector for ray in player space
        v_ray = [sin(ray_angle), cos(ray_angle)]

        # DDA raycaster - https://lodev.org/cgtutor/raycasting.html
        # https://www.youtube.com/watch?v=NbSee-XM7WA
        # https://www.youtube.com/watch?v=xW8skO7MFYw
        ray_step_size = (0 if v_ray[1] == 0 else ( 1 if v_ray[0] == 0 else abs(1 / v_ray[0])),
                         0 if v_ray[0] == 0 else ( 1 if v_ray[1] == 0 else abs(1 / v_ray[1])))
        map_pos = [int(player_x), int(player_y)]
        
        # Determine direction and initial ray lenght
        if v_ray[0] < 0:
            step = [-1]
            ray_lenght = [(player_x - map_pos[0]) * ray_step_size[0]]
        else:
            step = [1]
            ray_lenght = [(map_pos[0] + 1 - player_x) * ray_step_size[0]]
        if v_ray[1] < 0:
            step.append(-1)
            ray_lenght.append((player_y - map_pos[1]) * ray_step_size[1])
        else:
            step.append(1)
            ray_lenght.append((map_pos[1] + 1 - player_y) * ray_step_size[1])

        hit_wall, gem_pos, gem_scale, distance_wall = raycast(ray_lenght, step, ray_step_size, map_pos, map_w, map_h, gem_pos, gem_scale, map_list)
    
        # draw walls
        if hit_wall:
            new_buffer[int(n/tile_w)] = int(distance_wall/depth_step)
        else:
            new_buffer[int(n/tile_w)] = 32

    # Draw walls
    for c,t in enumerate(new_buffer):
        if t != screen_buffer[c]:
            try:
                display.draw_sprite(tiles[t], c * tile_w, 0)
            except IndexError:
                print(t, c)
                display.draw_sprite(tiles[t], c * tile_w, 0)
    
    # Draw gem
    if gem_pos != []:
        mid = int(len(gem_pos)/2)
        if gem_pos[mid][0] + gem[gem_scale][1] < view_width:
            display.draw_sprite(gem[gem_scale], gem_pos[mid][0], gem_pos[mid][1])

        # Mark walls where the gem was for redraw
        for wx in range(int(gem_pos[mid][0]/tile_w),
                        int((gem_pos[mid][0] + gem[gem_scale][1])/tile_w)+1,
                        1):
            if wx < len(new_buffer):
                new_buffer[wx] = -1

    screen_buffer = new_buffer.copy()

    # Make sound tick
    soundt += dt   
    if soundt > sound_tick_delay(gem_max_dist, map_gem, player_x, player_y):
        sound.play_effect([1,[(400,1)]])
        soundt = 0
