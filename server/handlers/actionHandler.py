from const import Constants
from handlers.dataHandler import Data, DATA_KEY
from handlers.responseHandler import RESPONSE_KEY, MESSAGE
from controllers.thermostatController import MAX_TEMPERATURE_OFFSET
from controllers.sensorController import Sensor
from handlers.stateLogsHandler import StateLogs
#from hashlib import sha256
#import base64

class Actions:

    #/!\ Warning /!\===================================================/!\ Warning /!\#
    # Actions that don't contain the char '_' in their name are exposed by the server #
    #=================================================================================#

    #Authorization to be implemented
    #def authorize_(authToken,data:Data):
    #    '''
    #    Check if use is authorized and return authorized username
    #    '''
    #    if authToken[:6] != 'Basic ':
    #        return
    #    users = data.getValue(DATA_KEY.users)
    #    authToken = authToken[6:]
    #    authToken = base64.b64decode(authToken).decode(Constants.ENCODING)
    #    authToken = authToken.split(':')
    #    if authToken[0] not in users:
    #        return None
    #    authToken[1] = sha256(authToken[1].encode(Constants.ENCODING)).hexdigest()
    #    if users[authToken[0]] == authToken[1]:
    #        return authToken[0]
    #    return None

    #================#
    # Server Actions #
    #================#====================================
    def _getData(data:Data,response,dataKey,actionName):
        if RESPONSE_KEY.data not in response:
            response[RESPONSE_KEY.data] = {}
        response[RESPONSE_KEY.data][actionName] = data.getValue(dataKey)
        return response

    def _setData(data:Data,response,dataKey,value,actionName):
        if RESPONSE_KEY.data not in response:
            response[RESPONSE_KEY.data] = {}
        if data.setValue(dataKey,value) == True:
            response[RESPONSE_KEY.data][actionName] = MESSAGE.Status.success
        else:
            response[RESPONSE_KEY.data][actionName] = MESSAGE.Status.error
        return response

    def _doResult(data:Data,response,action,message:str,status:str):
        if RESPONSE_KEY.data not in response:
            response[RESPONSE_KEY.data] = {}
        response[RESPONSE_KEY.data][action] = message
        response[RESPONSE_KEY.status] = status
        return response

    #================#
    # Getter Actions #
    #================#====================================
    # Takes 5 arguments: data , response , value, actionName
    def getCurrentTemperature(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getCurrentTemperature"]
        '''
        return Actions._getData(data,response,DATA_KEY.currentTemperature,actionName)

    def getRequiredTemperature(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getRequiredTemperature"]
        '''
        return Actions._getData(data,response,DATA_KEY.requiredTemperature,actionName)

    def getCurrentHumidity(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getCurrentHumidity"]
        '''
        return Actions._getData(data,response,DATA_KEY.currentHumidity,actionName)

    def getThermostatState(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getThermostatState"]
        '''
        return Actions._getData(data,response,DATA_KEY.thermostatState,actionName)

    def getRefreshRate(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getRefreshRate"]
        '''
        return Actions._getData(data,response,DATA_KEY.refreshRate,actionName)

    def getTemperatureOffset(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getTemperatureOffset"]
        '''
        return Actions._getData(data,response,DATA_KEY.temperatureOffset,actionName)

    def getLastUpdate(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getLastUpdate"]
        '''
        return Actions._getData(data,response,DATA_KEY.lastUpdate,actionName)

    def getSessionID(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getSessionID"]
        '''
        response[RESPONSE_KEY.sessionID] = "" #Don't know the sessionID in this context,
                                              #create the key and it will get populated later
        return response #Don't do anything, call this action when you just want the sessionID

    def getStateLogs(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":[{"getStateLogs":{ "year":year, "month":month, "day":day }}]
        '''
        if type(value) != dict:
            return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        if not "year" in value:
            value["year"] = None
        if not "month" in value:
            value["month"] = None
        if not "day" in value:
            value["day"] = None
        logs = StateLogs.getEntries(value["year"], value["month"], value["day"])
        if not RESPONSE_KEY.data in response:
            response[RESPONSE_KEY.data] = {}
        response[RESPONSE_KEY.data][actionName] = logs
        return response

    def getSchedule(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getSchedule"]
        '''
        return Actions._getData(data,response,DATA_KEY.schedule,actionName)
    
    def getSensors(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["getSensors"]
        '''
        if RESPONSE_KEY.data not in response:
            response[RESPONSE_KEY.data] = {}
        response[RESPONSE_KEY.data][actionName] = data.getValue(DATA_KEY.sensors)
        primarySensor = str(data.getValue(DATA_KEY.primarySensor))
        for s in response[RESPONSE_KEY.data][actionName]:
            if (s == primarySensor):
                response[RESPONSE_KEY.data][actionName][s][DATA_KEY.SENSORS.primary] = True
            else:
                response[RESPONSE_KEY.data][actionName][s][DATA_KEY.SENSORS.primary] = False
        return response

    #================#
    # Setter Actions #
    #================#====================================
    # Takes 4 arguments: data , response , value , actionName
    def setRequiredTemperature(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":[{"setRequiredTemperature":10}]
        '''
        if type(value) in [str, int]:
            try:
                value = float(value)
            except:
                return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        if type(value) != float:
            return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        return Actions._setData(data,response,DATA_KEY.requiredTemperature,value,actionName)

    #def setThermostatState(data:Data,response:dict,value,actionName:str):
    #    '''
    #    request : "actions":[{"setThermostatState":False}]
    #    '''
    #    if type(value) != bool:
    #        return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
    #    return Actions._setData(data,response,DATA_KEY.thermostatState,value,actionName)

    def setTemperatureOffset(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":[{"setTemperatureOffset":0.5}]
        '''
        if type(value) in [str,int]:
            try:
                value = float(value)
            except:
                return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        if type(value) != float:
            return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        if value > MAX_TEMPERATURE_OFFSET:
            return MESSAGE.setError(response,MESSAGE.overThanMaxTempOffset,str(MAX_TEMPERATURE_OFFSET))
        return Actions._setData(data,response,DATA_KEY.temperatureOffset,value,actionName)

    def setRefreshRate(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":[{"setRefreshRate":10}]
        '''
        if type(value) in [str,int]:
            try:
                value = int(value)
            except:
                return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        if type(value) != int:
            return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        return Actions._setData(data,response,DATA_KEY.refreshRate,value,actionName)

    def setSchedule(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":[{"setSchedule":{"time":"requiredTemperature"}}]
        '''
        if type(value) != dict:
            return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)
        return Actions._setData(data,response,DATA_KEY.schedule,value,actionName)

    def setSensorData(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":[{"setSensorData":{
            "sensor_0":{"ip":"true/false",name:"","temperatureOffset":"","humidityOffset":"","delete":"false/true","primary":"false/true"} , ...},
            "sensor_1":{"ip":"true/false",name:"","temperatureOffset":"","humidityOffset":"","delete":"false/true","primary":"false/true"} , ...},
            ...
            }
        '''
        if type(value) != dict:
            return MESSAGE.setError(response,MESSAGE.wrongValueType,actionName)

        sensors = data.getValue(DATA_KEY.sensors)
        primary = None

        for itm in value: #For each sesnor value received

            if DATA_KEY.SENSORS.delete in value[itm]: #Marked for deletion
                if value[itm][DATA_KEY.SENSORS.delete]:
                    if itm in sensors: del sensors[itm]
                    continue
            
            if itm not in sensors: #Add new sensor
                sensors[itm] = {
                    DATA_KEY.SENSORS.name:"unnamed" if DATA_KEY.SENSORS.name not in value[itm] else value[itm][DATA_KEY.SENSORS.name],
                    DATA_KEY.SENSORS.ip:Sensor.CheckIPSensor(itm),
                    DATA_KEY.SENSORS.temperatureOffset:0 if DATA_KEY.SENSORS.temperatureOffset not in value[itm] else value[itm][DATA_KEY.SENSORS.temperatureOffset],
                    DATA_KEY.SENSORS.humidityOffset:0 if DATA_KEY.SENSORS.humidityOffset not in value[itm] else value[itm][DATA_KEY.SENSORS.humidityOffset],
                }
            
            else: #Modify existing sensor
                if DATA_KEY.SENSORS.temperatureOffset in value[itm]:
                    sensors[itm][DATA_KEY.SENSORS.temperatureOffset] =  value[itm][DATA_KEY.SENSORS.temperatureOffset]
                if DATA_KEY.SENSORS.humidityOffset in value[itm]:
                    sensors[itm][DATA_KEY.SENSORS.humidityOffset] =  value[itm][DATA_KEY.SENSORS.humidityOffset]
                if DATA_KEY.SENSORS.name in value[itm]:
                    sensors[itm][DATA_KEY.SENSORS.name] =  value[itm][DATA_KEY.SENSORS.name]
                sensors[itm][DATA_KEY.SENSORS.ip] = Sensor.CheckIPSensor(itm)
            
            if DATA_KEY.SENSORS.primary in value[itm]: #Marked as primary sensor
                    if value[itm][DATA_KEY.SENSORS.primary]:
                        primary = itm

        if primary != None:
            data.setValue(DATA_KEY.primarySensor,primary)
        return Actions._setData(data,response,DATA_KEY.sensors,sensors,actionName)

    #============#
    # Do Actions #
    #============#========================================
    # Takes 3 arguments: data , response , value , actionName
    def doSave(data:Data,response:dict,value,actionName:str):
        '''
        request : "actions":["doSave"]
        '''
        success = data.save()
        status = MESSAGE.Status.error
        if success:
            message = MESSAGE.dataSaved
            status = MESSAGE.Status.success
        else:
            message = MESSAGE.dataSaveFailed
        return Actions._doResult(data,response,actionName,message,status)