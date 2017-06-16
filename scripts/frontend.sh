#!/bin/sh

# set hostname
sudo echo waspmq-frontend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-frontend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python-dev
sudo apt-get install -y python-pip
sudo apt-get install -y python-pika
sudo apt-get install -y python-flask
#sudo pip3 install flask==0.11.1
#sudo pip3 install pika==0.10.0
#sudo pip3 install statsd
export LC_ALL=C

#For upload and download to containers
sudo apt-get install -y python-swiftclient
sudo apt-get install -y python-keystoneclient

#Environment variables for swiftclient
# export ST_AUTH_VERSION=3
# export OS_USERNAME=ercx026
# export OS_PASSWORD=ercx026
# export OS_PROJECT_NAME=LiU-2
# export OS_USER_DOMAIN_NAME=xerces
# export OS_PROJECT_DOMAIN_NAME=xerces
# export OS_AUTH_URL=https://xerces.ericsson.net:5000/v3

# prepare application directory
mkdir /var/www
cd /var/www

# clone repo
git clone https://github.com/perbostrm/cloudassignment.git

# launch app
cd cloudassignment/src/service
#python frontend.py
