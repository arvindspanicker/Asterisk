import ari,time,urllib2,json,datetime
# import sqlite3
# import MySQLdb
from hubspot.connection import APIKey, PortalConnection
from hubspot.contacts import Contact
from hubspot.contacts import save_contacts
from ConfigParser import ConfigParser
import logging,time
from logging.handlers import RotatingFileHandler




class AsteriskListener:
    '''
    Class that listens inbound phone calls from the internal PBX system (Asterisk with FreePBX front-end) 
    and saves the contact information to the HubSpot Contacts API
    '''
    def __init__(self,log_file_name,conf_file_name):
        '''
        Initializing class variables
        '''
        self.log_file_name = log_file_name
        self.conf_file_name = conf_file_name
        self.config = ConfigParser()
        self.config.read(conf_file_name)
        self.init_logger()
        self.init_lisener()

    def init_lisener(self):
        '''
        function to initialize all the ARI configuration and create a listening event
        '''
        self.obtain_ari_config()
        self.client.on_channel_event('StasisStart', self.stasis_start_cb)
        self.client.on_channel_event('StasisEnd', self.stasis_end_cb)
        '''
        create this app in the extensions for statis event to occur
        '''
        self.client.run(apps=self.statis_app_name)

    def init_logger(self):
        '''
        function to initialize logging
        '''
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
        self.formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%Y-%m-%d %H:%M:%S")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def obtain_ari_config(self):
        '''
        function to get the configuration of ARI from the config file
        '''
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
            self.logger.exception("Error while obtaining ARI configuration {}".format(e.message))


    def obtain_db_config(self):
        '''
        function to obtain all the database configurations from the configuration file
        '''
        try:
            self.logger.debug('Inside obtain_db_config() function')
            self.db_host = self.config.get('db-config', 'DB_IP', '127.0.0.1')
            self.db_username = self.config.get('db-config','DB_USERNAME')
            self.db_password = self.config.get('db-config','DB_PASSWORD')
            self.db_name = self.config.get('db-config','DB_NAME')
            self.fname = self.config.get('db-config','DB_FIELD_FNAME')
            self.lname = self.config.get('db-config','DB_FIELD_LNAME')
            self.email = self.config.get('db-config','DB_FIELD_EMAIL')
        except Exception as e:
            self.logger.exception("Error while obtaining DB configuration. {}".format(e.message))


    def obtain_hubspot_config(self):
        '''
        function to obtain all the configurations for the Hubspot API from the configuration file
        '''
        try:
            self.logger.debug('Inside obtain_hubspot_config() function')
            self.api_key = self.config.get('hubspot-config', 'HUBSPOT_API_KEY')
            self.app_name = self.config.get('hubspot-config','APP_NAME')
        except Exception as e:
            self.logger.exception("Error while obtaining Hubspot configuration. {}".format(e.message))    

    
    def fetch_from_db(self):
        '''
            fetch from the database for the email and all the other details based on the incoming name
            and number 
        '''
        try:
            self.logger.debug('Inside fetch_from_db() function')
            self.obtain_db_config()
            connection = MySQLdb.connect(self.db_host,self.db_username,self.db_password,self.db_name)
            '''
            uncomment below if you're using sqlite3 database and comment the above line
            '''
            # connection = sqllite3.connect(self.db_name)
            sql_command = "SELECT id,{fname},{lname},{email} from Contacts where pnumber = \
            {phone_number}".format(phone_number=phone_number,fname=fname,lname=lname,email=email)
            crsr = connection.cursor()
            crsr.execute(sql_command)
            ans= crsr.fetchone() 
            if len(ans):
                self.vid = ans[0]
                self.first_name = ans[1]
                self.last_name = ans[2]
                self.email = ans[3] 
            else:
                raise Exception('User Does Not Exist in Database') 
        except Exception as e:
            self.logger.exception("Error fetching user data from DB. {}".format(e.message))

    def save_contact_to_hub(self):
        ''' calls hubspot api and created a contact (if not exists) and saves it to 
            the HubSpot Account registered 
        '''
        try:
            self.logger.debug('Inside save_contact_to_hub() function')
            self.logger.debug("Saving contact to hub {}{}{}{}{}".format(self.vid,self.first_name,\
            self.last_name,self.email,self.phone_number))
            self.obtain_hubspot_config()
            authentication_key = APIKey(self.api_key)
            with PortalConnection(authentication_key, self.app_name) as connection:
                contact = []
                contact.append(Contact(vid=self.vid, email_address=unicode(self.email,'utf-8'), \
                properties={u'lastname':unicode(self.last_name,'utf-8'), u'firstname': \
                unicode(self.first_name,'utf-8'),u'phone':unicode(str(self.phone_number),'utf-8')},))
                save_contacts(contact,connection)
        except Exception as e:
            self.logger.exception("Error saving contact to Hubspot. {}".format(e.message))
    

    def stasis_end_cb(self,channel, ev):
        """Handler for StasisEnd event"""
        """When caller cuts the call """
        try:
            self.logger.debug('Inside stasis_end_cb() function')
            print "Channel %s just left our application" % self.channel.get('name')
        except Exception as e:
            self.logger.exception("Error while executing statis_end_cd. {}".format(e.message))


    def stasis_start_cb(self,channel_obj, ev):
        """Handler for StasisStart event"""
        """When caller starts the call """
        try:
            self.logger.debug('Inside stasis_start_cb() function')
            self.ch = channel_obj.get('channel')
            self.channel = ev.get('channel')
            self.caller_name = self.channel.get('caller').get('name')
            self.caller_number = self.channel.get('caller').get('number')
            self.channel_id = self.channel.get('id')
            self.logger.debug('Call from Phone Number {}'.format(self.caller_number))
            '''
            uncomment the following two lines to get connection to the established database
            '''
            # self.fetch_from_db()
            # self.save_contact_to_hub() 
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

