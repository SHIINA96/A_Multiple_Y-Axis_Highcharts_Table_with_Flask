# Setting sqlalchemy
from sqlalchemy import Column, String, Integer, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Create engine
engine = create_engine("mysql+mysqlconnector://bob:secret@localhost:3306/Arduino")

# Web setting
from flask import Flask, render_template, make_response, Response, request, url_for, jsonify
from queue import Queue

import json
import datetime
import requests
import threading
import gevent
import os, sys
import time

app = Flask(__name__)
# devices = Devices()
qTempChart = Queue()
qHumiChart = Queue()

############### Logger Definition Start ###############
# To do - Class for Logger and Publisher
# Logging temp data - simulation
# To do - Error handling. 
temperatureChart_value = 0
humidityChart_value = 0
def log_tempChart(name):
    #print("Starting " + name)
    gevent.sleep(5)
    while True:
        global temperatureChart_value
        global humidityChart_value
        connection = engine.connect()
        temperatureChart_value = connection.execute("select Temperature_Value from Temperature_Data order by Data_ID DESC LIMIT 1")
        for row in temperatureChart_value:
            #print("Temperature:", row['Temperature_Value'])
            tempChart = row['Temperature_Value']
            global temperatureChartValue
            temperatureChartValue = tempChart
        connection.close()
        connection = engine.connect()
        humidityChart_value = connection.execute("select Humidity_Value from Humidity_Data order by Data_ID DESC LIMIT 1")
        for row in humidityChart_value:
            #print("Humidity:", row['Humidity_Value'])
            humiChart = row['Humidity_Value']
            global humidityChartValue
            humidityChartValue = humiChart
        connection.close()

        # print("temp added in the queue")
        qTempChart.put(tempChart)
        qHumiChart.put(humiChart)
        gevent.sleep(0.5)
############### Logger Definition End ###############


############### Stream Definition Start ############### 
def streamTemperatureChart_Data():
    #print("Starting streaming")
    while True:
        if not qTempChart.empty() and not qHumiChart.empty():
            resultTempChart = [(time.time())*1000, temperatureChartValue, humidityChartValue]
            yield 'data: ' + json.dumps(resultTempChart) + "\n\n"
            gevent.sleep(1)
        else:
            gevent.sleep(1) # Try again after 1 sec
            # os._exit(1)
############### Stream Definition End ###############


############### Route Definition Start ###############
# Home page route
@app.route('/')
def home():
    #print("Index requested")
    return render_template('dashboard.html')
    
# Highcharts Route
@app.route('/streamTemperatureChart/', methods=['GET', 'POST'])
def streamTemperatureChart():
    # gevent.sleep(1)
    #print("stream requested/posted")
    return Response(streamTemperatureChart_Data(), mimetype="text/event-stream")
        
############### Route Definition End ###############


if __name__ == '__main__':
    try:
       
        thTempChart = threading.Thread(target=log_tempChart, args=("tempChart_logger",)) 
        thTempChart.start()

        print ("Thread(s) started..")
    except:
        print ("Error: unable to start thread(s)")
        os._exit(1)
    else:
        # start streaming
        try:
            app.secret_key = 'verySecret#123'
            app.run(debug=True, threaded = True, host='127.0.0.1', port=5000)
            # app.run(debug=True, threaded = True, host='192.168.1.68', port=5000)

        except:
            print ("Streaming stopped")
            os._exit(1)
    