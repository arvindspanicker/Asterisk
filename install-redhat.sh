sudo yum install -y scl-utils
yum install -y  centos-release-scl-rh
sudo yum install -y python27
sudo yum install epel-release
sudo yum install python-pip -y
pip install --upgrade pip
pip install virtualenv
virtualenv asterisk --python=python2.7
source asterisk/bin/activate
pip install -r requirements.txt
