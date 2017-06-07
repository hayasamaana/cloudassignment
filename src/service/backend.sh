#!/bin/sh

# set hostname
sudo echo waspmq-backend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-backend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-pip
#sudo apt-get install -y python-pika
sudo pip3 install flask
sudo pip3 install pika

# prepare directory
mkdir /usr/local/
cd /usr/local/

# clone repo
git clone https://github.com/perbostrm/cloudassignment.git

# update queue ip
cd cloudassignment/scripts
a="server="
b=$(python vmanager.py -a show-ip waspmq)
c="$a$b"
awk -v var="$c" 'NR==3 {$0=var} 1' ../src/service/credentials.txt > ../src/service/credentials.txt

# launch app
cd ../src/service
python3 worker.py
