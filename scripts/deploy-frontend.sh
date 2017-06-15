#!/bin/sh
num=$1
python vmanager.py -c ../src/service/frontend.sh -a create waspmq-frontend$num
