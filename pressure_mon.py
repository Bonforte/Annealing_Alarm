#this will monitor for pressure values that exceed a threshhold


from influxdb import InfluxDBClient
import time
import json
import tools



def VacAlert(th, host, port, database, measurement, stop):

    #Defining json config file pathing. Change this when moving code from PC to PC.
    json_file_path="/home/georgen24/Desktop/Python_Grafana/conf_files/app_conf.json"


    #Checking if stop condition is active when first starting the code.
    if stop ():
        print("Conditions not met for vacmon.")
        
    else:
        #Enter while loop
        while(True):


            #Opening json file and checking if it can open. Otherwise sending email
            try:
                #small pause to make sure the threads dont access the file at the same time and encounter error.
                time.sleep(0.5) 

                with open(json_file_path,"r") as file:
                    json_conf = json.load(file)

            except Exception as e:
                print("Cannot open json file. Reason: " + str(e))
                tools.SendEmail_mem()



            #Establishing InfluxDB connection and checking it. Sending email if no connection:
            try:
                client = InfluxDBClient(host=host,port=port,database=database)

            except Exception as e:
                print("Could not establish connection to InfluxDB server. Reason: " + str(e))
                tools.SendEmail(json_conf,"INF")




            #Initializing empty working code variables.
            data = []
            pr1 = []
            pr2 = []
            pr = []



            #Querying InfluxDB measurement. If error, send email
            try:
                result=client.query('SELECT * FROM '+str(measurement))

            except Exception as e:
                print("Measurement not detected. Reason: " + str(e))
                result = 0
                print("Could not establish connection to InfluxDB server. Reason: " + str(e))
                tools.SendEmail(json_conf,"INF")



            #If query was successful
            if result:

                try:
                    headings = result.raw['series'][0]['columns']
                    
                    for entry in reversed(result.raw['series'][0]['values'][-20:]): 
                        data.append(entry)  

                except Exception as e:
                    #Send Email if retrieved data is not proper.
                    print("Could not retrieve data from active measurement. Reason: "+str(e))    
                    tools.SendEmail(json_conf,"INF")

                #Dividing extracted pressure values for specific sensors. One vector for each PR. Both vectors are inserted into PR matrix.
                for entry in data:

                    if entry[2] == "PR1":
                        pr1.append(entry[1])

                    elif entry[2] == "PR2":
                        pr2.append(entry[1])

                    else:
                        pass


                pr.append(pr1)
                pr.append(pr2)
                #PR matrix:
                print(pr)


                #Checking extracted values for over limit values.
                for vec in range(2):
                    
                    counter = 0

                    #Checking each sensor
                    for value in pr[vec]:
                        if value >= th:
                            counter += 1

                    if counter >= 10:
                        print("Threshhold value exceeded. Calling 5 time sequence.")
                        
                        #Checking alarm flags and updating.
                        if (json_conf["Call-Monitor_Variables"]["PF"] == 0):

                            json_conf["Call-Monitor_Variables"]["PF"] = 1

                            #Triggering call sequence
                            for phone in json_conf["Call-Monitor_Variables"]["phone_array"]:

                                for i in range(3):

                                    tools.SIMCall(phone)
                                    time.sleep(60)

                        break

                    else:
                        print("No problems detected in monitoring of PR" + str(vec + 1) + "!")
                        json_conf["Call-Monitor_Variables"]["PF"] = 0


            #Pause
            time.sleep(30)


            #Checking stop condition.
            if stop():
                print("Stopping Initiated for vacmon_influx!")
                time.sleep(1)
                break


            #Updating json file flags for alarms
            with open(json_file_path,"w") as file:
                json.dump(json_conf, file,indent=2)




        #When script ends, values get reset.
        print("Completing ending script protocols!")

        json_conf["Call-Monitor_Variables"]["UF"]=0
        json_conf["Call-Monitor_Variables"]["PF"]=0
        json_conf["Call-Monitor_Variables"]["SEN"]=0
        json_conf["Call-Monitor_Variables"]["SEU"]=0

        with open(json_file_path,"w") as file:
            json.dump(json_conf, file,indent=2)
            
        time.sleep(1)
        





