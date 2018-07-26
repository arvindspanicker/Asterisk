# Asterisk

<h3>Create Rest Interface User<h3>
First create a Rest Interface User
Add a user in the ari_additional.conf
(It is in /etc/asterisk/ )

Example of user in the above file:

[username]
type=user
password=1234
password_format=plain
read_only=no


Now add an extension.
Go to extensions_custom.conf
(It is in /etc/asterisk/)

Example of extension for  calls:

exten => 3003,1,NoOp()
 same =>      n,Answer()
 same =>      n,Stasis(hello-world)
 same =>      n,Hangup()


To make sure the statis up and running, try the following command from the system
where the python script would be running (remove '<' '>'):

wscat -c "ws://<ipaddressofasterisk>:8088/ari/events?api_key=<username_of_registered_restuser>:password&app=<statis-app-name-in-python-script>"


<h3>Installation</h3> (install all dependencies)
./install.sh

<h3>Run</h3>
./run.sh

To test, 
call 3003 extension




