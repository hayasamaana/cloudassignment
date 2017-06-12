#!/usr/bin/env python
from flask import Flask, jsonify
import pika, ConfigParser
from optparse import OptionParser
import uuid
import json
import StorageOperations

MODE_PERSISTENT_MSGS = 2
CONTAINERNAME = "VideoStorage"

class Connection:
    def __init__(self, connection_info=None):
        self.connection_info = connection_info
        print(self.connection_info)
        self.credentials = pika.PlainCredentials(
            self.connection_info["username"],
            self.connection_info["password"])
            
    def getConnection(self):
        qname = self.connection_info["queue"]
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            self.connection_info["server"],
            self.connection_info["port"],'/',
            self.credentials))
        channel = connection.channel()
        channel.queue_declare(queue=qname)
        return connection, channel

    def conversionRequest(self, message):
        connection, channel = self.getConnection()
        jsonmsg = json.dumps(message)
        channel.basic_publish(
            exchange='',
            routing_key=self.connection_info["queue"],
            body=jsonmsg,
            properties=pika.BasicProperties(delivery_mode = MODE_PERSISTENT_MSGS))
        print(" [x] Sent '%s'" % message)
        connection.close()

app = Flask(__name__)

def valid_keys():
    return ["1.avi","2.avi","3.avi","4.avi","5.avi","6.avi","7.avi" ]

@app.route("/")
def index():
    return "WASPMQ Microservices\n"

@app.route("/v1/waspmq", methods=["GET"])
def waspmq():
    return "WASPMQ Microservices\n"

@app.route("/convert/<VideoName>", methods=["GET"])
def conversionRequest(VideoName):
    if not VideoName in valid_keys():
        message = {
            'status': 400,
            'message': 'Invalid video name: ' + VideoName,
        }
        resp = jsonify(message)
        resp.status_code = 400
        return resp
    else:
        convertedVideoName = str(uuid.uuid4())+'-'+VideoName
        msg = {}
        msg["type"] = "conversionRequest"
        msg["VideoName"] = VideoName
        msg["convertedVideoName"] = convertedVideoName
        messenger.conversionRequest(msg)
        message = {
                'status': 202,
                'message': '/conversiondone/' + convertedVideoName,
        }
        resp = jsonify(message)
        resp.status_code = 202
        return resp

@app.route("/conversiondone/<VideoName>", methods=["GET"])
def conversionRequest(VideoName):
    if not StorageOperations.file_exists("ConvertedVideos/"+VideoName,CONTAINERNAME):
        message = {
            'status': 404,
            'message': 'Not found',
        }
        resp = jsonify(message)
        resp.status_code = 404
    else:
        message = {
            'status': 200,
            'message': 'conversion done',
        }
        resp = jsonify(message)
        resp.status_code = 200
    return resp


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--credential', dest='credentialFile',
                      default="../../etc/credentials/mq-credentials.txt",
                      help='Path to CREDENTIAL file', metavar='CREDENTIALFILE')
    (options, args) = parser.parse_args()
    if options.credentialFile:
        config = ConfigParser.RawConfigParser()
        config.read(options.credentialFile)
        connection = {}
        connection["server"] = config.get('rabbit', 'server')
        connection["port"] = int(config.get('rabbit', 'port'))
        connection["queue"] = config.get('rabbit', 'queue')
        connection["username"]=config.get('rabbit', 'username')
        connection["password"]=config.get('rabbit', 'password')

        messenger = Connection(connection_info=connection)

        #start application
        app.run(host="0.0.0.0", port=8000)

    else:
        #e.g. python frontend.py -c credentials.txt
        print("Syntax: 'python frontend.py -h' | '--help' for help")
