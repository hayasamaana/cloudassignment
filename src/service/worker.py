#!/usr/bin/env python3
import configparser as ConfigParser
from optparse import OptionParser
import time
import pika

def valid_keys():
    return ["1.avi","2.avi","3.avi","4.avi","5.avi","6.avi","7.avi" ]

def convertVideo(inputVideo):
    time.sleep(3)
    return True
    # success = True
    # convertedVideo = ???
    # return success, convertedVideo

def storeFile(file,path):
    return True

def getVideo(fileName):
    return

def callback(ch, method, props, body):
    print(" [x] Received '{}'".format(body))
    body = body.decode('utf-8')

    # check if message is a conversion request
    if not body.startswith("conversionRequest::"):
        print(" [x] Not a video conversion request")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return

    # download video file
    # filename = ???
    # inputVideo =  getVideo(filename)
    #
    # # convert video
    # # success, convertedVideo = convertVideo(inputVideo)
    # success = convertVideo(inputVideo)
    # if not success:
    #     print(" [x] Conversion failed")
    #     ch.basic_ack(delivery_tag = method.delivery_tag)
    #     return
    #
    # # upload converted video
    # # convertedPath = ???
    # # success = storeVideo(convertedVideo, convertedPath)
    # if not success:
    #     print(" [x] Storing failed")
    #     ch.basic_ack(delivery_tag = method.delivery_tag)
    #     return
    #
    # print(" [x] Conversion request handled")
    ch.basic_ack(delivery_tag = method.delivery_tag)


# def oldcallback(ch, method, props, body):
#     print(" [x] Received '{}'".format(body))
#     body = body.decode('utf-8')
#
#     result = 'unknown message type' # default = fail
#     if body.startswith("videoconvert::"):
#         arg = body.split("::", 1)[1]
#         if arg in valid_keys():
#             print(" [x]   - converting video '{}'".format(arg))
#             result = "Finished without any trouble"
#
#     print(" [x]   - done. result/reply: '{}'.".format(result))
#     ch.basic_publish(exchange='',
#                  routing_key=props.reply_to,
#                  properties=pika.BasicProperties(correlation_id = props.correlation_id),
#                  body=str(result))
#     ch.basic_ack(delivery_tag = method.delivery_tag)

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
        print("worker.py starting")
        receive(connection_info=connection)
    else:
        # e.g. python worker.py -c credentials.txt
        print("Syntax: 'python worker.py -h' | '--help' for help")
