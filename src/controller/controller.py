#!/usr/bin/python3
import configparser as ConfigParser
from optparse import OptionParser
import pika
import time

#sudo rabbitmqctl list_queues name messages messages_ready messages_unacknowledged | grep wasp

def queue_length(connection_info=None):
    # connection = pika.BlockingConnection(pika.ConnectionParameters(
    #             host='localhost',
    #             port=5672,
    #             credentials=pika.credentials.PlainCredentials('guest', 'guest'),
    #         )
    credentials = pika.PlainCredentials(
        connection_info["username"], connection_info["password"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        connection_info["server"], connection_info["port"], '/', credentials))
    channel = connection.channel()
    print(channel.queue_declare(queue="wasp", durable=False,  exclusive=False,
                      auto_delete=False,passive=True).method.message_count)

def run(connection_info=None):
    numberOfRequests = 1000
    for i in range(0,numberOfRequests):
        time.sleep(0.5)
        queue_length(connection_info)

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
        connection["username"] = config.get('rabbit', 'username')
        connection["password"] = config.get('rabbit', 'password')
        print("test.py starting")
        run(connection_info=connection)
    else:
        # e.g. python worker.py -c credentials.txt
        print("Syntax: 'python worker.py -h' | '--help'")
