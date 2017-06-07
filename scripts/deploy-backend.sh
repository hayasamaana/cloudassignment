#!/bin/sh
python vmanager.py -c ../src/service/backend.sh -a create waspmq-backend

# update queue ip
#a="server="
#b=$(python vmanager.py -a show-ip waspmq)
#c="$a$b"
#awk -v var="$c" 'NR==3 {$0=var} 1' ../src/service/credentials.txt > ../src/service/credentials.txt
