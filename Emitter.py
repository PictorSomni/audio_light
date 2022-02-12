import random
import time
import board
import displayio
import terminalio
import digitalio
from adafruit_debouncer import Debouncer
import neopixel
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor
# can try import bitmap_label below for alternative
from adafruit_display_text import label
import adafruit_displayio_sh1107

displayio.release_displays()

## BLE
ble = BLERadio()
advertisement = AdafruitColor()

# Set up button pins
# pin_a = digitalio.DigitalInOut(board.D9)
# pin_a.direction = digitalio.Direction.INPUT
# pin_a.pull = digitalio.Pull.UP

pin_b = digitalio.DigitalInOut(board.D6)
pin_b.direction = digitalio.Direction.INPUT
pin_b.pull = digitalio.Pull.UP

pin_c = digitalio.DigitalInOut(board.D5)
pin_c.direction = digitalio.Direction.INPUT
pin_c.pull = digitalio.Pull.UP

# button_a = Debouncer(pin_a) #9
button_b = Debouncer(pin_b) #6
button_c = Debouncer(pin_c) #5

## Neopixels
pixels = neopixel.NeoPixel(board.D9, 2, brightness=0.1)
pixels.fill((0, 0, 0))

## setup for LED to indicate BLE connection
blue_led = digitalio.DigitalInOut(board.BLUE_LED)
blue_led.direction = digitalio.Direction.OUTPUT

## Use for I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

## SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)

## Make the display context
group = displayio.Group()
display.show(group)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

text = "LE FUTUR"
text_area = label.Label(terminalio.FONT, text=text, scale=2, color=0xFFFFFF, x=21, y=30)
group.append(text_area)
time.sleep(1)

def send(broadcast_text, broadcast_color):
    text_area.text = broadcast_text
    text_area.scale = 2
    pixels.fill(0xFF00FF)
    advertisement.color = broadcast_color
    ble.stop_advertising()
    ble.start_advertising(advertisement)
    time.sleep(1)
    text_area.text = "LE FUTUR"

while True :
    ble.stop_advertising()
    
    button_b.update()
    button_c.update()

    pixels.fill(0x0077FF)

    if not pin_b.value and not pin_c.value :
        send("ORAGE", 0x001100)
        
    elif button_b.fell:
        send("PORTE", 0x110000)

    elif button_c.fell:
        send("WHAAAAAT", 0x000011)

    display.show(group)

