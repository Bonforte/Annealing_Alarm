#!/usr/bin/env python3

#This is the main code which will run the inferior threads.

import netcon as nc
import vacmon_influx as vi
import json
import time
import threading
import sys


print("Initializing settings...")
json_file_path="/home/georgen24/Desktop/Python_Grafana/conf_files/app_conf.json"
threads = []
stop = False

try:
    with open(json_file_path,"r") as file:
        json_conf = json.load(file)
except Exception as e:
    print("Cannot open json file. Reason: "+str(e))
    stop = True
    

time.sleep(1)

host =json_conf["InfluxDB"]["host"]
port =json_conf["InfluxDB"]["port"]
database = json_conf["InfluxDB"]["database"]
measurement = json_conf["InfluxDB"]["msr_name"]
url = json_conf["Call-Monitor_Variables"]["url"]
timeout = json_conf["Call-Monitor_Variables"]["timeout"]
phone = json_conf["Call-Monitor_Variables"]["phone"]
th = json_conf["Call-Monitor_Variables"]["th"]

time.sleep(1)

try:
    
    x=threading.Thread(target=nc.NetMonitoring,args = (url, timeout, phone, lambda:stop,), name="Network_Connection")
    x.daemon=True
    threads.append(x)

    y=threading.Thread(target=vi.VacAlert, args =(th, host, port, database, measurement, phone, lambda: stop,), name="Vac_Alarm_Monitor")
    y.daemon=True
    threads.append(y)

    for i in threads:
        i.start()
        print("Starting "+str(i.name)+".\n")

    while(True):
        time.sleep(60)
except:
    print("Sending STOP signal.")
    stop=True
    time.sleep(2)
    print("Main Finishing Execution.")
    time.sleep(1)
    sys.exit()




