import adafruit_displayio_sh1107
import board
import digitalio
import displayio
import neopixel
import terminalio
import time
from adafruit_display_text import label
from adafruit_led_animation.color import RED
from adafruit_led_animation.color import AMBER
from adafruit_led_animation.color import GREEN
from i2cdisplaybus import I2CDisplayBus

# this firmware assumes you have a means of connecting
# a high voltage relay to GPIO pins in full isolation of
# the low voltage microcontroller.
#
# don't mess around with high voltage unless you know
# what you are doing.
#
# you can simulate a high voltage traffic signal with
# low voltage LEDs correctly wired to the GPIO pins
RED_PIN = board.D12
RED_TIME = 35
AMBER_PIN = board.D11
AMBER_TIME = 3
GREEN_PIN = board.D10
GREEN_TIME = 30

DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_BORDER = 2


class TrafficSignal:
    def __init__(self):
        self.setup_oled()

        # the phases are cycled through with the onboard
        # RGB neopixel if you have no GPIO pins wired up
        self.pixels = neopixel.NeoPixel(
            board.NEOPIXEL, 1, brightness=0.1, auto_write=True, bpp=3
        )

        self.red_light = digitalio.DigitalInOut(RED_PIN)
        self.red_light.direction = digitalio.Direction.OUTPUT

        self.amber_light = digitalio.DigitalInOut(AMBER_PIN)
        self.amber_light.direction = digitalio.Direction.OUTPUT

        self.green_light = digitalio.DigitalInOut(GREEN_PIN)
        self.green_light.direction = digitalio.Direction.OUTPUT

        # we are using this just as an indicator for the
        # firmware operating correctly when the phases are
        # running
        self.power_light = digitalio.DigitalInOut(board.LED)
        self.power_light.direction = digitalio.Direction.OUTPUT

    def setup_oled(self):
        displayio.release_displays()
        i2c = board.I2C()
        display_bus = I2CDisplayBus(i2c, device_address=0x3C)

        display = adafruit_displayio_sh1107.SH1107(
            display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT
        )
        self.screen = displayio.Group()
        display.root_group = self.screen

    def set_text(self, text):
        character_width = 6
        scale = 6
        text_width = len(text) * character_width * scale

        x_position = (DISPLAY_WIDTH // 2) - (text_width // 2)
        # ensure the position is not negative
        if x_position < DISPLAY_BORDER:
            x_position = DISPLAY_BORDER

        y_position = DISPLAY_HEIGHT // 2

        if len(self.screen) > 0:
            self.screen.pop()

        text_area = label.Label(
            terminalio.FONT,
            text=text,
            scale=scale,
            color=0xFFFFFF,
            x=x_position,
            y=y_position,
        )
        self.screen.append(text_area)

    def all_lights_off(self):
        print("ALL OFF")
        self.red_light.value = False
        self.amber_light.value = False
        self.green_light.value = False

    def red_light_on(self):
        self.red_light.value = True
        self.set_text("R")

    def amber_light_on(self):
        self.amber_light.value = True
        self.set_text("Y")

    def green_light_on(self):
        self.green_light.value = True
        self.set_text("G")

    def run_phase(self, name, color, sleep_time, on_fn):
        self.pixels[0] = color
        self.all_lights_off()
        print(f"{name} ON")
        on_fn()
        time.sleep(sleep_time)

    def run_startup(self):
        self.pixels[0] = RED
        self.all_lights_off()
        self.red_light_on()

        for i in range(10, 0, -1):
            self.set_text(str(i))
            time.sleep(1)

    def run_phases(self):
        print("\n---")
        print("STARTING PHASE LOOP")
        print("---\n")

        self.power_light.value = True

        while True:
            self.run_phase("GREEN", GREEN, GREEN_TIME, self.green_light_on)
            self.run_phase("AMBER", AMBER, AMBER_TIME, self.amber_light_on)
            self.run_phase("RED", RED, RED_TIME, self.red_light_on)


traffic_signal = TrafficSignal()
traffic_signal.run_startup()
traffic_signal.run_phases()
