#!/bin/bash
APP_DIRECTORY=$(pwd)
yum install gcc
cd /usr/src
wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
tar xzf Python-2.7.10.tgz
cd Python-2.7.10
./configure
make altinstall
export PYTHONPATH="/usr/bin/python2.7"

yum --enablerepo=extras install -y  epel-release
sudo yum install -y python-pip
sudo yum install -y git
pip install virtualenv
cd $APP_DIRECTORY
virtualenv asterisk --python=python2.7
source asterisk/bin/activate
pip install -r requirements.txt



