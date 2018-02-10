import utime
import ujson
import network
import machine
from umqtt.simple import MQTTClient

#TODO list
#define a mutable class with all state parameters
#wifi connection temporarily commented out for motor testing 
#---------------------------------------------------------------
#declarations
#communication
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
CLIENT_ID = machine.unique_id()
BROKER_ADDRESS = '192.168.0.10'
ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)
client = MQTTClient(CLIENT_ID, BROKER_ADDRESS)

#leds
#value(1) -> turn off
#value(0) -> turn on
red_led = machine.Pin(0, machine.Pin.OUT)
blue_led = machine.Pin(2, machine.Pin.OUT)

#---------------------------------------------------------------
def connect_wifi(name, password):
    #setup connection
    print ("connecting to " + name + "...")
    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect(name, password)
    utime.sleep_ms (2000)

    while(not sta_if.isconnected()):
        print ("connection to WiFi failed, retrying in 3 seconds.")
        blue_led.value(0)
        utime.sleep_ms(1000)
        sta_if.connect(name, password)
        blue_led.value(1)
        utime.sleep_ms(2000)

    print ("connection to WiFi successful.")
    blue_led.value(0)
    #MQTT setup
    client.connect()
    client.set_callback(msg_print)
    client.subscribe('esys/JEDI/Server/')
    client.publish('esys/JEDI/Server/','working')
    
def msg_print(topic, msg):
    print(str(msg))
    data = ujson.loads(msg.decode('utf-8'))
    k = data['inst']
    if (k == 'blink'):
        blue_led.value(1)
        utime.sleep_ms(100)
        blue_led.value(0)
    elif (k == 'reset'):
        #current_duty = 57
        #servo.duty(current_duty)
        print("servo reset does not work yet.")
    else:
        print(k)
    
#---------------------------------------------------------------
#initialisation
connect_wifi('EEERover','exhibition')

#---------------------------------------------------------------
#main loop
try:
    while 1:
        #micropython.mem_info()
        client.wait_msg()
finally:
        client.disconnect()
    





    
