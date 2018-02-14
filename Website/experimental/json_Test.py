# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 18:20:34 2018
JSON Test: testing reading and writing of JSON files


@author: james
"""

import json

sensorData = {'Time':24,'Name':'James','Doomed':'Absolutely'}

with open('C:/Users/james/Documents/GitHub/Embedded_Systems_Coursework/Website/Experimental/test.json','r+',encoding='utf-8') as f:
# Read sensor data
    fileData = json.load(f)
    f.seek(0)
    # Add the new data to the list
    fileData.append(sensorData)
    print(fileData)
    # Write the data to the json file
    json.dump(fileData,f)
    # a function to collect the data and plot it in time
