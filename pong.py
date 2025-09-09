from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random
from math import sqrt, sin
PI = 3.1415926535897932384626433

pin = Pin(19, Pin.OUT)
player = NeoPixel(pin, 64)
ball = NeoPixel(pin, 64)

pin_js_r = Pin(2, Pin.IN) #rechts
pin_js_l = Pin(7, Pin.IN) #links
pin_js_u = Pin(3, Pin.IN) #hoch
pin_js_d = Pin(6, Pin.IN) #runter
pin_js_c = Pin(8, Pin.IN) #mitte

color_r = 0x11 # Rot
color_g = 0x11 # Gruen
color_b = 0x11 # Blau

player_pos = 4
ball_pos = 33 + random.randint(0, 5)

player[player_pos] = (color_r, color_g, color_b)
player.write()


global direction_x, direction_y
r = random.randint(0, 1)
direction_x = r
direction_y = 1

t = 0

def right(np, pos):
    if pos % 8 == 7:
        return pos
    np[pos] = (0,0,0)
    pos += 1
    return pos

def left(np, pos):
    if pos % 8 == 0:
        return pos
    np[pos] = (0,0,0)
    pos -= 1
    return pos

def up(np, pos):
    if pos // 8 == 7:
        return pos
    np[pos] = (0,0,0)
    pos += 8
    return pos

def down(np, pos):
    if pos // 8 == 0:
        return pos
    np[pos] = (0,0,0)
    pos -= 8
    return pos

def get_x(pos):
    return pos % 8

def get_y(pos):
    return pos // 8

def dy(pos_a, pos_b):
    return abs(get_y(pos_a) - get_y(pos_b))

def dx(pos_a, pos_b):
    return abs(get_x(pos_a) - get_x(pos_b))

def distance(a_pos, b_pos):
    return sqrt(dx(a_pos, b_pos)**2 + dy(a_pos, b_pos)**2)

def ball_movement(np, pos):
    global direction_x, direction_y, player_pos, points, angle

    # ball hits left edge
    if get_x(pos) == 0:
        pos = right(np, pos) + angle
        direction_x = 1
    elif direction_x == 0:
        print("l")
        print(pos)
        pos = left(np, pos)
        print(pos)
    
    # ball hits right edge
    if get_x(pos) == 7:
        pos = left(np, pos) + angle
        direction_x = 0
    elif direction_x == 1:
        print("r")
        print(pos)
        pos = right(np, pos)
        print(pos)
    
    # ball hits ceil
    if get_y(pos) == 7:
        pos = down(np, pos)
        direction_y = 0
    elif direction_y == 1:
        print("u")
        print(pos)
        pos = up(np, pos)
        print(pos)
    
    # move down
    if direction_y == 0:
        pos = down(np, pos)
    
    # ball hits paddle
    # paddle width 
    if abs(get_x(pos) - get_x(player_pos)) <= 2 and get_y(pos) == get_y(player_pos) + 1:
        direction_y = 1
        points += 1
    
    sleep_ms(20)
    return int(pos)

points = 0
while True:
    # ball movement
    global direction_x, direction_y
    global angle

    angle = random.randint(0, 1)

    """if ball_pos >= 64:
        while 1:
            print()"""
    # game over
    if get_y(ball_pos) <= get_y(player_pos):
        print("booo")
        print("points", points)
        ball[ball_pos] = (0x33, 0, 0)
    else:
        ball[ball_pos] = (0, 0x33, 0)
        sleep_ms(100)

    ball.write()


    # (x, y)

    ball_pos = ball_movement(ball, int(ball_pos))

    """go_r = distance(player_pos, right(ai, ai_pos))
    go_l = distance(player_pos, left(ai, ai_pos))
    go_u = distance(player_pos, up(ai, ai_pos))
    go_d = distance(player_pos, down(ai, ai_pos))

    best_move = max(go_r, go_l, go_u, go_d)

    if go_r == best_move:
        sleep_ms(t*2)
        ai_pos = right(ai, ai_pos)
    elif go_l == best_move:
        sleep_ms(t*2)
        ai_pos = left(ai, ai_pos)
    elif go_u == best_move:
        sleep_ms(t*2)
        ai_pos = up(ai, ai_pos)
    else:
        sleep_ms(t*2)
        ai_pos = down(ai, ai_pos)

    r = random.randint(0, 3)
    if r == 0:
        # right
    if r == 1:
        # left
        ai_pos = left(ai, ai_pos)
    if r == 2:
        # up
        ai_pos = up(ai, ai_pos)
    if r == 3:
        # down
        ai_pos = down(ai, ai_pos)
    """
    

    # player movement
    if pin_js_r.value() == 0:
        print("rechts")
        sleep_ms(t)
        player_pos = right(player, player_pos)
    elif pin_js_l.value() == 0:
        print("links")
        sleep_ms(t)
        player_pos = left(player, player_pos)
    elif pin_js_c.value() == 0:
        sleep_ms(t)
        print("mitte")
        color_r = random.randint(0, 0x11)
        color_g = random.randint(0, 0x11)
        color_b = random.randint(0, 0x11)

    player[player_pos] = (color_r, color_g, color_b)
    player.write()

