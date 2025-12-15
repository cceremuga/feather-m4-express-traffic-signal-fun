import adafruit_displayio_sh1107
import adafruit_lidarlite
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
from adafruit_led_animation.color import WHITE
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
RED_TIME = 33
RED_THRESHOLD = 20
AMBER_PIN = board.D11
AMBER_TIME = 3
AMBER_THRESHOLD = 50
GREEN_PIN = board.D10
GREEN_TIME = 30

DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_BORDER = 2

STARTUP_TIME = 5


class TrafficSignal:
    def __init__(self):
        self.i2c = i2c = board.I2C()
        self.setup_oled()

        # m4 express CAN boards require manual power management
        # for the onboard neopixel
        neopixel_power = digitalio.DigitalInOut(board.NEOPIXEL_POWER)
        neopixel_power.direction = digitalio.Direction.OUTPUT
        neopixel_power.value = True

        # the phases are cycled through with the onboard
        # RGB neopixel if you have no GPIO pins wired up
        self.pixels = neopixel.NeoPixel(
            board.NEOPIXEL, 1, brightness=0.2, auto_write=True, bpp=3
        )

        self.current_color = None

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
        self.power_light.value = True

        # Garmin LIDAR-Lite v3
        self.lidar = adafruit_lidarlite.LIDARLite(i2c)

    def setup_oled(self):
        displayio.release_displays()
        display_bus = I2CDisplayBus(self.i2c, device_address=0x3C)

        display = adafruit_displayio_sh1107.SH1107(
            display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT
        )
        self.screen = displayio.Group()
        display.root_group = self.screen

    def set_text(self, text):
        if len(self.screen) == 0:
            text_area = label.Label(
                terminalio.FONT,
                text=text,
                scale=5,
                color=0xFFFFFF,
                x=20,
                y=DISPLAY_HEIGHT // 2,
            )
            self.screen.append(text_area)
        self.screen[0].text = text

    def all_lights_off(self):
        self.red_light.value = False
        self.amber_light.value = False
        self.green_light.value = False

    def red_light_on(self):
        self.red_light.value = True

    def amber_light_on(self):
        self.amber_light.value = True

    def green_light_on(self):
        self.green_light.value = True

    def set_light(self, color, on_fn):
        if self.current_color == color:
            return

        self.pixels[0] = color
        self.all_lights_off()
        on_fn()
        self.current_color = color

    def startup(self):
        self.all_lights_off()
        self.pixels[0] = WHITE

        for i in range(STARTUP_TIME, 0, -1):
            self.set_text(str(i))
            time.sleep(1)

    def run(self):
        while True:
            try:
                current_distance = self.lidar.distance
                self.set_text(str(current_distance))

                if current_distance > AMBER_THRESHOLD:
                    self.set_light(GREEN, self.green_light_on)
                elif (
                    current_distance <= AMBER_THRESHOLD
                    and current_distance > RED_THRESHOLD
                ):
                    self.set_light(AMBER, self.amber_light_on)
                elif current_distance <= RED_THRESHOLD:
                    self.set_light(RED, self.red_light_on)
            except RuntimeError as e:
                print(e)

            time.sleep(0.2)


traffic_signal = TrafficSignal()
traffic_signal.startup()
traffic_signal.run()
