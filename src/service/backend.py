#!/usr/bin/env python
import pika
from optparse import OptionParser
import ConfigParser
import json
import StorageOperations
import time
import os
import ffmpy
#import subprocess

CONTAINERNAME = "VideoStorage"
DOWNLOADFOLDER = '/home/ubuntu/'

def getVideo(fileName):
    StorageOperations.download_file("Videos/"+fileName,CONTAINERNAME,DOWNLOADFOLDER)

def uploadVideo(uploadFile,fileName):
    StorageOperations.upload_file(DOWNLOADFOLDER+uploadFile,"ConvertedVideos/"+fileName,CONTAINERNAME)
    return StorageOperations.file_exists("ConvertedVideos/"+fileName,CONTAINERNAME)

def convertVideo(videoName,convertedVideoName):
    try:
        ff = ffmpy.FFmpeg(
            inputs={DOWNLOADFOLDER+"Videos/"+videoName: None},
            outputs={DOWNLOADFOLDER+"Videos/"+convertedVideoName: None}
            )
        ff.run()
        success = True
    except:
        success = False
    return success

def callback(ch, method, properties, body):
    msg = json.loads(body)

    # check if message is a conversion request
    if not msg["type"] == "conversionRequest":
        print(" [x] Not a video conversion request")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return

    videoName = msg["VideoName"]
    convertedVideoName = msg["convertedVideoName"]

    # download video file
    getVideo(videoName)

    # convert video
    success = convertVideo(videoName, convertedVideoName)
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

    os.remove(DOWNLOADFOLDER+"Videos/"+videoName)
    os.remove(DOWNLOADFOLDER+"Videos/"+convertedVideoName)
    print(" [x] Conversion request handled")

    ch.basic_ack(delivery_tag = method.delivery_tag)

def receive(connection_info=None):
    qname = "wasp"
    credentials = pika.PlainCredentials(connection_info["username"], connection_info["password"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(connection_info["server"],connection_info["port"],'/',credentials))
    channel = connection.channel()
    channel.queue_declare(queue=qname)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=qname)
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
        success = False
        while not success :
            try:
                 receive(connection_info=connection)
                 success = True
            except:
                 print("Trying to connect again...")
    else:
        print("Syntax: 'python backend.py -h' | '--help' for help")
