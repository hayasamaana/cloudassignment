#!/bin/sh

# set hostname
sudo echo waspmq-frontend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-frontend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-pip
sudo apt-get install -y python-dev python-pip
#sudo apt-get install -y python-pika
sudo pip3 install flask==0.11.1
sudo pip3 install pika==0.10.0
export LC_ALL=C
sudo pip install python-novaclient==7.1.0
sudo pip install python-swiftclient

# prepare application directory
mkdir /var/www
cd /var/www

# clone repo
git clone https://github.com/perbostrm/cloudassignment.git

# update queue ip
#cd cloudassignment/scripts
#a="server="
#b=$(python vmanager.py -a show-ip waspmq)
#c="$a$b"
#awk -v var="$c" 'NR==3 {$0=var} 1' ../src/service/credentials.txt > ../src/service/credentials.txt

# launch app
#cd ../src/service
cd cloudassignment/src/service
python3 frontend.py
