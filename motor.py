# implement a perturb and observe algorithm
import time

# functions needed from motor
# move by 'amount' angle in the specified direction
def motor_move(amount, direction):
    if direction == 'ACW':
        pass
    elif direction == 'CW':
        pass
        
# move to a specified angle
def motor_abs(angle):
    pass

# functions needed from sensor
def sensor_read():
    return 1.0

# parameters
SMALL = 1

# initialisation
# use string for state?
# true is CW, false is ACW
State = True
old_max = 0.0

# adjusting functions

# loop
while (True):
    if State:
        motor_move(SMALL, 'CW')
        new_max = sensor_read()

        if new_max > old_max:
            old_max = new_max
            # time.sleep_ms(500)
            
        else:
            old_max = new_max
            State = not State
            # time.sleep_ms(500)

    else:
        motor_move(SMALL, 'ACW')
        new_max = sensor_read()

        if new_max > old_max:
            old_max = new_max
            # time.sleep_ms(500)
            
        else:
            old_max = new_max
            State = not State
            # time.sleep_ms(500)
