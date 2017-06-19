#!/bin/sh
num=$1
cd /home/ubuntu/cloudassignment/scripts/
python vmanager.py -c backend.sh -a create waspmq-backend$num
