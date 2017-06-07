#!/usr/bin/python

import threading
from random import randint
import time
import requests

class ClientThread(threading.Thread):
    def __init__(self, threadNumber):
        threading.Thread.__init__(self)
        self.setName('Thread ' + str(threadNumber))
        self.meanTimeBetweenRequests = 4
        self.numberOfVideos = 5
        self.request_url = 'http://172.16.0.8/wasp/v1/waspmq/convert/'

    def selectVideo(self):
        return randint(1,self.numberOfVideos)

    def requestConversion(self):
        videoNumber = self.selectVideo()
        print('%s: requesting conversion of video %d' % (self.getName(), videoNumber))
        timeStart = time.time()
        time.sleep(.01) # todo: remove
        r = requests.get(self.request_url + str(videoNumber))
        print(r.status_code)
        # todo: send HTTP GET to Frontend Web API

        timeEnd = time.time()
        print('%s: conversion done in %g seconds' % (self.getName(), timeEnd-timeStart))

    def run(self):
        time.sleep(.01) # todo, remove?
        numberOfRequests = 2
        for i in range(0,numberOfRequests):
            # Sleep for random time
            secondsToSleep = randint(1,2*self.meanTimeBetweenRequests)
            print('%s: sleeping for %d s' % (self.getName(), secondsToSleep))
            time.sleep(secondsToSleep)

            # Request conversion
            self.requestConversion()
        print('done')


if __name__ == '__main__':
    numberOfThreads = 2

    # Declare client threads
    threads = [ClientThread(i) for i in range(numberOfThreads)]

    # Start client threads
    for t in range(0,numberOfThreads):
        print('starting Thread %d' % t)
        threads[t].daemon = True;
        threads[t].start()

    # Wait for the threads to finish...
    while threading.active_count() > 1:
        time.sleep(0.1)

    print('Main terminating...')
