#this will monitor for internet down(meaning current off)

###### DO NOT FORGET##########
#start android debugging server: sudo adb start-server

from ppadb.client import Client as AdbClient
import sys
import time
import os
import requests
import json




def SIMCall (phone):

    

    try:
        client=AdbClient(host="127.0.0.1", port=5037)
        devices=client.devices()
    except Exception as e:
        print("Problem detected with ADB server. Calls will not be active! Reason: "+str(e))
        time.sleep(30)
    
    if devices:
        
        os.system(f'adb shell am start -a android.intent.action.CALL -d tel:{phone}')
        print("Initiating call!\n")
        
    else:
        
        print("No devices connected!\n")
        print("Call was not initiated. Major Alarm Problem.")


def NetMonitoring (url, timeout, phone,stop):
    json_file_path="/home/georgen24/Desktop/Python_Grafana/conf_files/app_conf.json"

    if stop():
        print("Conditions not met for netcon.")
        
    else:
        while(True):
            try:   
                with open(json_file_path,"r") as file:
                    json_conf = json.load(file)
            except Exception as e:
                print("Cannot open json file. Reason: "+str(e))

            try:
                request = requests.get(url=url,timeout=timeout)
                print("\nConnection to Internet is active!\n")
                json_conf["Call-Monitor_Variables"]["AF"]=0
                # time.sleep(120)
                

            except(requests.ConnectionError, requests.Timeout) as exception:
                
                print("No Internet connection detected!\n")
                print("Initiating 5 call sequence.")
                

                if (json_conf["Call-Monitor_Variables"]["AF"]==0):
                    json_conf["Call-Monitor_Variables"]["AF"]=1
                    for i in range(1):
                        SIMCall(phone)
                        
                        time.sleep(10)
                
            time.sleep(10)

            if stop():
                print("Stopping Initiated for netcon!")
                time.sleep(1)
                break

            with open(json_file_path,"w") as file:
                json.dump(json_conf, file,indent=2)
        
                