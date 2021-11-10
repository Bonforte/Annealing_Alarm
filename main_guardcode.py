#!/usr/bin/env python3

#This is the main code which will run the inferior threads.

import facilities_mon as fm
import pressure_mon as pm
import json
import time
import threading
import sys
import tools


#Initializing starting variables.
print("Initializing settings...")

json_file_path="/home/georgen24/Desktop/Python_Grafana/conf_files/app_conf.json"
threads = []
stop = False


#Opening json file. Otherwise email.
try:
    with open(json_file_path,"r") as file:
        json_conf = json.load(file)

except Exception as e:
    print("Cannot open json file. Reason: "+str(e))
    stop = True
    tools.SendEmail_mem()

time.sleep(1)


#Loading important values from json configuration file.
host =json_conf["InfluxDB"]["host"]
port =json_conf["InfluxDB"]["port"]
database = json_conf["InfluxDB"]["database"]
measurement = json_conf["InfluxDB"]["msr_name"]
url = json_conf["Call-Monitor_Variables"]["url"]
timeout = json_conf["Call-Monitor_Variables"]["timeout"]
th = json_conf["Call-Monitor_Variables"]["th"]

time.sleep(1)


#Starting threads
try:
    
    x=threading.Thread(target=fm.Facilities_Monitoring,args = (url, timeout, lambda:stop,), name="Power_Out_Check")
    x.daemon=True
    threads.append(x)

    y=threading.Thread(target=pm.VacAlert, args =(th, host, port, database, measurement,  lambda: stop,), name="Vac_Alarm_Monitor")
    y.daemon=True
    threads.append(y)


    #Starting defined threads
    for i in threads:
        i.start()
        print("Starting "+str(i.name)+".\n")

    #Entering infinite loop
    while(True):
        time.sleep(30)

#If error encountered (example keyboard interrupt) code initializes closing procedures.
except:
    print("Sending STOP signal.")

    stop=True

    #Waiting for threads to successfully end.
    time.sleep(3)

    print("Main Finishing Execution.")

    #Exiting program.
    sys.exit()




