#!/usr/bin/python
import ConfigParser
from optparse import OptionParser
import pika
import time
import math
import subprocess

LOWEST_NR_OF_WORKERS = 2
HIGHEST_NR_OF_WORKERS = 10
WORKER_THRESHOLD = 2
INCREASE_SCRIPT = "../../scripts/./deploy-backend.sh "
DECREASE_SCRIPT = "../../scripts/./delete-backend.sh "
Tconv = 10
Tmax = 20

def queue_length(connection_info=None):
    credentials = pika.PlainCredentials(
        connection_info["username"], connection_info["password"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        connection_info["server"], connection_info["port"], '/', credentials))
    channel = connection.channel()
    queueLen = channel.queue_declare(queue="wasp", durable=False,  exclusive=False,
                      auto_delete=False,passive=True).method.message_count
    print(queueLen)
    return queueLen

def run(connection_info=None):
    nrWorkers = LOWEST_NR_OF_WORKERS
    while True :
        time.sleep(1)
        currQueue = queue_length(connection_info)
        workerRef = min(HIGHEST_NR_OF_WORKERS,max(math.ceil((currQueue*Tconv)/Tmax),LOWEST_NR_OF_WORKERS))
        controlError = workerRef - nrWorkers
        if (controlError) >= WORKER_THRESHOLD:
            print("increasing number of workers")
            for i in range(1, controlError+1):
                print("deploying")
                #Call the bash script for creating workers
                #subprocess.call(INCREASE_SCRIPT+str(nrWorkers+i), shell=True)
            nrWorkers += controlError

        if (-controlError >= WORKER_THRESHOLD):
            print("decreasing the number of workers")
            for i in range(1, -controlError+1):
                print("killingInTheNameOf")
                #Call the bash script for deleting workers
                #subprocess.call(DECREASE_SCRIPT+str(nrWorkers-i), shell=True)
            nrWorkers += controlError


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
