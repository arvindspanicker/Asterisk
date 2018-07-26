sudo apt-get install -y python2.7
sudo apt-get install -y python-pip python-dev
pip install virtualenv
virtualenv asterisk --python=python2.7
source asterisk/bin/activate
pip install swaggerpy
pip install git+https://github.com/asterisk/ari-py.git
pip install hubspot-contacts

