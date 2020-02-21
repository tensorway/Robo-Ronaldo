import RPi.GPIO as GPIO
import time
from robocup import commands as comm


switch_pins = [5, 6, 7, 8]

#print("sw set")
def init():
    GPIO.setmode(GPIO.BCM)
    for pin in switch_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

init()

def state(i):
    return GPIO.input(switch_pins[i])

def check_pause():
    if not state(0):
        while not state(0):
            comm.pause()
            time.sleep(0.01)
            if not state(1):
                comm.set_orientation()
            time.sleep(0.01)
        comm.start()