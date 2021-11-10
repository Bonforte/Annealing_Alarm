#this will monitor for internet down(meaning current off)

###### DO NOT FORGET##########
#start android debugging server: sudo adb start-server

from ppadb.client import Client as AdbClient
import sys
import time
import os
import requests
import json
from bs4 import BeautifulSoup
import urllib.request
from IPython.display import HTML
import re
import tools




def Facilities_Monitoring (url, timeout,stop):
    #Defining json config file pathing. Change this when moving code from PC to PC.
    json_file_path = "/home/georgen24/Desktop/Python_Grafana/conf_files/app_conf.json"


    #Checking if stop condition is active when first starting the code.
    if stop ():
        print("Conditions not met for netcon.")
        
    else:
        #Enter while loop
        while(True):
            

            #Opening json file and checking if it can open. Otherwise sending email
            try:   
                with open(json_file_path,"r") as file:
                    json_conf = json.load(file)
                
            except Exception as e:
                print("Cannot open json file. Reason: "+str(e))
                tools.SendEmail_mem()



            #Checking UPS activation condition (time of battery is less than 50 min. Normal functioning parameters are battery life >50 min)
            try:
                #reading value and configuring alarm flag with its specific value.
                remaining_time = tools.UPS_rd(json_conf)
                json_conf["Call-Monitor_Variables"]["SEU"]=0

                if remaining_time <= 50: 
                    #Initiating call sequence to the persons in charge as alarm is triggered. (Pause of 60 seconds between sequence calls.)
                    for phone in json_conf["Call-Monitor_Variables"]["phone_array"]:

                        for i in range(3):

                            tools.SIMCall(phone)
                            time.sleep(60)

            #Sending email if connection to UPS through network failed.
            except:
                if json_conf["Call-Monitor_Variables"]["SEU"] == 0:
                    tools.SendEmail(json_conf, "UPS")
                    json_conf["Call-Monitor_Variables"]["SEU"] = 1



            #Checking internet connection
            try:
                request = requests.get(url=url,timeout=timeout)

                print("\nConnection to Internet is active!\n")
                json_conf["Call-Monitor_Variables"]["SEN"] = 0

                time.sleep(120)

            except(requests.ConnectionError, requests.Timeout) as exception:
                
                print("No Internet connection detected!\n")
                
                #If request variable encountered an error, in this exception we will issue a call sequence, because of internet outage.
                if (json_conf["Call-Monitor_Variables"]["SEN"] == 0):

                    for phone in json_conf["Call-Monitor_Variables"]["phone_array"]:

                        for i in range(3):

                            tools.SIMCall(phone)
                            time.sleep(60)

                    json_conf["Call-Monitor_Variables"]["SEN"]=1
                   


            #Checking stop condition.
            if stop():
                print("Stopping Initiated for netcon!")
                time.sleep(1)
                break


            #Updating json file flags for alarms
            with open(json_file_path,"w") as file:
                json.dump(json_conf, file,indent = 2)
        

            #Waiting time
            time.sleep(30)



        #When script ends, values get reset.
        print("Completing ending script protocols!")

        json_conf["Call-Monitor_Variables"]["UF"] = 0
        json_conf["Call-Monitor_Variables"]["PF"] = 0
        json_conf["Call-Monitor_Variables"]["SEN"] = 0
        json_conf["Call-Monitor_Variables"]["SEU"] = 0

        with open(json_file_path,"w") as file:
            json.dump(json_conf, file,indent = 2)

        time.sleep(1)
        
                