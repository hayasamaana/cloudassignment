#!/bin/sh
num=$1
cd /home/ubuntu/cloudassignment/scripts/
python vmanager.py -a delete waspmq-backend$num
