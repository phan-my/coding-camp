from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random
from math import sqrt, sin
from utime import sleep_ms
from hashlib import sha256
import uasyncio as asyncio
from BLECommunicator import BLECommunicator
from zhaw_led_matrix import LedMatrix

PI = 3.1415926535897932384626433
START       = -2
OK          = -3
WAITING     = -4
GAME_OVER   = -16


lm = LedMatrix(8, 8)
winscreen = "/gg.bmp"


""" game mechanics """
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

player_pos = 32
ball_pos = 15 + 8*random.randint(0, 5)

player[player_pos] = (color_r, color_g, color_b)
player.write()

start = True

global direction_x, direction_y
r = random.randint(0, 1)
direction_x = 0
direction_y = r

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
    global direction_x, direction_y, player_pos, angle
    angle = random.randint(0, 1)

    # ball hits left edge
    if get_x(pos) == 0:
        np[pos] = (0x22, 0, 0)
    elif direction_x == 0:
        pos = left(np, pos)
    
    # ball hits right edge
    if get_x(pos) == 7 and direction_x == 1:
        np[pos] = (0,0,0)
    elif direction_x == 1:
        pos = right(np, pos)
    
    # ball hits ceil
    if get_y(pos) == 7:
        pos = down(np, pos)
        # add random bounce
        if 2 < get_x(pos) and get_x(pos) < 7:
            pos -= 8 * angle
        direction_y = 0
    elif direction_y == 1:
        pos = up(np, pos)

    # ball hits floor
    if get_y(pos) == 0:
        pos = up(np, pos)
        # add random bounce
        if 2 < get_x(pos) and get_x(pos) < 7:
            pos += 8 * angle
        direction_y = 1
    elif direction_y == 0:
        pos = down(np, pos)

    # ball hits paddle
    # paddle width 
    if abs(get_y(pos) - get_y(player_pos)) <= 1 and get_x(pos) == get_x(player_pos) + 1:
        direction_x = 1
        pos += angle
    
    return int(pos)

# player movement
def player_movement(np, pos):
    # player movement
    if pin_js_u.value() == 0:
        if pos // 8 == 7:
            return pos
        np[pos] = (0,0,0)
        pos += 8
        return pos
    elif pin_js_d.value() == 0:
        if pos // 8 == 0:
            return pos
        np[pos] = (0,0,0)
        pos -= 8
        return pos

    return int(pos)

""" communications """
received_data = None # Shared variable to hold received data

async def peripheral_loop():
    global received_data
    global ball_pos, direction_x, direction_y
    ble = BLECommunicator(name="Pico2-adv", role="peripheral")
    await ble.init()
    count = 0
    while True:
        # Receive messages from central
        if ball_pos < 0:
            # await ble.send({"pos_y": int(get_y(ball_pos)), "dir_y": int(direction_y)})
            data = await ble.receive()
            if data:
                print("Received from central:", data)
                received_data = data  # Store received data

        """ send to opponent """
        if ball_pos >= 0:
            reply = {"pos_y": OK, "dir_y": OK}
            await ble.send(reply)
            reply = None

        # Periodically send a reply only if central is connected
        # send ball
        if get_x(ball_pos) == 7 and ball_pos >= 0 and direction_x == 1:
            # print("sending")
            if get_y(ball_pos) == 8:
                direction_y = 0
            elif get_y(ball_pos) == 0:
                direction_y = 1

            reply = {"pos_y": int(get_y(ball_pos)), "dir_y": int(direction_y)}
            await ble.send(reply)
            ball_pos = WAITING
            direction_x = WAITING
            reply = None
        # send status
        if get_x(ball_pos) == 0:
            await ble.send({"pos_y": GAME_OVER, "dir_y": GAME_OVER})
            print("GG")
        
        # reset game
        if pin_js_c.value() == 0 and get_x(ball_pos) == 0:
            await ble.send({"pos_y": START, "dir_y": START})


        """
        if ball_pos < 0:
            await ble.send({"pos_y": ball_pos, "dir_y": direction_y})
        """

        count += 1
        await asyncio.sleep(0.5)

async def data_watcher():
    global received_data
    global player, player_pos
    global ball, ball_pos
    global direction_x, direction_y
    color_r = 0x22
    color_g = 0x22
    color_b = 0x22
    pause = True
    dead = False

    ball[ball_pos] = (0, 0x33, 0)
    ball.write()

    t = 0

    player[player_pos] = (color_r, color_g, color_b)
    player.write()
    while True:
        # player movement
        player.write()
        if pin_js_c.value() == 0:
            pause = False
            color_r = random.randint(0x33, 0x66)
            color_g = random.randint(0x33, 0x66)
            color_b = random.randint(0x33, 0x66)
            ball.fill((0,0,0))
            ball.write()
        if pin_js_u.value() == 0 or pin_js_d.value() == 0:
            player_pos = player_movement(player, int(player_pos))
            player[player_pos] = (color_r, color_g, color_b)
            player.write()
        player.write()
        
        # restart game
        if pin_js_c.value() == 0 and dead == True:
            color_r = 0x22
            color_g = 0x22
            color_b = 0x22
            pause = True
            dead = False

            player_pos = 32
            ball_pos = 15 + 8*random.randint(0, 5)

            player[player_pos] = (color_r, color_g, color_b)
            player.write()

            start = True

            r = random.randint(0, 1)
            direction_x = 0
            direction_y = r

            ball[ball_pos] = (0, 0x33, 0)
            ball.write()

        # ball movement
        if ball_pos >= 0 and not pause and not dead and not (get_x(ball_pos) == 7 and direction_x == 1):
            # print("ball pos", ball_pos)
            ball_pos = ball_movement(ball, int(ball_pos))
            ball[ball_pos] = (0, 0x33, 0)
            ball.write()
            #player.write()
        if get_x(ball_pos) == 7 and direction_x == 1:
            ball[ball_pos] = (0, 0, 0)
            ball.write()
            #player.write()
        
        # death
        if get_x(ball_pos) == 0:
            dead = True
            ball[ball_pos] = (0x66, 0, 0)
            ball.write()

        # get and process data
        if received_data:
            """ Do something with the received data """
            # print("Processing received data:", received_data)
            if int(received_data["pos_y"]) >= 0 and int(received_data["pos_y"]) >= 0:
                ball_pos = 8 * int(received_data["pos_y"]) + 7
                direction_x = 0
                direction_y = int(received_data["dir_y"])
                t += 0.01
                await asyncio.sleep(0.01)
            if int(received_data["pos_y"]) == GAME_OVER and int(received_data["dir_y"]) == GAME_OVER:
                lm.draw_bitmap(winscreen)
                lm.set_brightness(20)
                lm.apply()
                print("gg ez")
            received_data = None  # Reset after processing
        await asyncio.sleep(0.15 - t)

async def main():
    await asyncio.gather(
        peripheral_loop(),
        data_watcher()
    )

asyncio.run(main())
