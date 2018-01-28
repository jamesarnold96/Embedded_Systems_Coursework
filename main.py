
import time
time.sleep_ms(500)
from machine import Pin,I2C
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
#power up
i2c.writeto_mem(0x39,0xA0,bytearray([0x03]))

#continuous measurement
while True:
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
    print (lux)
    time.sleep_ms(1000)
