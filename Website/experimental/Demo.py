# Testing the Micropython data sending and receiving to test the website
import time
import machine

red_led = machine.Pin(0, machine.Pin.OUT)
blue_led = machine.Pin(2, machine.Pin.OUT)

def toggle(p):
    p.value(not p.value())

while True:
    toggle(blue_led)
    time.sleep_ms(500)
