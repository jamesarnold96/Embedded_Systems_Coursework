import time
import json
import network
import machine
from umqtt.simple import MQTTClient

#declarations
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
CLIENT_ID = machine.unique_id()
BROKER_ADDRESS = '192.168.0.10'
#value(1) -> turn off
#value(0) -> turn on
red_led = machine.Pin(0, machine.Pin.OUT)
blue_led = machine.Pin(2, machine.Pin.OUT)
ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)
client = MQTTClient(CLIENT_ID, BROKER_ADDRESS)

#---------------------------------------------------------------
#functions to be moved to seperate files
def connect_wifi(name, password):
    #setup connection
    print ("connecting to " + name + "...")
    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(name, password)
    time.sleep_ms (2000)

    while(not sta_if.isconnected()):
        print ("connection to WiFi failed, retrying in 3 seconds.")
        blue_led.value(0)
        time.sleep_ms(1000)
        sta_if.connect(name, password)
        blue_led.value(1)
        time.sleep_ms(2000)

    print ("connection to WiFi successful, sending message every 0.5 second.")
    blue_led.value(0)
    #MQTT setup
    client.connect()
    client.set_callback(print_msg)
    client.subscribe('esys/JEDI/Server/')

def calc_lux(ch0, ch1):
    if ch0 == 0:
        return float('nan')

    ratio = float(ch1/ch0)

    if 0 < ratio <= 0.5:
        return 0.0304*ch0 - 0.062*ch0*(ratio**1.4)
    elif 0.5 <ratio <= 0.61:
        return 0.0224*ch0 - 0.031*ch1
    elif 0.61 < ratio <= 0.80:
        return 0.0128*ch0 - 0.0153*ch1
    elif 0.8 < ratio <= 1.3:
        return 0.00146*ch0 - 0.00112*ch1
    elif ratio>1.3:
        return 0

def blink_msg(topic, msg):
    if msg == b'Hello ESP8266':
        blue_led.value(0)
        time.sleep_ms(500)
        blue_led.value(1)

def print_msg(topic, msg):
    print(msg)


#---------------------------------------------------------------
#power up
i2c.writeto_mem(0x39,0xA0,bytearray([0x03]))
red_led.value(1)
blue_led.value(1)

connect_wifi('EEERover','exhibition')
#---------------------------------------------------------------
#main loop
while True:
    #read data
    channel0 = i2c.readfrom_mem(0x39,0xAC,2)
    channel0 = int.from_bytes(channel0,'little')

    channel1 = i2c.readfrom_mem(0x39,0xAE,2)
    channel1 = int.from_bytes(channel1,'little')

    #calc output
    lux = calc_lux(channel0, channel1)
    print (lux)

    #read physcial input

    #control motor

    #check if still connected (donno if this code works yet)
    if (not sta_if.isconnected()):
        blue_led.value(1)
        connect_wifi('EEERover','exhibition')

    #send message
    payload = json.dumps({'name':'luminous flux','data':lux})
    client.publish('esys/JEDI/', bytes(payload,'utf-8'))

    #read message
    client.check_msg()

    time.sleep_ms(800)
#---------------------------------------------------------------