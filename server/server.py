from handlers.dataHandler import Data
from handlers.requestHandler import requestHandler
from threading import Thread
from const import Constants
from flask import Flask, request, render_template
import requests

server = None
app = Flask(__name__, static_folder=Constants.FRONTEND_STATIC, template_folder=Constants.FRONTEND)

class Server():
    def __init__(self,host='0.0.0.0',port=6969,dataHandler:Data=None):
        #Start the hosting...
        self._data = dataHandler
        self._host = host
        self._port = 6969
        self._serve = False

    def start(self):
        if self._serve == False:
            self._thread = Thread(target=self._startFlaskApp, name="smartThermostatServer")
            self._thread.start()

    def isActive(self):
        return self._serve

    def _startFlaskApp(self):
        global server
        server = self
        self._serve = True
        try:
            app.run(port=server._port, host=server._host)
        except Exception as e:
            print(str(e))
        self._serve = False

    def stop(self):
        self._serve = False
        requests.get(f'http://localhost:{self._port}/kill') #Send kill command to the server


#Returns the frontend client
@app.route("/", methods=['GET'])
def client():
    return render_template('index.html')

@app.route("/kill", methods=['GET'])
def shutdown():
    if server._serve: return
    exit(0)

#Remove a port mapping rule
@app.route("/actions", methods=['POST'])
def action():
    reqHandler = requestHandler(request.get_json())
    reqHandler.performActions(server._data)
    return reqHandler.getResponse()