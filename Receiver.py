# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import os
import digitalio
import board
from rainbowio import colorwheel
import neopixel
import audiopwmio
import audiocore
import random
import time
import sdcardio
import storage
import gc
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

#############################################################
#                          CONTENT                          #
#############################################################
## STATE
prev_state = None

## BLE
ble = BLERadio()
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)
advertisement = AdafruitColor()

## SD CARD
sd = sdcardio.SDCard(board.SPI(), board.D2)
vfs = storage.VfsFat(sd)
storage.mount(vfs, '/sd')
os.listdir('/sd')

## AUDIO
audio = audiopwmio.PWMAudioOut(board.A0)
audio_file = None

## NEOPIXELS
pixels = neopixel.NeoPixel(board.A2, 32, brightness=0.3)
off = (0, 0, 0)
pixels.fill(off)

enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

#############################################################
#                         FUNCTION                          #
#############################################################
def delay(wait):
    now = time.monotonic()
    while (time.monotonic() - now) < wait :
        pass


def play_file(filename, func):
    audio_path = "/sd/{}".format(filename)
    files = [file for file in os.listdir(audio_path)]
    global audio_file  # pylint: disable=global-statement

    if audio.playing:
        audio.stop()
    if audio_file:
        audio_file.close()

    file = random.choice(files)

    audio_file = open("{}/{}".format(audio_path, file), "rb")
    try:
        wav = audiocore.WaveFile(audio_file)
    except ValueError :
        print(f"ERROR --> {file}")
    else :
        audio.play(wav)
        while audio.playing:
            func()
        audio.stop()
        audio_file.close()
        gc.collect()


def thunder():
    times = random.randint(1, 4)
    color = random.randint(0, 255)
    wait = random.uniform(0.01, 0.2)
    while times > 0 :
        pixels.fill((color, color, color))
        delay(wait)
        pixels.fill(off)
        delay(wait)
        times -= 1
    delay(random.uniform(0.5, 20))


def rainbow():
    pixels.fill(colorwheel(int(time.monotonic() * 20) & 255))
    pixels.fill(off)


def nothing():
    pixels.fill(off)

#############################################################
#                          EFFECTS                          #
#############################################################
fx = {
    "0x000000":["bruits bizzares",  nothing],
    "0x000001":["degats",           thunder],
    "0x000002":["dragon",           nothing],
    "0x000003":["explosion",        thunder],
    "0x000004":["fantome",          nothing],
    "0x000005":["lich",             nothing],
    "0x000006":["orage",            thunder],
    "0x000007":["porte",            nothing],
    "0x000008":["rire",             nothing],
    "0x000009":["whaaaaat",         rainbow],
    "0x00000A":["",                 nothing],
    "0x00000B":["",                 nothing],
    "0x00000C":["",                 nothing],
    "0x00000D":["",                 nothing],
    "0x00000E":["",                 nothing],
    "0x00000F":["",                 nothing]
}

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    for entry in ble.start_scan(AdafruitColor, timeout=5):
        color = f"0x{entry.color:06x}"

        if color in fx.keys() :
            play_file(fx[color][0], fx[color][1])
            break
            
    ble.stop_scan()