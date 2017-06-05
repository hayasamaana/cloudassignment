#!/bin/sh

# set hostname 
sudo echo waspmq-frontend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-frontend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python-dev
sudo apt-get install -y python-pip
sudo apt-get install -y python-pika



# install python Flask web framework
sudo pip install Flask
sudo pip3 install flask

# prepare application directory  
mkdir /var/www
cd /var/www

#"Cloning our Cloud repo"
git clone https://github.com/perbostrm/cloudassignment.git
git clone https://github.com/muyiibidun/WASP.git

