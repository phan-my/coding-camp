import uasyncio as asyncio
from BLECommunicator import BLECommunicator
from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random
from math import sqrt
PI = 3.1415926535897932384626433
import uasyncio as asyncio
import aioble
import bluetooth
from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms

START = -2
OK = -3
WAITING = -4



global direction_x, direction_y
r = random.randint(0, 1)
direction_x = 1
direction_y = r

t = 0

def process_list(data):
    if not data:
        return []
    return list(data)

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
        np[pos] = (0,0,0)
    elif direction_x == 0:
        print(pos)
        pos = left(np, pos)
        print(pos)
    
    # ball hits right edge
    if get_x(pos) == 7:
        pos = left(np, pos)
        direction_x = 0
    elif direction_x == 1:
        print("l")
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
    

    # ball hits floor
    if get_y(pos) == 0:
        pos = up(np, pos)
        direction_y = 1
    elif direction_y == 0:
        print("d")
        print(pos)
        pos = down(np, pos)

    # fixes weird glich
    if pos == 0:
        pos += up(np, pos)

    # ball hits paddle
    # paddle width 
    if abs(get_y(pos) - get_y(player_pos)) <= 2 and get_x(pos) == get_x(player_pos) + 1:
        direction_x = 1
        # points += 1
    
    return int(pos)


#From Template
ball_pos = START
direction_y = START
received_data = None  # Shared variable to hold received data
async def central_loop():
    global received_data
    global ball_pos, direction_x, direction_y
    ble = BLECommunicator(name="Pico2-adv", role="central")
    await ble.init()
    while True:
        #BLE RECEIVE/ SEND
        print("ball_pos ", ball_pos)

        # send waiting signal
        if ball_pos == WAITING or ball_pos == START:
            # await ble.send({"dir_y": WAITING, "pos_y": WAITING})
            data = await ble.receive()
            if data:
                received_data = data

        # send OK status
        if ball_pos >= 0:
            await ble.send({"dir_y": OK, "pos_y": OK})
            await asyncio.sleep(0.5)

        # ball hits left edge
        if get_x(ball_pos) == 0 and direction_x == 0:
            print("sending")
            if get_y(ball_pos) == 8:
                direction_y == 0
            elif get_y(ball_pos) == 0:
                direction_y == 1
            
            
            reply = {"pos_y": get_y(ball_pos), "dir_y": direction_y}
            await ble.send(reply)
            ball_pos = WAITING
            direction_y = WAITING
            # await asyncio.sleep(0.5)
        await asyncio.sleep(0.5)


async def data_watcher():

    #Definitions
    global received_data
    global ball, ball_pos
    global player, player_pos
    global direction_x, direction_y
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

    player_pos = 39

    player[player_pos] = (color_r, color_g, color_b)
    player.write()

    #MAIN LOOP
    while True:

        # player movement
        global angle
        if pin_js_u.value() == 0:
            sleep_ms(t)
            player_pos = up(player, player_pos)
        elif pin_js_d.value() == 0:
            sleep_ms(t)
            player_pos = down(player, player_pos)
        elif pin_js_c.value() == 0:
            sleep_ms(t)
            color_r = random.randint(0, 0x11)
            color_g = random.randint(0, 0x11)
            color_b = random.randint(0, 0x11)

        player[player_pos] = (color_r, color_g, color_b)
        player.write()

        # ball movement
        angle = random.randint(0, 1)
        if ball_pos >= 0:
            ball_pos = ball_movement(ball, int(ball_pos))
            ball_g = 0x33
            ball[ball_pos] = (0, ball_g, 0)
            ball.write()
        else:
            ball.fill((0,0,0))
            ball.write()

        if received_data:
            #BALL Position
            # data = received_data
            print("Received from peripheral:", received_data)
            if int(received_data["pos_y"]) != OK and int(received_data["pos_y"]) != WAITING:
                ball_pos = 8 * int(received_data["pos_y"])
                direction_x = 1
                direction_y = int(received_data["dir_y"])
            print('Position Ball ', ball_pos)
            #ball_pos = -1
            received_data = None  # Reset after handling
        else:
            print(".", end='')

        await asyncio.sleep(0.1)

        



async def main():
    await asyncio.gather(
        central_loop(),
        data_watcher()
    )

asyncio.run(main())