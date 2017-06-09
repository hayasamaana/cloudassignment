#!/bin/sh
python vmanager.py -c ../src/service/waspmq.sh -a create waspmq

while [ 1 ]
do
    b=$(python vmanager.py -a show-ip waspmq)
    echo $b
    if [ "$b" = "instance not found" ]
    then
            echo $b
    else
            echo "IP found"
            a="server="
            c="$a$b"
            awk -v var="$c" 'NR==3 {$0=var} 1' ../etc/credentials/mq-credentials-template.txt > ../etc/credentials/mq-credentials.txt
            git add ../etc/credentials/mq-credentials.txt
            git commit -m "new message queue (automatic commit!!!!)"
            git push
            exit
    fi
    sleep 5
done
