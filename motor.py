# implement a perturb and observe algorithm
#duty cycle range:(21-120), error massage generated when outside the range
#center: 57
#CW:- ACW:+
import time

# functions needed from motor
# move by 'amount' angle in the specified direction

import machine
time.sleep_ms(500)
from machine import Pin,I2C
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
#power up
i2c.writeto_mem(0x39,0xA0,bytearray([0x03]))

#initialize pwm pin
servo=machine.PWM(machine.Pin(12),freq=50)

#issue:  pass by referenct in MP
def motor_move(current_duty,direction):

    if direction == 'AW':
        current_duty = current_duty + 10
       
    elif direction == 'CW':
        current_duty = current_duty - 10
       
    servo.duty(current_duty)

    
def sensor_read():
    channel0 = i2c.readfrom_mem(0x39,0xAC,2)
    channel0 = int.from_bytes(channel0,'little')

    channel1 = i2c.readfrom_mem(0x39,0xAE,2)
    channel1 = int.from_bytes(channel1,'little')

    ratio = float(channel1/channel0)

    if 0< ratio <=0.5:
        lux =  0.0304*channel0 - 0.062*channel0*(ratio**1.4)
    elif 0.5 <ratio <= 0.61:
        lux = 0.0224*channel0 - 0.031*channel1
    elif 0.61 < ratio <= 0.80:
        lux = 0.0128*channel0 - 0.0153*channel1
    elif 0.8 < ratio <= 1.3:
        lux = 0.00146*channel0 - 0.00112*channel1
    elif ratio>1.3:
        lux = 0
        
    print(lux)
    return lux


#reset to central position

current_duty = 57
step =8
direction = ['AW', 'CW']
index = 0;
servo.duty(57)
while True:
    if current_duty>=21 and current_duty<=120:
        old_lux = sensor_read()
        time.sleep_ms(500)
        if direction[index] == 'AW':
            current_duty = current_duty + step
       
        elif direction[index] == 'CW':
            current_duty = current_duty - step
       
        servo.duty(current_duty)
        new_lux = sensor_read()
        time.sleep_ms(500)
        if new_lux <= old_lux:
            index = ~index
            if direction[index] == 'AW':
                current_duty = current_duty + step
       
            elif direction[index] == 'CW':
                current_duty = current_duty - step
                
            servo.duty(current_duty)
    elif current_duty<21 or current_duty>120:
        if current_duty <21:
            current_duty = current_duty+step+21-current_duty
        else:
            current_duty = current_duty-step-current_duty+120
            
        print('The max lux position is out of range')

    print(current_duty)
    time.sleep_ms(500)


