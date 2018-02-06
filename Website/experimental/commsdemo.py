# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 22:01:55 2018

@author: james
"""

# Testing the Micropython data sending and receiving to test the website
import time
import machine
import ujson

BROKER_ADDRESS = '192.168.0.10'
CLIENT_ID = machine.unique_id()

# Set up connection
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover', 'exhibition')

# Connect to Wi-Fi
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
    client.set_callback(msg_print)
    client.subscribe('esys/JEDI/Server/')

# pins which control the LEDs
red_led = machine.Pin(0, machine.Pin.OUT)
blue_led = machine.Pin(2, machine.Pin.OUT)

# JSON string of test data to send over Wi-Fi
data_list = [1, 4, 56, 97, 43, 23]
data = dict()
data["data"] = data_list
jdata = ujson.dumps(data)


    
