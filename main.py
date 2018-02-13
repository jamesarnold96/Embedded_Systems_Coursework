import utime
import ujson
import network
import machine
from umqtt.simple import MQTTClient

#TODO list
#
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

#servo
servo = machine.PWM(machine.Pin(12),freq=50)
INITIAL_DUTY = 57
STEP_SIZE = 18
direction = True
MARGIN = 0.005

#motor
leftm = machine.PWM(machine.Pin(15),freq=50)
rightm = machine.PWM(machine.Pin(13),freq=50)

#---------------------------------------------------------------
#state of servo
class State(object):
    def __init__(self, direction, duty, luxlst):
        self.direction = direction
        self.duty = duty
        self.luxlst = luxlst
    def __str__(self):
        if direction:
            dir = 'Right '
        else:
            dir = 'Left '
        return dir+str(self.duty)+" "+str(self.luxlst)
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
    client.set_callback(msg_callback)
    client.subscribe('esys/JEDI/Server/')
#---------------------------------------------------------------
#convert raw data to lux, formula from data sheet
def sensor_calc(ch0, ch1):
    if ch0 == 0:
        return float('nan')

    ratio = float(ch1/ch0)

    if 0 <= ratio <= 0.5:
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
#motor move
def motor_move(direction):
    if direction == 'left':
        leftm.duty(440)
        rightm.duty(230)
    elif direction == 'right':
        leftm.duty(230)
        rightm.duty(480)
    elif direction == 'forward':
        leftm.duty(230)
        rightm.duty(230)
    elif direction == 'stop':
        leftm.duty(0)
        rightm.duty(0)
    else:
        print('MOTOR MOVE ERROR')

#possible states:
#left: 21, 30, 39
#forward: 48, 57, 66
#right: 75, 84, 93
def motor_servocontrol(servo_state):
    if servo_state.duty < 57:
        motor_move('left')
    elif servo_state.duty > 57:
        motor_move('right')
    elif servo_state.duty == 57:
        motor_move('forward')
    else:
        print('SERVO CONTROL ERROR')

def motor_overridden(r, l, f):
    if f and not l and not r:
        motor_move('forward')
        print('going forward')
    elif f and not l and r:
        motor_move('right')
        print('going right')
    elif f and l and not r:
        motor_move('left')
        print('going left')
    else:
        motor_move('stop')
        print('going nowhere')
#---------------------------------------------------------------
#servo move should change direction when one edge is reached
#duty cycle range may need to be re-tested
def servo_move(duty, direction):
    if direction:
        duty += STEP_SIZE
    else:
        duty -= STEP_SIZE
    if duty < 21:
        duty = 21
    if duty > 93:
        duty = 93
    servo.duty(duty)
    return duty

def servo_track(state):
    if 21 <= state.duty <= 93:
        utime.sleep_ms(200)
        state.duty = servo_move(state.duty, state.direction)
        state.luxlst = math_keep10(state.luxlst, sensor_read())
        utime.sleep_ms(200)
        # think of better way to set threshold to turn around
        # or just don't move if there isn't too much difference
        if (state.luxlst[-2] - state.luxlst[-1]) >= MARGIN:
            state.direction = not state.direction
        else:
            pass
        return state
#---------------------------------------------------------------
def msg_blink(value):
    if value == 'true':
        red_led.value(0)
    elif value == 'false':
        red_led.value(1)
    else:
        pass

def msg_override(value):
    global override_mode
    servo.duty(57)
    servo_state = State(True, INITIAL_DUTY, [sensor_read()])
    if value == 'true':
        override_mode = True
    elif value == 'false':
        override_mode = False
    else:
        pass

def msg_set_or(direction, value):
    global or_forward
    global or_left
    global or_right

    if value == 'true':
        temp = True
    elif value == 'false':
        temp = False
    else:
        pass

    if direction == 'up':
        or_forward = temp
    elif direction == 'left':
        or_left = temp
    elif direction == 'right':
        or_right = temp
    else:
        pass

def msg_callback(topic, msg):
    print(str(msg))
    data = ujson.loads(msg.decode('utf-8'))
    k = data['inst']
    v = data['state']
    #add authorisation by name field here?
    if k == 'redLED':
        msg_blink(v)
    elif k == 'override':
        msg_override(v)
    elif k == 'up' or 'left' or 'right':
        if override_mode:
            msg_set_or(k, v)
        else:
            pass
    else:
        print('unrecognised instruction: '+str(k))

#---------------------------------------------------------------
#power up
i2c.writeto_mem(0x39,0xA0,bytearray([0x03]))

#initialisation
red_led.value(1)
blue_led.value(1)
override_mode = False
or_forward = False
or_left = False
or_right = False
#this line here is weird
servo.duty(INITIAL_DUTY)
servo_state = State(True, INITIAL_DUTY, [sensor_read()])
leftm.duty(230)
rightm.duty(230)

connect_wifi('EEERover','exhibition')
#---------------------------------------------------------------
#main loop
while True:
    if override_mode:
        motor_overridden(or_right, or_left, or_forward)
        print(str(or_right)+str(or_left)+str(or_forward))
    else:
        #control servo
        servo_state = servo_track(servo_state)
        print(servo_state)

        #control motor
        motor_servocontrol(servo_state)

    #find average
    luxavg = math_listavg(servo_state.luxlst)

    #check if still connected
    if (not sta_if.isconnected()):
        blue_led.value(1)
        connect_wifi('EEERover','exhibition')

    #send message
    payload = ujson.dumps({'name':'neZOOMi-chan',
                            'time':utime.ticks_ms(),
                            'brightness':servo_state.luxlst[-1],
                            'avglight':luxavg,
                            'direction':servo_state.direction,
                            'duty': servo_state.duty})
    client.publish('esys/JEDI/', bytes(payload,'utf-8'))

    #read message
    client.check_msg()

    utime.sleep_ms(100)
#---------------------------------------------------------------