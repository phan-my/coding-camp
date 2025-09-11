from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
import random
from math import sqrt, sin
from utime import sleep_ms
from hashlib import sha256
import uasyncio as asyncio
from BLECommunicator import BLECommunicator
from zhaw_led_matrix import (
    LedMatrix,
    PixelColor,
    ColorTable
)
from movement import *

PI = 3.1415926535897932384626433

# GPIO pin for WS2812
pin_leds = 19

# LED count
LEDS = 64

#=============================================================
# List X Offset
# --> Moves list to the left edge outside of the LED Matrix
# --> Move list in x direction by given offset
#=============================================================
def list_offset_x(coords, offset, cols):
    # find the highest and lowest y coordinate value to determine width of pixel art
    highest_x = 0
    lowest_x = cols

    for coord in coords:
        if highest_x < coord[0]:
            highest_x = coord[0]
        if lowest_x > coord[0]:
            lowest_x = coord[0]

    width = highest_x-lowest_x+1

    i = -(highest_x+1)+ offset
    new_list = []
    for coord in coords:
        x,y = coord
        x = x+i
        if (x>=0) and (x<cols):
            new_list.append((x,y))
    return new_list

#=============================================================
# List Y Offset
# --> Moves list to the bottom edge inside the LED Matrix
# --> Move list in y direction by given offset
#=============================================================
def list_offset_y(coords, offset, rows):
    new_list = []
    for coord in coords:
        x,y = coord
        y = y+offset
        if (y>=0) and (y<rows):
            new_list.append((x,y))
    return new_list



# pieces
j_piece = [[3, 7], [4, 7], [5, 7], [5, 6]]
l_piece = [[3, 6], [3, 7], [4, 7], [5, 7]]
s_piece = [[3, 6], [4, 6], [4, 7], [5, 7]]
z_piece = [[3, 7], [4, 7], [4, 6], [5, 6]]
i_piece = [[2, 7], [3, 7], [4, 7], [5, 7]]
o_piece = [[3, 7], [4, 7], [3, 6], [4, 6]]
t_piece = [[3, 7], [4, 7], [5, 7], [4, 6]]

pieces = [j_piece, l_piece, s_piece, z_piece, i_piece, o_piece, t_piece]
pieces_color = [
    (0x00, 0x00, 0xff),
    (0xff, 0x80, 0x00),
    (0x00, 0x66, 0x00),
    (0xff, 0x00, 0x00),
    (0x00, 0xff, 0xff),
    (0xff, 0xff, 0x00),
    (0xff, 0x00, 0xff)
]

# Set brightness

pin = Pin(pin_leds, Pin.OUT)
current = NeoPixel(pin, LEDS)




if __name__ == '__main__':
    current[32-8] = (0x22, 0x22, 0x22)
    current.write()