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
Tconv = 4.
Tmax = 12.

def queue_stats(connection_info=None):
    credentials = pika.PlainCredentials(
        connection_info["username"], connection_info["password"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        connection_info["server"], connection_info["port"], '/', credentials))
    channel = connection.channel()
    queueLen = channel.queue_declare(queue="wasp", durable=False,  exclusive=False,
                      auto_delete=False,passive=True).method.message_count

    actualNumberOfWorkers = channel.queue_declare(queue="wasp", durable=False,  exclusive=False,
                      auto_delete=False,passive=True).method.consumer_count
    return queueLen, actualNumberOfWorkers

def run(connection_info=None):
    timeOfLatestIncrease = 0.0
    nrWorkers = LOWEST_NR_OF_WORKERS
    trend = "default"
    while True :
        time.sleep(1)
        currQueue, actualNWorkers = queue_stats(connection_info)
        workerRef = int(min(HIGHEST_NR_OF_WORKERS,max(math.ceil((currQueue*Tconv)/Tmax),LOWEST_NR_OF_WORKERS)))
        #print("Worker ref: %i \n" %workerRef)
        controlError = workerRef - nrWorkers
        if (controlError > 0 and trend != "decreasing") or (controlError >= WORKER_THRESHOLD):
#            print("increasing number of workers")
            for i in range(1, controlError+1):
 #               print("deploying %s \n" %str(nrWorkers+i) )
                #Call the bash script for creating workers
                timeOfLatestIncrease = time.time()
                subprocess.call(INCREASE_SCRIPT+str(nrWorkers+i), shell=True)

            nrWorkers += controlError
            trend = "increasing"

        if (controlError < 0 and trend != "increasing") or (-controlError >= WORKER_THRESHOLD):
            if time.time()-timeOfLatestIncrease > 60*10.:
  #              print("decreasing the number of workers")
                for i in range(0, -controlError):
   #                 print("killingInTheNameOf")
                    #Call the bash script for deleting workers
                    subprocess.call(DECREASE_SCRIPT+str(nrWorkers-i), shell=True)
                nrWorkers += controlError
                trend = "decreasing"
        #print("Number of workers: %i \n " %nrWorkers)
        stats(currQueue, workerRef, nrWorkers, actualNWorkers)

def stats(queueLength,nRef,nBackends,actualnBackends):
    print('{}, {}, {}, {}, {}; ...'.format(time.time(),queueLength,nRef,nBackends,actualnBackends))

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
        print("%controller.py starting")
        print("%controllerStats = [time, queueLength, nRef, nBackends]")
        print("controllerStats = [ ...")
        run(connection_info=connection)
    else:
        # e.g. python worker.py -c credentials.txt
        print("Syntax: 'python worker.py -h' | '--help'")
