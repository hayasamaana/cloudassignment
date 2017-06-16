#!/usr/bin/env python
import pika
from optparse import OptionParser
import ConfigParser
import json
import StorageOperations
import time
#import subprocess

CONTAINERNAME = "VideoStorage"
DOWNLOADFOLDER = '/home/ubuntu/'

def getVideo(fileName):
    StorageOperations.download_file("Videos/"+fileName,CONTAINERNAME,DOWNLOADFOLDER)

def uploadVideo(uploadFile,fileName):
    StorageOperations.upload_file(DOWNLOADFOLDER+uploadFile,"ConvertedVideos/"+fileName,CONTAINERNAME)
    return StorageOperations.file_exists("ConvertedVideos/"+fileName,CONTAINERNAME)

def convertVideo(VideoName):
    time.sleep(10)
    success = True
    return success, VideoName
    # success = True
    # convertedVideo = ???
    # return success, convertedVideo

def callback(ch, method, properties, body):
    msg = json.loads(body)

    # check if message is a conversion request
    if not msg["type"] == "conversionRequest":
        print(" [x] Not a video conversion request")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return

    # download video file
    getVideo(msg["VideoName"])

    # convert video
    success, convertedVideoName = convertVideo(msg["VideoName"])
    if not success:
        print(" [x] Conversion failed")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return

    # upload converted video
    success = uploadVideo("Videos/"+convertedVideoName, msg["convertedVideoName"])
    if not success:
        print(" [x] Upload failed")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return

    print(" [x] Conversion request handled")
    ch.basic_ack(delivery_tag = method.delivery_tag)

def receive(connection_info=None):
    qname = "wasp"
    credentials = pika.PlainCredentials(connection_info["username"], connection_info["password"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(connection_info["server"],connection_info["port"],'/',credentials))
    channel = connection.channel()
    channel.queue_declare(queue=qname)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=qname, no_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__=="__main__":
    parser = OptionParser()
    parser.add_option('-c', '--credential', dest='credentialFile',default="../../etc/credentials/mq-credentials.txt", help='Path to CREDENTIAL file', metavar='CREDENTIALFILE')
    (options, args) = parser.parse_args()

    #subprocess.call("../../scripts/./swiftclient-credentials.sh", shell=True)

    if options.credentialFile:
        config = ConfigParser.RawConfigParser()
        config.read(options.credentialFile)
        connection = {}
        connection["server"] = config.get('rabbit', 'server')
        connection["port"] = int(config.get('rabbit', 'port'))
        connection["queue"] = config.get('rabbit', 'queue')
        connection["username"] = config.get('rabbit', 'username')
        connection["password"] = config.get('rabbit', 'password')
        receive(connection_info=connection)
    else:
        print("Syntax: 'python backend.py -h' | '--help' for help")
