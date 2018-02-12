#!C:\Users\james\Documents\Python\WinPython-64bit-3.6.3.0Qt5\python-3.6.3.amd64\python.exe
 
# Uses Bottle to handle communication with the website
from bottle import get, request, static_file, run, route

import paho.mqtt.client as mqtt
import json
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esys/JEDI/")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    data = json.loads(msg.payload.decode('utf-8'))
    # might need errror checks for this
    print(str(data['brightness'])
    		+ ' at: ' + str(data['time'])
    		+ ' with ' + str(data['duty']))
    # a function to collect the data and plot it in time


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.10", 1883)
client.publish('esys/JEDI/Server/', 'Connected')

override_state = False;

# main program
def upload(controlIns, controlData):
    print("Connection Successful!")
    payload = json.dumps({'name': 'Dai lo','inst':controlIns,'state':controlData})
    client.publish('esys/JEDI/Server/', bytes(payload,'utf-8'))

# receives button input data from the website 
@get('/control')   
def getData():
    # Instruction from the frontend
    controlIns = request.query.control
    # Button data from the frontend
    controlData = request.query.value
    # only controls the vehicle if the 'override' instruction has been sent
    if(controlIns == 'override'):
        global override_state
        override_state = controlData
        upload(controlIns, controlData)
    elif(override_state):
        upload(controlIns, controlData)
    return 'Input recieved'

# directs a root request to the home page
@route('/testing')
def home_page():
    return static_file('home.html',root='C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website')

# loads html files for display
@route('/testing/<filename>')
def display_page(filename):
    return static_file(filename,root='C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website')

# run program in 'localhost', for testing
run(host='localhost', port=8080, debug=True)