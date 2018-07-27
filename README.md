# Asterisk
Application for linking inbound phone calls from the internal PBX system (Asterisk with FreePBX front-end) to the HubSpot Contacts API. <br>
Please follow the steps below for setting up the application.<br>

<h3>Creating Rest Interface User</h3>
<pre>
For REST API Authentication, add an user in the ari_additional.conf
(file location: /etc/asterisk/ )

Sample:
[username]
type=user
password=<password>
password_format=plain
read_only=no
</pre>

Add an extension for receiving the calls.
Go to extensions_custom.conf
(file location: /etc/asterisk/)

Example of extension for  calls:

exten => 3003,1,NoOp()
 same =>      n,Answer()
 same =>      n,Stasis(hello-world)
 same =>      n,Hangup()


To make sure the statis up and running, try the following command from the system
where the python script would be running (remove '<' '>'):

wscat -c "ws://<ipaddressofasterisk>:8088/ari/events?api_key=<username_of_registered_restuser>:password&app=<statis-app-name-in-python-script>"

</pre>
<h2>Installing the application</h2> (with all dependencies)
./install.sh

<h3>Running the application</h3>
./run.sh

To test, 
call 3003 extension




