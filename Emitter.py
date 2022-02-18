# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import board
import digitalio
import rotaryio
import displayio
import terminalio
import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from adafruit_trellis import Trellis
from adafruit_debouncer import Debouncer

#############################################################
#                          CONTENT                          #
#############################################################
## CLEARS DISPLAY
displayio.release_displays()

## BLE
ble = BLERadio()
advertisement = AdafruitColor()

## ENCODER
encoder = rotaryio.IncrementalEncoder(board.D10, board.D12)
switch_pin = digitalio.DigitalInOut(board.D11)
switch_pin.direction = digitalio.Direction.INPUT
switch_pin.pull = digitalio.Pull.UP
switch = Debouncer(switch_pin)

## I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
trellis = Trellis(i2c)

# DISPLAY CONTEXT
group = displayio.Group()
display.show(group)

color_bitmap = displayio.Bitmap(128, 32, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

text = "LE FUTUR"
text_area = label.Label(terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=13, y=15)
group.append(text_area)

## MENU
menu = [["BRUITS",      0x000000],
        ["DEGATS",      0x000001],
        ["DRAGON",      0x000002],
        ["EXPLOSION",   0x000003],
        ["FANTOME",     0x000004],
        ["LICHE",       0x000005],
        ["ORAGE",       0x000006],
        ["PORTE",       0x000007],
        ["RIRE",        0x000008],
        ["WTF",         0x000009],
        ["VIDE",        0x00000A],
        ["VIDE",        0x00000B],
        ["VIDE",        0x00000C],
        ["VIDE",        0x00000D],
        ["VIDE",        0x00000E],
        ["VIDE",        0x00000F]
]

## START ANIMATION
for i in range(16):
    trellis.led[i] = True
    time.sleep(0.05)

for i in range(16):
    trellis.led[i] = False
    time.sleep(0.05)

## A BIT OF WAIT
time.sleep(0.5)

## STATE OF THE ART
last_position = encoder.position
pressed_buttons = set()

#############################################################
#                         FUNCTION                          #
#############################################################
def choice(broadcast_text, broadcast_color):
    text_area.text = broadcast_text
    text_area.scale = 2
    advertisement.color = broadcast_color


def send():
    text_area.text = "BROADCAST"
    ble.start_advertising(advertisement)
    time.sleep(1)
    text_area.text = "MENU"

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    display.show(group)
    ble.stop_advertising()
    time.sleep(0.1)

    switch.update()
    current_position = encoder.position
    position_change = current_position - last_position

    '''
        If i don't need the following code to make it works, i don't need the following code. :D
    '''
    # if position_change > 0:
    #     for _ in range(position_change):
    #         print("+1")
    #     text_area.text = f"{current_position}"

    # elif position_change < 0:
    #     for _ in range(-position_change):
    #         print("-1")
    #     text_area.text = f"{current_position}"

    if switch.fell:
        send()

    just_pressed, released = trellis.read_buttons()

    for b in just_pressed:
        trellis.led.fill(False)
        trellis.led[b] = True
        choice(menu[b][0], menu[b][1])

    pressed_buttons.update(just_pressed)
    last_position = current_position

