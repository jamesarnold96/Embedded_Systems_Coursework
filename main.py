import utime
import ujson
import network
import machine
from umqtt.simple import MQTTClient

#--------------------------neZOOMi-----------------------------
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
MARGIN = 0.005

#motor
leftm = machine.PWM(machine.Pin(15),freq=50)
rightm = machine.PWM(machine.Pin(13),freq=50)

#override
override_mode = False
or_forward = False
or_left = False
or_right = False
#---------------------------------------------------------------
#state of servo
class State(object):
    def __init__(self, direction, duty, luxlst):
        self.direction = direction
        self.duty = duty
        self.luxlst = luxlst
    #pretty printing
    def __str__(self):
        if self.direction:
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
def math_keep20(datalst, data):
    datalst.append(data)
    if len(datalst) < 21:
        return datalst
    else:
        return datalst[-20:]

def math_listavg(datalst):
    return sum(datalst) / len(datalst)
#---------------------------------------------------------------
#motor move
#values found empirically, on smooth surface
def motor_move(direction):
    if direction == 'right':
        leftm.duty(430)
        rightm.duty(0)
    elif direction == 'left':
        leftm.duty(0)
        rightm.duty(480)
    elif direction == 'forward':
        leftm.duty(230)
        rightm.duty(230)
    elif direction == 'forleft':
        leftm.duty(230)
        rightm.duty(480)
    elif direction == 'forright':
        leftm.duty(430)
        rightm.duty(230)
    elif direction == 'stop':
        leftm.duty(0)
        rightm.duty(0)
    else:
        print('MOTOR MOVE ERROR')
    utime.sleep_ms(150)

def motor_servocontrol(servo_state):
    if servo_state.duty < 48:
        motor_move('right')
    elif servo_state.duty > 66:
        motor_move('left')
    elif 48 <= servo_state.duty <= 66:
        motor_move('forward')
    else:
        print('SERVO CONTROL ERROR')
    
#three boolean values corresponds to arrow key presses from website
#pressing down sets to true, key release sets to false by msg_set_or
def motor_overridden(r, l, f):
    if f and not l and not r:
        motor_move('forward')
    elif not f and not l and r:
        motor_move('right')
    elif not f and l and not r:
        motor_move('left')
    elif f and not l and r:
        motor_move('forright')
    elif f and l and not r:
        motor_move('forleft')
    else:
        motor_move('stop')
        print('going nowhere')
#---------------------------------------------------------------
def servo_move(duty, direction):
    if direction:
        duty -= STEP_SIZE
    else:
        duty += STEP_SIZE
    if duty < 21:
        duty = STEP_SIZE + 21
    if duty > 93:
        duty = 93 - STEP_SIZE
    servo.duty(duty)
    return duty

#Decision making in autonomous mode, uses 'perturb and observe'
#Values determined empirically
def servo_track(state):
    motor_move('forward')
    if 21 <= state.duty <= 93:
        old_lux = sensor_read()
        state.duty = servo_move(state.duty, state.direction)
        utime.sleep_ms(200)
        state.luxlst = math_keep20(state.luxlst, old_lux)
        new_lux = sensor_read()
        state.luxlst = math_keep20(state.luxlst, new_lux)
        
        #don't move if there isn't too much difference
        #if (state.luxlst[-2] - state.luxlst[-1]) >= MARGIN:
        if new_lux <= old_lux - MARGIN:
            state.direction = not state.direction
            state.duty = servo_move(state.duty, state.direction)
            utime.sleep_ms(200)
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

#change override 
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

#set override direction
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

#---------------------------------------------------------------
# note on I/O with server:
# neZOOMi is subscribed to esys/JEDI/Server
# expects messages in JSON with a 'inst' and a 'state' string
# LED control only needs 'redLED' 'true/false'
# motor and servo controls requires setting override to true
#---------------------------------------------------------------
def msg_callback(topic, msg):
    print(str(msg))
    data = ujson.loads(msg.decode('utf-8'))
    k = data['inst']
    v = data['state']
    #could add authorisation by name field here if needed
    #if data['name'] == 'Dai lo':
    if k == 'redLED':
        msg_blink(v)
    elif k == 'override':
        msg_override(v)
    elif k == 'up' or 'left' or 'right':
        if override_mode:
            msg_set_or(k, v)
        else:
            pass
    elif k == 'servo' and override_mode:
        servo.duty(v)
    else:
        print('unrecognised instruction: '+str(k))

#---------------------------------------------------------------
#power up
i2c.writeto_mem(0x39,0xA0,bytearray([0x03]))

#initialisation
red_led.value(1)
blue_led.value(1)
servo.duty(INITIAL_DUTY)
servo_state = State(True, INITIAL_DUTY, [sensor_read()])
leftm.duty(0)
rightm.duty(0)

connect_wifi('EEERover','exhibition')
#---------------------------------------------------------------
#main loop
while True:
    if override_mode:
        motor_overridden(or_right, or_left, or_forward)
        #print(str(or_right)+str(or_left)+str(or_forward))
    else:
        #control servo
        servo_state = servo_track(servo_state)
        #print(servo_state)

        #control motor
        motor_servocontrol(servo_state)

    #find average
    #useful when used with manual servo control to read
    #average brightness in a specified direction
    luxavg = math_listavg(servo_state.luxlst)

    #check if still connected before IO through MQTT
    if (not sta_if.isconnected()):
        blue_led.value(1)
        connect_wifi('EEERover','exhibition')

    #send message
    payload = ujson.dumps({'name':'neZOOMi-chan',
                            'time':utime.ticks_ms(),
                            'brightness':servo_state.luxlst[-1],
                            'brit_list':servo_state.luxlst,
                            'avglight':luxavg,
                            'direction':servo_state.direction,
                            'duty': servo_state.duty})
    client.publish('esys/JEDI/', bytes(payload,'utf-8'))

    #read message
    client.check_msg()

    utime.sleep_ms(10)
#---------------------------------------------------------------

