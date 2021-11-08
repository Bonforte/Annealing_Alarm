#this will monitor for pressure values that exceed a threshhold


from influxdb import InfluxDBClient
import time
from netcon import SIMCall
import json

def VacAlert(th, host, port, database, measurement, phone, stop):
    json_file_path="/home/georgen24/Desktop/Python_Grafana/conf_files/app_conf.json"
    if stop():
        print("Conditions not met for vacmon.")
        
    else:
        #Establishing InfluxDB connection:
        try:
            client = InfluxDBClient(host=host,port=port,database=database)

        except Exception as e:
            print("Could not establish connection to InfluxDB server. Reason: "+str(e))

        while(True):
            try:   
                with open(json_file_path,"r") as file:
                    json_conf = json.load(file)
            except Exception as e:
                print("Cannot open json file in netcon. Reason: "+str(e))
            data = []
            pr1 = []
            pr2 = []
            pr = []

            try:
                result=client.query('SELECT * FROM '+str(measurement))

            except Exception as e:
                print("Measurement not detected. Reason: "+str(e))
                result=0

            if result:
                try:
                    headings=result.raw['series'][0]['columns']
                    
                    for entry in reversed(result.raw['series'][0]['values'][-20:]): 
                        data.append(entry)  
                except Exception as e:
                    print("Could not retrieve data from active measurement. Reason: "+str(e))    

                #dividing pressures for specific sensors:
                for entry in data:
                    if entry[2] == "PR1":
                        pr1.append(entry[1])
                    elif entry[2] == "PR2":
                        pr2.append(entry[1])
                    else:
                        pass
                pr.append(pr1)
                pr.append(pr2)
                print(pr)
                for vec in range(2):

                    counter = 0
                    for value in pr[vec]:
                        if value >= th:
                            counter+=1

                    if counter>=10:
                        print("Threshhold value exceeded. Calling 5 time sequence.")
                        

                        if (json_conf["Call-Monitor_Variables"]["AF"]==0):
                            json_conf["Call-Monitor_Variables"]["AF"]=1
                            for i in range(4):
                                SIMCall(phone)
                                
                                time.sleep(10)
                        break

                    else:
                        print("No problems detected in monitoring of PR" + str(vec+1)+"!")
                        json_conf["Call-Monitor_Variables"]["AF"]=0

            time.sleep(10)

            if stop():
                print("Stopping Initiated for vacmon_influx!")
                time.sleep(1)
                break

            with open(json_file_path,"w") as file:
                json.dump(json_conf, file,indent=2)





