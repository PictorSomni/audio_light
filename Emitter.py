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

switch = digitalio.DigitalInOut(board.D11)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

## I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
trellis = Trellis(i2c)

# Make the display context
group = displayio.Group()
display.show(group)

color_bitmap = displayio.Bitmap(128, 32, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

text = "LE FUTUR"
text_area = label.Label(terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=21, y=15)
group.append(text_area)

print("Turning on each LED, one at a time...")
for i in range(16):
    trellis.led[i] = True
    time.sleep(0.05)
time.sleep(0.5)
trellis.led.fill(False)

## A BIT OF WAIT
time.sleep(0.5)

switch_state = None
last_position = encoder.position
pressed_buttons = set()

#############################################################
#                         FUNCTION                          #
#############################################################
def send(broadcast_text, broadcast_color):
    text_area.text = broadcast_text
    text_area.scale = 2
    # pixels.fill(0xFFFFFF)
    advertisement.color = broadcast_color
    ble.stop_advertising()
    ble.start_advertising(advertisement)
    time.sleep(1)
    text_area.text = "LE FUTUR"

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    display.show(group)
    ble.stop_advertising()
    time.sleep(0.1)
    
    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        for _ in range(position_change):
            print("+1")
        text_area.text = f"{current_position}"
    elif position_change < 0:
        for _ in range(-position_change):
            print("-1")
        text_area.text = f"{current_position}"
    last_position = current_position
    if not switch.value and switch_state is None:
        switch_state = "pressed"
    if switch.value and switch_state == "pressed":
       text_area.text = "PRESSED"
       switch_state = None

    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        print("pressed:", b)
        trellis.led[b] = True
        if b == 0:
            send("ORAGE", 0x001100)

        if b == 1:
            send("PORTE", 0x110000)

        if b == 2:
            send("WHAAAAAT", 0x000011)

    pressed_buttons.update(just_pressed)
    for b in released:
        print("released:", b)
        # text_area.text = b
        trellis.led[b] = False

