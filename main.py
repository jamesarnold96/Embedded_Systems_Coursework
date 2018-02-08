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

#motor
servo = machine.PWM(machine.Pin(12),freq=50)
INITIAL_DUTY = 57
STEP_SIZE = 8
direction = True

#---------------------------------------------------------------
# class tracker_state:
#     def __init__(self, direction, duty, lux):
#         self.direction = direction
#         self.duty = duty
#         self.lux = lux

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
#---------------------------------------------------------------
def sensor_calc(ch0, ch1):
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

def sensor_read():
    #read data
    channel0 = i2c.readfrom_mem(0x39,0xAC,2)
    channel0 = int.from_bytes(channel0,'little')

    channel1 = i2c.readfrom_mem(0x39,0xAE,2)
    channel1 = int.from_bytes(channel1,'little')

    #calc output
    lux = sensor_calc(channel0, channel1)
    print (lux)
    return lux

#---------------------------------------------------------------
def math_keep10(datalst, data):
    l = len(datalst)
    datalst.append(data)
    if l < 11:
        return datalst
    else:
        return datalst[l-10:l]

def math_listavg(datalst):
    return sum(datalst) / len(datalst)

#---------------------------------------------------------------
#motor move should change direction when one edge is reached
#duty cycle range may need to be re-tested
#a mutable class should be passed around this group of functions
def motor_move(current_duty, direction):
    if direction:
        current_duty += STEP_SIZE
    else:
        current_duty -= STEP_SIZE
    if current_duty < 21:
        current_duty = 21
    if current_duty > 120:
        current_duty = 120
    servo.duty(current_duty)
    return current_duty

def motor_track(current_duty, direction, old_lux):
    if 21 <= current_duty <= 120:
        utime.sleep_ms(500)
        current_duty = motor_move(current_duty, direction)
        new_lux = sensor_read()
        utime.sleep_ms(500)
        if new_lux <= old_lux:
            direction = not direction
        else:
            pass
        return (current_duty, direction, new_lux)
#---------------------------------------------------------------
def msg_blink(topic, msg):
    if msg == b'Hello ESP8266':
        blue_led.value(0)
        utime.sleep_ms(500)
        blue_led.value(1)

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
#power up
i2c.writeto_mem(0x39,0xA0,bytearray([0x03]))

#initialisation
red_led.value(1)
blue_led.value(1)
servo.duty(INITIAL_DUTY)
current_duty = INITIAL_DUTY
lux = sensor_read()
luxlst = [lux]

connect_wifi('EEERover','exhibition')
#---------------------------------------------------------------
#main loop
while True:
    #control motor
    (current_duty, direction, lux) = motor_track(current_duty, direction, lux)

    #find average
    luxlst = math_keep10(luxlst, lux)
    luxavg = math_listavg(luxlst)

    #check if still connected (donno if this code works yet)
    if (not sta_if.isconnected()):
        blue_led.value(1)
        connect_wifi('EEERover','exhibition')

    #send message
    payload = ujson.dumps({'name':'neZOOMi-chan',
                            'time':utime.ticks_ms(),
                            'brightness':lux,
                            'avglight':luxavg,
                            'direction':direction,
                            'duty': current_duty})
    client.publish('esys/JEDI/', bytes(payload,'utf-8'))

    #read message
    client.check_msg()

    utime.sleep_ms(100)
#---------------------------------------------------------------