import board
import digitalio
import neopixel
import time
from adafruit_led_animation.color import RED
from adafruit_led_animation.color import AMBER
from adafruit_led_animation.color import GREEN

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


class TrafficSignal:
    def __init__(self):
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

    def all_lights_off(self):
        print("ALL OFF")
        self.red_light.value = False
        self.amber_light.value = False
        self.green_light.value = False

    def red_light_on(self):
        self.red_light.value = True

    def amber_light_on(self):
        self.amber_light.value = True

    def green_light_on(self):
        self.green_light.value = True

    def run_phase(self, name, color, sleep_time, on_fn):
        self.pixels[0] = color
        self.all_lights_off()
        print(f"{name} ON")
        on_fn()
        time.sleep(sleep_time)

    def run_phases(self):
        print("\n---")
        print("STARTING PHASE LOOP")
        print("---\n")

        self.power_light.value = True

        while True:
            self.run_phase("RED", RED, RED_TIME, self.red_light_on)
            self.run_phase("GREEN", GREEN, GREEN_TIME, self.green_light_on)
            self.run_phase("AMBER", AMBER, AMBER_TIME, self.amber_light_on)


traffic_signal = TrafficSignal()
traffic_signal.run_phases()
