#!/bin/sh
num=$1
python vmanager.py -c ../src/service/backend.sh -a create waspmq-backend$num
