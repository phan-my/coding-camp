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

SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_TX_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")  # peripheral -> central
CHAR_RX_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef2")  # central -> peripheral

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
ball_pos = -1

player[player_pos] = (color_r, color_g, color_b)
player.write()


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
    if direction_x == 0:
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

    # ball hits paddle
    # paddle width 
    if abs(get_y(pos) - get_y(player_pos)) <= 2 and get_x(pos) == get_x(player_pos) + 1:
        direction_x = 1
        points += 1
    
    return int(pos)

async def peripheral_task(pos_y, direction_x, direction_y):
    count = 0
    while True:
        print("Advertising...")
        conn = await aioble.advertise(
            500_000,
            name="Right",
            services=[SERVICE_UUID],
        )
        print("Connected to", conn.device)

        try:
            while conn.is_connected():
                """
                    STANDARD:
                    [y position for opponent, x direction, y direction]
                """
                indices = [pos_y, direction_x, direction_y]
                
                tx_message = bytes(indices)  # peripheral -> central
                try:
                    char_tx.write(tx_message)
                except Exception as e:
                    print("char_tx write failed:", e)
                try:
                    char_tx.notify(conn, tx_message)
                except Exception:
                    pass
                print("Sent indices:", indices)

                count = (count + 1) & 0x7FFF

                try:
                    source_conn, data = await char_rx.written() # source_conn lets you know the origin of the message
                except Exception as e:
                    print("char_rx read error:", e)
                    await asyncio.sleep(0.5)
                    continue

                # process incoming payload from central
                """
                rec_indices = process_list(data)
                pr(nprint("Received from central:", rec_indices)
                ball.fill((0, 0, 0))
                for idx in rec_indices:
                    if 0 <= idx < len(ball):
                        ball[idx] = (100, 100, 100)
                ball.write()
                await asyncio.sleep(0.5)
                """
        except Exception as e:
            print("Connection lost:", e)

points = 0

async def central_task():
    global indices
    print("Scanning for devices...")
    device = None
    async with aioble.scan(duration_ms=50000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print("Found:", result.name(), result.device)
            if "Left" == result.name():
                device = result.device
                break

    if not device:
        print("No PicoAdvertiser found")
        return

    print("Connecting...")
    connection = await device.connect(timeout_ms=2000)
    print("Connected!")

    service = await connection.service(SERVICE_UUID)
    char_tx = await service.characteristic(CHAR_TX_UUID)  # read notifications / reads from peripheral
    char_rx = await service.characteristic(CHAR_RX_UUID)  # write to peripheral


    while connection.is_connected():
        # read data
        data = await char_tx.read()
        indices = process_list(data)

        # empty data
        if not indices:
            print("Received empty payload, skipping:", data)
            await asyncio.sleep(0.5)
            return 0

        # process data
        try:
            print("Received indices:", indices)
            return indices
        except Exception as e:
            print("Error processing payload:", e, "raw:", data)

while True:
    global direction_x, direction_y
    global angle
    # player movement
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


    """if ball_pos >= 64:
        while 1:
            print()"""
    # game over
    """
    if get_y(ball_pos) <= get_y(player_pos):
        print("booo")
        print("points", points)
        ball[ball_pos] = (0x33, 0, 0)
        """
    if ball_pos > 0:
        print("ball pos", ball_pos)
        ball_pos = ball_movement(ball, int(ball_pos))
        ball_g = 0x33
        ball[ball_pos] = (0, ball_g, 0)
    else:
        ball.fill((0,0,0))

    ball.write()
    sleep_ms(100)

    # receive ball from opponent
    if ball_pos == -1:
        global indices
        asyncio.run(central_task())
        print(indices)
        ball_pos = 8 * indices[0]
        direction_y = indices[2]

    # send ball to opponent
    if get_x(ball_pos) == 0 and direction_x == 0:
        if get_y(ball_pos) == 8:
            direction_y = 0
        elif get_y(ball_pos) == 0:
            direction_y = 1

        # wait until signal
        asyncio.run(peripheral_task(get_y(ball_pos) + (direction_y * 2 - 1), direction_x, direction_y))
        ball_pos = -1



