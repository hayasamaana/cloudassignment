#!/bin/sh
python vmanager.py -c ../src/service/waspmq.sh -a create waspmq

while [ 1 ]
do
    b=$(python vmanager.py -a show-ip waspmq)
    echo $b
    if [ "$b" = "" ]
    then
            echo "IP not found"
    else
            echo "IP found"
            a="server="
            c="$a$b"
            awk -v var="$c" 'NR==3 {$0=var} 1' ../src/service/credentials-template.txt > ../src/service/credentials.txt
            git add ../src/service/credentials.txt
            git commit -m "new message queue (automatic commit!!!!)"
            git push
            exit
    fi
    sleep 5
done
