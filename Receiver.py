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

## SD card
sd = sdcardio.SDCard(board.SPI(), board.D2)
vfs = storage.VfsFat(sd)
storage.mount(vfs, '/sd')
os.listdir('/sd')

## Audio output
audio = audiopwmio.PWMAudioOut(board.A0)
audio_file = None

## Neopixel
pixel = neopixel.NeoPixel(board.A2, 32, brightness=0.3)
off = (0, 0, 0)
pixel.fill(off)

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
        pixel.fill((color, color, color))
        delay(wait)
        pixel.fill((0, 0, 0))
        delay(wait)
        times -= 1
    delay(random.uniform(0.5, 20))


def rainbow():
    for i in range(255):
        pixel.fill((colorwheel(i)))
    pixel.fill((0, 0, 0))


def nothing():
    pixel.fill((0, 0, 0))


#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    for entry in ble.start_scan(AdafruitColor, timeout=5):
        print(f"#{entry.color:06x}\n")
        # pixel.fill(entry.color)

        if entry.color == 0x110000 :
            play_file("porte", nothing)
            break
        
        elif entry.color == 0x000011 :
            play_file("whaaaaat", rainbow)
            break
        
        elif entry.color == 0x001100 :
            play_file("orage", thunder)
            break

    ble.stop_scan()