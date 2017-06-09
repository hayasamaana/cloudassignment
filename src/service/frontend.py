#!/usr/bin/env python3
import configparser as ConfigParser
from optparse import OptionParser
import uuid
import time

from flask import Flask, g, jsonify
import pika

from statsd import StatsClient


MODE_PERSISTENT_MSGS = 2
TIMEOUT_SECONDS = 3600

class Connection:
    def __init__(self, connection_info=None):
        self.connection_info = connection_info
        self.credentials = pika.PlainCredentials(
            self.connection_info["username"], self.connection_info["password"])

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.connection_info["server"],
                                                  self.connection_info["port"], '/',
                                                  self.credentials))
        self.channel = self.connection.channel()

        # configure reply channel
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_reply, no_ack=True,
                                   queue=self.callback_queue)

    def on_reply(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def send_to_queue(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        qname = self.connection_info["queue"]
        self.channel.queue_declare(queue=qname)
        self.channel.basic_publish(exchange='',
                              routing_key=qname,
                              body=message,
                              properties=pika.BasicProperties(
                                delivery_mode = MODE_PERSISTENT_MSGS,
                                reply_to = self.callback_queue,
                                correlation_id = self.corr_id
                              ))
        print(" [x] Sent '%s'" % message)

        start_time = time.time()
        i = 0
        while self.response is None:
            i += 1
            if i > 100:
                i = 0
                now_time = time.time() - start_time
                if now_time > TIMEOUT_SECONDS:
                    print(" [x] timed out after {} seconds".format(TIMEOUT_SECONDS))
                    return 'error:timeout'

            self.connection.process_data_events()
            time.sleep(0.005) # block 5ms to avoid cpu overload
        print(" [x] Received reply '%s'" % self.response)
        return self.response

app = Flask(__name__)

def rabbitmq():
    if not hasattr(g, 'rabbitmq') or g.rabbitmq is None:
        g.rabbitmq = rabbitmq_connect()
    return g.rabbitmq

def rabbitmq_connect(filename="./credentials.txt"):
    config = ConfigParser.RawConfigParser()
    config.read(filename)
    connection = {}
    connection["server"] = config.get('rabbit', 'server')
    connection["port"] = int(config.get('rabbit', 'port'))
    connection["queue"] = config.get('rabbit', 'queue')
    connection["username"] = config.get('rabbit', 'username')
    connection["password"] = config.get('rabbit', 'password')
    print("Connection instantiated using '%s'" % filename)
    return Connection(connection_info=connection)

def valid_keys():
    return ["1.avi","2.avi","3.avi","4.avi","5.avi","6.avi","7.avi" ]

@app.route("/")
def index():
    return "WASPMQ Microservices\n"

@app.route("/v1/waspmq", methods=["GET"])
def waspmq():
    return jsonify("WASPMQ Microservices")

@app.route("/v1/waspmq/convert/<video_id>", methods=["GET"])
def videosend(video_id):
    if not video_id in valid_keys():
      r = jsonify("invalid video id: '{}'. valid values are: {}".format(video_id, [x for x in videodb.keys()]))
      r.status_code = 400
      return r
    else:
      resp = None
      statsd = StatsClient('127.0.0.1', 8125)
      with statsd.timer('webapi_convert.{}'.format(video_id)):
        resp = rabbitmq().send_to_queue("videoconvert::{}".format(video_id))
      return jsonify("video '{}' converted: '{}'".format(video_id, resp))

@app.route("/v1/waspmq/msg/<message>")
def send(message):
    rabbitmq().send_to_queue(message.replace("+", " "))
    return jsonify("Sent '%s'\n" % message.replace("+", " "))

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--credential', dest='credentialFile',
                      default="./credentials.txt",
                      help='Path to CREDENTIAL file', metavar='CREDENTIALFILE')
    (options, args) = parser.parse_args()

    if options.credentialFile:
        # start application
        app.run(host="0.0.0.0", port=8000)
    else:
        # e.g. python webapi.py -c credentials.txt
        print("Syntax: 'python webapi.py -h' | '--help' for help")
