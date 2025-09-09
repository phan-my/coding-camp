from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random

pin = Pin(19, Pin.OUT)
np = NeoPixel(pin, 64)

pin_js_r = Pin(2, Pin.IN)
pin_js_l = Pin(7, Pin.IN)
pin_js_c = Pin(8, Pin.IN)

color_r = 0x11
color_g = 0x11
color_b = 0x11

paddle_center = 4
paddle_length = 2
ball_pos = 44
ball_speed = 130    #slow = 150 ms pause

def draw_paddle(pos):
    for i in range(64):
        np[i] = (0, 0, 0)
    half = paddle_length // 2
    if paddle_length % 2 == 0:
        start = max(0, pos - (half - 1))
        end = min(7, pos + half)
    else:
        start = max(0, pos - half)
        end = min(7, pos + half)
    for x in range(start, end + 1):
        np[x] = (color_r, color_g, color_b)
    np.write()

def draw_ball(pos):
    np[pos] = (0x11, 0, 0)
    np.write()

def clear_ball(pos):
    np[pos] = (0,0,0)

def get_x(pos):
    return pos % 8

def get_y(pos):
    return pos // 8

def right(pos):
    if get_x(pos) == 7:
        return pos
    return pos + 1

def left(pos):
    if get_x(pos) == 0:
        return pos
    return pos - 1

def up(pos):
    if get_y(pos) == 7:
        return pos
    return pos + 8

def down(pos):
    if get_y(pos) == 0:
        return pos
    return pos - 8

direction_x = random.randint(0,1)
direction_y = 1

draw_paddle(paddle_center)
draw_ball(ball_pos)

t = 10

while True:
    '''
    if random.randint(0, 1) == 1:
        ball_speed -= 1    #acceleration -ms pause 50% chance fuer 1ms schneller
        '''
    sleep_ms(ball_speed)
    clear_ball(ball_pos)

    # new ball pos
    if direction_x == 0:
        if get_x(ball_pos) == 0:
            direction_x = 1
            ball_pos = right(ball_pos)
        else:
            ball_pos = left(ball_pos)
    else:
        if get_x(ball_pos) == 7:
            direction_x = 0
            ball_pos = left(ball_pos)
        else:
            ball_pos = right(ball_pos)

    # is player beneath ball
    if direction_y == 0:  # ball goes down
        if get_y(ball_pos) == 1: 
            half = paddle_length // 2
            paddle_positions = list(range(paddle_center - half, paddle_center + half + 1))
            if get_x(ball_pos) in paddle_positions:
                direction_y = 1  # ricochet
                # direction adaption
                if random.randint(1, 4) == 1: #25% chance fuer random abprall
                    direction_x = random.randint(0,1)
                else:
                    if get_x(ball_pos) == paddle_positions[0]:
                        direction_x = 0
                    elif get_x(ball_pos) == paddle_positions[-1]:
                        direction_x = 1
            else:
               # game over - red screen
                for i in range(64):
                    np[i] = (30, 0, 0)
                np.write()
                sleep_ms(2000)
                for i in range(64):
                    np[i] = (0, 0, 0)
                np.write()
                break
        else:
            ball_pos = down(ball_pos)
    else:
        # Ball up 
        if get_y(ball_pos) == 7:
            direction_y = 0
            ball_pos = down(ball_pos)
        else:
            ball_pos = up(ball_pos)

    draw_ball(ball_pos)

    # User control
    if pin_js_r.value() == 0 and paddle_center < 7 - paddle_length // 2:
        paddle_center += 1
        draw_paddle(paddle_center)
        sleep_ms(t)
    elif pin_js_l.value() == 0 and paddle_center > paddle_length // 2:
        paddle_center -= 1
        draw_paddle(paddle_center)
        sleep_ms(t)
    elif pin_js_c.value() == 0:
        color_r = random.randint(0, 0x11)
        color_g = random.randint(0, 0x11)
        color_b = random.randint(0, 0x11)
        draw_paddle(paddle_center)
        sleep_ms(t)
