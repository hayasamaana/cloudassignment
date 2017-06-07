#!/usr/bin/env python3
import configparser as ConfigParser
from optparse import OptionParser

import pika

def callback(ch, method, props, body):
    print(" [x] Received '{}'".format(body))
    body = body.decode('utf-8')

    result = 'unknown message type' # default = fail
    if body.startswith("videoconvert::"):
      arg = body.split("::", 1)[1]
      if arg < 11:
        print(" [x]   - converting video '{}'".format(arg))
        result = "Finished without any trouble"

    print(" [x]   - done. result/reply: '{}'.".format(result))
    ch.basic_publish(exchange='',
                 routing_key=props.reply_to,
                 properties=pika.BasicProperties(correlation_id = props.correlation_id),
                 body=str(result))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def receive(connection_info=None):
    qname = "wasp"
    credentials = pika.PlainCredentials(
        connection_info["username"], connection_info["password"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        connection_info["server"], connection_info["port"], '/', credentials))
    channel = connection.channel()

    channel.queue_declare(queue=qname)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=qname)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--credential', dest='credentialFile',
                      default="./credentials.txt",
                      help='Path to CREDENTIAL file', metavar='CREDENTIALFILE')
    (options, args) = parser.parse_args()

    if options.credentialFile:
        config = ConfigParser.RawConfigParser()
        config.read(options.credentialFile)
        connection = {}
        connection["server"] = config.get('rabbit', 'server')
        connection["port"] = int(config.get('rabbit', 'port'))
        connection["queue"] = config.get('rabbit', 'queue')
        connection["username"] = config.get('rabbit', 'username')
        connection["password"] = config.get('rabbit', 'password')
        print("worker.py starting")
        receive(connection_info=connection)
    else:
        # e.g. python worker.py -c credentials.txt
        print("Syntax: 'python worker.py -h' | '--help' for help")
