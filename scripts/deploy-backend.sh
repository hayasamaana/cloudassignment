#!/bin/sh
num=$1
python vmanager.py -c backend.sh -a create waspmq-backend$num
