import ari,time,urllib2,json,datetime,os
import mysql.connector as mariadb 
from hubspot.connection import APIKey, PortalConnection
from hubspot.contacts import Contact
from hubspot.contacts import save_contacts
from ConfigParser import ConfigParser
import logging
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime
from hubspot.contacts.lists import get_all_contacts
from hubspot.contacts.properties import Property, create_property, NumberProperty


class AsteriskListener:
    """
    Class that listens inbound phone calls from the internal PBX system (Asterisk with FreePBX 
    front-end) and saves the contact information to the HubSpot Contacts API
    """
    def __init__(self,log_file_name,conf_file_name):
        """
        Initializing class variables
        """
        self.log_file_name = os.path.join(os.getcwd(), log_file_name) 
        self.conf_file_name = os.path.join(os.getcwd(),conf_file_name)
        self.config = ConfigParser()
        self.config.read(conf_file_name)
        self.init_logger()
        self.init_lisener()

    def init_lisener(self):
        """
        Function to initialize all the ARI configuration and create a listening event
        """
        self.obtain_ari_config()
        self.client.on_channel_event('StasisStart', self.stasis_start_cb)
        self.client.on_channel_event('StasisEnd', self.stasis_end_cb)
        """
        create this app in the extensions for statis event to occur
        """
        self.client.run(apps=self.statis_app_name)

    def init_logger(self):
        """
        Function to initialize logging
        """
        self.file_size = int(self.config.get('logfile-config', 'SIZE'))
        self.back_up_count = int(self.config.get('logfile-config', 'BACKUPCOUNT'))
        self.logger_name = self.config.get('logfile-config', 'LOGGERNAME')
        self.log_mode = self.config.get('logfile-config', 'MODE')
        self.logger = logging.getLogger(self.logger_name)
        if self.log_mode == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        elif self.log_mode == 'ERROR':
            self.logger.setLevel(logging.ERROR)
        elif self.log_mode == 'INFO':
            self.logger.setLevel(logging.INFO)
        elif self.log_mode == 'CRITICAL':
            self.logger.setLevel(logging.CRITICAL)
        elif self.log_mode == 'WARNING':
            self.logger.setLevel(logging.WARNING)
        elif self.log_mode == 'NOTSET':
            self.logger.setLevel(logging.NOTSET)
        else:
            raise Exception('Logging Mode is not Set')
        self.handler = RotatingFileHandler(self.log_file_name,maxBytes=self.file_size, \
        backupCount=self.back_up_count)
        self.formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s",\
        "%Y-%m-%d %H:%M:%S")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def obtain_ari_config(self):
        """
        Function to get the configuration of ARI from the config file
        """
        try:
            self.logger.debug('Inside obtain_ari_config() function')      
            self.ari_host = self.config.get('ari-config', 'ARI_IP')
            self.ari_port = self.config.get('ari-config', 'ARI_PORT')
            self.ari_username = self.config.get('ari-config','ARI_USERNAME')
            self.ari_password = self.config.get('ari-config','ARI_PASSWORD')
            self.statis_app_name = self.config.get('ari-config','STATIS_APP_NAME')
            self.client = ari.connect('{0}:{1}/'.format(self.ari_host,self.ari_port)\
            ,self.ari_username,self.ari_password)
        except Exception as e:
            self.logger.exception("Error while obtaining ARI configuration {}".\
            format(e.message))


    def obtain_db_config(self):
        """
        Function to obtain all the database configurations from the configuration file
        """
        try:
            self.logger.debug('Inside obtain_db_config() function')
            self.db_host = self.config.get('db-config', 'DB_IP', '127.0.0.1')
            self.db_username = self.config.get('db-config','DB_USERNAME')
            self.db_password = self.config.get('db-config','DB_PASSWORD')
            self.db_name = self.config.get('db-config','DB_NAME')
            self.fname = self.config.get('db-config','DB_FIELD_FNAME')
            self.lname = self.config.get('db-config','DB_FIELD_LNAME')
            self.email = self.config.get('db-config','DB_FIELD_EMAIL')
            self.phone = self.config.get('db-config','DB_FIELD_PHONE')
            self.group_table = self.config.get('db-config','DB_TABLE_NAME_FOR_GROUP')
            self.email_table = self.config.get('db-config','DB_TABLE_NAME_FOR_EMAIL')
            self.number_table = self.config.get('db-config','DB_TABLE_NAME_FOR_NUMBER')
            self.ignore_table = self.config.get('db-config','DB_IGNORE_TABLE_NAME')
            self.entryid = self.config.get('db-config','DB_FIELD_ENTRYID')
            self.id = self.config.get('db-config','DB_FIELD_ID')
            self.ignore_phone = self.config.get('db-config','DB_FIELD_IGNORE_NUMBER')
        except Exception as e:
            self.logger.exception("Error while obtaining DB configuration. {}".\
            format(e.message))


    def obtain_hubspot_config(self):
        """
        function to obtain all the configurations for the Hubspot API from the configuration file
        """
        try:
            self.logger.debug('Inside obtain_hubspot_config() function')
            self.api_key = self.config.get('hubspot-config', 'HUBSPOT_API_KEY')
            self.app_name = self.config.get('hubspot-config','APP_NAME')
            self.hubspot_property_label = self.config.get('hubspot-config','CHANNEL_ID_PROPERTY_LABEL')
        except Exception as e:
            self.logger.exception("Error while obtaining Hubspot configuration. {}".\
            format(e.message))    

    
    def fetch_from_db(self):
        """
        Fetch from the database for the email and all the other details based on 
        the number 
        """
        try:
            label = 'unassigned'
            time_label = datetime.now().strftime('%Y%m%d%H%M%S%f')
            email_label = label + '@' + time_label + '.com'
            sql_command = 'select {entryid} from {table} where {number} = {pnumber}'.\
            format(pnumber=self.phone_number,entryid=self.entryid,table=self.number_table,\
            number=self.phone)
            self.crsr.execute(sql_command)
            ans = self.crsr.fetchone()
            if not ans:
                self.first_name = str(self.phone_number)
                self.last_name = label
                self.email = email_label
                raise Exception('User With Number : {} Does Not Exist in Database'.\
                format(self.phone_number))
            else:
                entry_id = ans[0]
                sql_command = 'select {fname},{lname} from {table} where {id} = {entry_id};'.\
                format(entry_id=entry_id,fname=self.fname,lname=self.lname,table=self.group_table,\
                id=self.id)
                self.crsr.execute(sql_command)
                answer = self.crsr.fetchone()

                self.first_name = answer[0] if (answer[0] is not None and ans[0] != '') else \
                str(self.phone_number)
                self.last_name = answer[1] if (answer[1] is not None and ans[0] != '') else label

                sql_command = 'select {email} from {table} where {entryid} = {id};'.\
                format(entryid=self.entryid,table=self.email_table,email=self.email,id=entry_id)
                self.crsr.execute(sql_command)
                answer = self.crsr.fetchone()
                self.email = answer[0] if (answer[0] is not None and ans[0] != '') else email_label
        except Exception as e:
            self.logger.exception("Error fetching user data from DB. {}".format(e.message))


    def check_ignore_table(self):
        """
        Functin to check if the calling number is inside the ignore contact table specified 
        in the config file.
        If present, ignores the call to saving the contact to hubspot api
        else, fetches the contact from the database saves it to the 
        hubspot account configured in the conf file  
        """
        try:
            self.logger.debug('Inside check_ignore_table() function')
            self.obtain_db_config()
            self.connection = mariadb.connect(host = self.db_host, user = self.db_username, \
            password = self.db_password, database = self.db_name)
            sql_command = "SELECT {pnumber} from {table} where {pnumber} = \
            {phone_number}".format(phone_number=self.phone_number,pnumber=self.ignore_phone,\
            table=self.ignore_table)
            self.crsr = self.connection.cursor()
            self.crsr.execute(sql_command)
            ans = self.crsr.fetchall()
            if not ans:
                self.fetch_from_db()
                self.save_contact_to_hub() 
            else:
                raise Exception('Ignoring Contact {number} because it\'s in table {table}.'.\
                format(number=self.phone_number,table=self.ignore_table)) 
        except Exception as e:
            self.logger.exception("Error fetching number from the ignore contact table. {}".\
            format(e.message))

    def save_contact_to_hub(self):
        """
        Calls hubspot api and created a contact (if not exists) and saves it to 
        the HubSpot Account registered 
        """
        try:
            self.logger.debug('Inside save_contact_to_hub() function')
            self.vid = self.phone_number
            self.logger.debug("Saving contact to hub {}{}{}{}{}".format(self.vid,self.first_name,\
            self.last_name,self.email,self.phone_number))
            with PortalConnection(self.authentication_key, self.app_name) as connection:
                for contact in get_all_contacts(connection,property_names=('phone',)):
                    if 'unassigned' in contact.email_address and \
                    'unassigned' in self.email:
                        raise Exception('Contact {} already saved in hubspot'.\
                        format(self.phone_number))
                contact = []
                contact.append(Contact(vid=self.vid, email_address=self.email, \
                properties={u'lastname':self.last_name, u'firstname': \
                self.first_name,u'phone':str(self.phone_number),u'channelid':str(self.channel_id)},))
                save_contacts(contact,connection)
        except Exception as e:
            self.logger.exception("Error saving contact to Hubspot. {}".format(e.message))
    
    def create_hubspot_property(self):
        """
        To create the property called channel id to save the channel id of the
        caller to hubspot contacts
        """
        try:
            self.logger.debug('Inside create_hubspot_property() function')
            self.obtain_hubspot_config()
            self.authentication_key = APIKey(self.api_key)
            with PortalConnection(self.authentication_key, self.app_name) as connection:
                property_ = NumberProperty(name='channelid',label=self.hubspot_property_label,\
                description='channel id of asterisk call',field_widget=u'text',\
                group_name=u'contactinformation')
                prop = create_property(property_,connection)
        except Exception as e:
            self.logger.exception("Error while creating Hubspot property. {}".format(e.message))

    def stasis_end_cb(self,channel, ev):
        """
        Handler for StasisEnd event
        When caller cuts the call 
        """
        try:
            self.logger.debug('Inside stasis_end_cb() function')
            print("Channel %s just left our application" % self.channel.get('name'))
        except Exception as e:
            self.logger.exception("Error while executing statis_end_cd. {}".format(e.message))


    def stasis_start_cb(self,channel_obj, ev):
        """
        Handler for StasisStart event
        When caller starts the call 
        """
        try:
            self.logger.debug('Inside stasis_start_cb() function')
            self.ch = channel_obj.get('channel')
            self.channel = ev.get('channel')
            self.caller_name = self.channel.get('caller').get('name')
            self.phone_number = self.channel.get('caller').get('number')
            self.channel_id = self.channel.get('id')
            self.logger.debug('Call from Phone Number {}'.format(self.phone_number))
            self.create_hubspot_property()
            self.check_ignore_table()
            """
            continue back to the dial plan
            """
            self.ch.continueInDialplan() 
        except Exception as e:
            self.logger.exception("Error while getting channel event. {}".format(e.message))



if __name__ == "__main__":
    log_file_name = 'Handler.log'
    conf_file_name = 'handler.conf'
    asterisk_lisener = AsteriskListener(log_file_name,conf_file_name)

