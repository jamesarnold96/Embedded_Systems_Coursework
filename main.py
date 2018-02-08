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
#state of motor
class State(object):
    def __init__(self, direction, duty, luxlst):
        self.direction = direction
        self.duty = duty
        self.luxlst = luxlst
    def __str__(self):
        return str(self.direction)+" "+str(self.duty)+" "+str(self.luxlst)
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
#convert raw data to lux, formula from data sheet
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
#remove from beginning and add new element to end
def math_keep10(datalst, data):
    datalst.append(data)
    if len(datalst) < 11:
        return datalst
    else:
        return datalst[-10:]

def math_listavg(datalst):
    return sum(datalst) / len(datalst)

#---------------------------------------------------------------
#motor move should change direction when one edge is reached
#duty cycle range may need to be re-tested
def motor_move(duty, direction):
    if direction:
        duty += STEP_SIZE
    else:
        duty -= STEP_SIZE
    if duty < 21:
        duty = 21
    if duty > 120:
        duty = 120
    servo.duty(duty)
    return duty

def motor_track(state):
    if 21 <= state.duty <= 120:
        utime.sleep_ms(300)
        state.duty = motor_move(state.duty, state.direction)
        state.luxlst = math_keep10(state.luxlst, sensor_read())
        utime.sleep_ms(300)
        # think of better way to set threshold to turn around
        # or just don't move if there isn't too much difference
        if (state.luxlst[-2] - state.luxlst[-1]) >= 2:
            state.direction = not state.direction
        else:
            pass
        return state
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
#this line here is weird
servo.duty(INITIAL_DUTY)
current_duty = INITIAL_DUTY
motor_state = State(True, INITIAL_DUTY, [sensor_read()])

connect_wifi('EEERover','exhibition')
#---------------------------------------------------------------
#main loop
while True:
    #control motor
    motor_state = motor_track(motor_state)
    print(motor_state)
    #find average
    luxavg = math_listavg(motor_state.luxlst)

    #check if still connected (donno if this code works yet)
    if (not sta_if.isconnected()):
        blue_led.value(1)
        connect_wifi('EEERover','exhibition')

    #send message
    payload = ujson.dumps({'name':'neZOOMi-chan',
                            'time':utime.ticks_ms(),
                            'brightness':motor_state.luxlst[-1],
                            'avglight':luxavg,
                            'direction':motor_state.direction,
                            'duty': motor_state.duty})
    client.publish('esys/JEDI/', bytes(payload,'utf-8'))

    #read message
    client.check_msg()

    utime.sleep_ms(100)
#---------------------------------------------------------------