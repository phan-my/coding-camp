from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random
from math import sqrt

pin = Pin(19, Pin.OUT)
player = NeoPixel(pin, 64)
ai = NeoPixel(pin, 64)

pin_js_r = Pin(2, Pin.IN) #rechts
pin_js_l = Pin(7, Pin.IN) #links
pin_js_u = Pin(3, Pin.IN) #hoch
pin_js_d = Pin(6, Pin.IN) #runter
pin_js_c = Pin(8, Pin.IN) #mitte

color_r = 0x11 # Rot
color_g = 0x11 # Gruen
color_b = 0x11 # Blau

player_pos = 0
ai_pos = 32

player[player_pos] = (color_r, color_g, color_b)
player.write()

ai[ai_pos] = (0x11, 0, 0)
ai.write()

t = 100

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

while True:
    # ai movement

    go_r = distance(player_pos, right(ai, ai_pos))
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

    """r = random.randint(0, 3)
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
        ai_pos = down(ai, ai_pos)"""
    
    ai[ai_pos] = (0x11, 0, 0)
    ai.write()

    # player movement
    if pin_js_r.value() == 0:
        print("rechts")
        sleep_ms(t)
        player_pos = right(player, player_pos)
    elif pin_js_l.value() == 0:
        print("links")
        sleep_ms(t)
        player_pos = left(player, player_pos)
    elif pin_js_u.value() == 0:
        print("hoch")
        sleep_ms(t)
        player_pos = up(player, player_pos)
    elif pin_js_d.value() == 0:
        print("runter")
        sleep_ms(t)
        player_pos = down(player, player_pos)
    elif pin_js_c.value() == 0:
        sleep_ms(t)
        print("mitte")
        color_r = random.randint(0, 0x11)
        color_g = random.randint(0, 0x11)
        color_b = random.randint(0, 0x11)

    player[player_pos] = (color_r, color_g, color_b)
    player.write()

    if player_pos == ai_pos:
        print("yay")
        break
    sleep_ms(200)
