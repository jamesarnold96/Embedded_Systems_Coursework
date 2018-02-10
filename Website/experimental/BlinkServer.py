#!C:\Users\james\Documents\Python\WinPython-64bit-3.6.3.0Qt5\python-3.6.3.amd64\python.exe

import cgi
import cgitb
cgitb.enable(display=0, logdir="C:/xampp/htdocs/testing/logdir")
#cgitb.enable()

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

# receives button input data from the website    
def getData():
    buttonData = cgi.FieldStorage()
    buttonState = buttonData.getvalue('buttonState')
    return buttonState

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.10", 1883)
client.publish('esys/JEDI/Server/', 'Working so far...')

# main program
if __name__ == "__main__":
    try:
        buttonState = getData()
        if buttonState == "true": # JS true != Python True
            print("Connection Successful!")
            rawin = 'blink'
            payload = json.dumps({'name': 'Dai lo','inst':rawin,})
            client.publish('esys/JEDI/Server/', bytes(payload,'utf-8'))
    except:
        cgi.print_exception()