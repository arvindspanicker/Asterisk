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


Add an extension for receiving the calls.
Go to extensions_custom.conf
(file location: /etc/asterisk/)

Example of extension for  calls:

exten => 3003,1,NoOp()
 same =>      n,Answer()
 same =>      n,Stasis(hello-world)
 same =>      n,Hangup()


</b> Note: External contact details should be stored in contat manager - external <b>
<b> Also, the contacts that are not saved in the asterisk will be saved with 'unassigned' <br>
for first name, last name and email since the api doesn't allow empty strings </b>

To make sure the statis up and running, try the following command from the system
where the python script would be running :

wscat -c "ws://ipaddressofasterisk:8088/ari/events?api_key=<username_of_registered_restuser>:password&app=statis-app-name-in-python-script"
</pre>

<h2>Installing the application</h2> (with all dependencies)
Execute  <b>./install_redhat.sh</b> to install the application (for redhat operating system - asterisk)
<b>Or<b>
Execute  <b>./install_ubuntu-16.04.sh</b> to install the application (for Ubuntu-16.04 operating system)

<h3>Running the application</h3>
Execute <b>./run.sh</b> to run the application

To test, 
call 3003 extension

<h3>Configuration File</h3>
<pre>
Inside [ari-config]
ARI_IP - IP Address of the PBX's Asterisk Rest Interface
ARI_PORT - Port Address of the PBX's Asterisk Rest Interface
ARI_USERNAME - The registered REST Interface User Name
ARI_PASSWORD= - The registered REST Interface User Password
STATIS_APP_NAME - Name of the Statis App 

<b>Note</b>: The same app name should be given in the extensions for receiving the event.

Inside [db-config]
DB_IP - IP Address of the Database
DB_USERNAME - Database Username
DB_PASSWORD - Database Password
DB_NAME - Database Name
DB_FIELD_FNAME - Field name specified in the database for the first name of the user
DB_FIELD_LNAME - Field name specified in the database for the last name of the user
DB_FIELD_EMAIL - Field name specified in the database for the email of the user
DB_FIELD_PHONE - Field name specified in the database for the account of the user
DB_FIELD_ENTRYID=entryid
DB_FIELD_ID - Field name specified in the database for the id label for the table that stores the name details
DB_FIELD_IGNORE_NUMBER - Field name specified in the database for the number field stored for ignore numbers
DB_TABLE_NAME_FOR_GROUP - Table name specified in the database for group entries 
DB_TABLE_NAME_FOR_NUMBER - Table name specified in the database for number details 
DB_TABLE_NAME_FOR_EMAIL - Table name specified in the database for the email details 
DB_IGNORE_TABLE_NAME- Table name for the contacts for the hubspot to ignore
 

Inside [hubspot-config]
HUBSPOT_API_KEY - API Key optained from the Hubspot Account
APP_NAME - App Name registered in the Hubspot Account
CHANNEL_ID_PROPERTY_LABEL - Label for channel id for the contacts in hubspot

Inside [logfile-config]
SIZE - Size of the log file
BACKUPCOUNT - Number of log files to be kept
LOGGERNAME - Name for the Logger
MODE - Different Modes for Logs : DEBUG,INFO,CRITICAL,WARNING,ERROR





