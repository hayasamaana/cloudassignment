#!/bin/sh

# set hostname 
sudo echo waspmq-frontend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-frontend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-pip
#sudo apt-get install -y python-pika
sudo pip3 install flask
sudo pip3 install pika

# prepare application directory  
mkdir /var/www
cd /var/www

# echo "Cloning repo with WASP2"
git clone https://github.com/muyiibidun/WASP.git
git clone https://github.com/perbostrm/cloudassignment.git

