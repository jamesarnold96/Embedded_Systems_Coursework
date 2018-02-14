import paho.mqtt.client as mqtt
import json
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esys/JEDI/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    data = json.loads(msg.payload.decode('utf-8'))
    # might need errror checks for this
    print(str(data['brightness'])
    		+ ' at: ' + str(data['time'])
    		+ ' with ' + str(data['duty']))
    # a function to collect the data and plot it in time
    #pass
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.10", 1883)

rawin = ''
va = ''

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while (rawin != 'END'):
    rawin = input("\nPlease enter a command:")
    va = input("Please enter the value:")
    payload = json.dumps({'name': 'Dai lo',
                        'inst':rawin,
                        'state':va})
    client.publish('esys/JEDI/Server/', bytes(payload,'utf-8'))

client.loop_stop(force=False)