"""Python server code for processing and storing sensor data for the NeZOOMi
tunnel and pipe cleaning vehicle prototype. This code also allows the vehicle 
to be controlled via the website, along with the display of sensor data. To access
the website, type localhost:8080 into a web browser whilst this code is running.
The file paths in lines 35, 81, 106 and 112 will have to be changed to ones 
corresponding to the project folder on your machine,"""

# Uses Bottle to handle communication with the website
from bottle import get, request, static_file, run, route

# MQTT libary for communicating with the bug
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
    #print(msg.topic+" "+str(msg.payload))
    sensorData = json.loads(msg.payload.decode('utf-8'))
    # might need errror checks for this
    print(str(sensorData['brightness'])
    		+ ' at: ' + str(sensorData['time'])
    		+ ' with ' + str(sensorData['duty']))
    #print(sensorData)
    # opens json file to store data (as a list)
    with open('C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website/sensorData.json','r+',encoding='utf-8') as f:
    # Read sensor data
        fileData = json.load(f)
        # moves pointer to beginning of .json file to ensure contents are overwritten
        f.seek(0)
        # Add the new data to the list
        fileData.append(sensorData)
        #print(fileData)
        # Write the data to the json file
        json.dump(fileData,f)
        # a function to collect the data and plot it in time

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.10", 1883)

# Only send instructions if "override" instruction has been sent
override_state = False;

# send control instructions to bug using MQTT
def upload(controlIns, controlData):
    print("Connection Successful!")
    payload = json.dumps({'inst':controlIns,'state':controlData})
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

# Displays a table of the last 20 data entries
@get('/table')
def displayTable():
    with open('C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website/sensorData.json','r+') as f:
        # Read sensor data
        sensorData = json.loads(f.read())
        tableTxt = """
        <table class="table table-dark table-striped" style="padding-top:50px">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Brightness(Lux)</th>
                    <th>Duty</th>
                </tr>
            </thead>
            <tbody>"""
        # loop over last 20 list items to build table
        for i in range(20):
            latest = sensorData[len(sensorData) - 1 - i]
            tableTxt += '<tr><td>'+ str(latest['time']) + '</td><td>'\
            + str(latest['brightness']) +  '</td><td>' + str(latest['duty']) + '</td></tr>'
        tableTxt += '</tbody></table>'
        return tableTxt    

# directs a root request to the home page
# NB This path will have to be changed to the relevant location on your computer
@route('/')
def home_page():
    return static_file('home.html',root='C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website')

# loads files from the required for display
# NB This path will have to be changed to the relevant location on your computer
@route('/<filename>')
def display_page(filename):
    return static_file(filename,root='C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website')

# run program in 'localhost', for testing
client.loop_start()
run(host='localhost', port=8080, debug=True)
client.loop_stop()