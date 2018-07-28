sudo apt-get install -y python2.7
sudo apt-get install -y python-pip python-dev
pip install virtualenv
virtualenv asterisk --python=python2.7
source asterisk/bin/activate
pip install -r requirements.txt

