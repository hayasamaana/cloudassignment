#!/bin/sh

# set hostname
sudo echo waspmq-frontend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-frontend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-pip
sudo pip3 install flask==0.11.1
sudo pip3 install pika==0.10.0
sudo pip3 install statsd
export LC_ALL=C

# prepare application directory
mkdir /var/www
cd /var/www

# clone repo
git clone https://github.com/perbostrm/cloudassignment.git

# launch app
cd cloudassignment/src/service
python3 frontend.py
