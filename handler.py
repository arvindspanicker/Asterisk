import ari
import logging
import urllib2, json
#import sqllite3
from hubspot.connection import APIKey, PortalConnection
from hubspot.contacts import Contact
from hubspot.contacts import save_contacts
import datetime

'''
All errors are logged in a file called Handler.log
'''
logging.basicConfig(filename='Handler.log',level=logging.ERROR)
client = ari.connect('http://192.168.20.195:8088/', 'arvind', 'arvind')

def fetch_from_db(user_name, phone_number):
    try:
        '''
        fetch from the database for the email and all the other details based on the incoming name
        and number 
        '''
        # connection = MySQLdb.connect("localhost","testuser","test123","Contacts" )
        connection = sqllite3.connect('Contact.db')
        sql_command = "SELECT id,fname,lname,email from Contacts where uname = {user_name} and pnumber = \
        {phone_number}".format(user_name=user_name,phone_number=phone_number)
        crsr = connection.cursor()
        crsr.execute(sql_command)
        ans= crsr.fetchone() 
        if len(ans):
            return ans[0],ans[1],ans[2],ans[3] 
        else:
            logging.error('User Does Not Exist in Database')
    except Exception as e:
        logging.error(datetime.datetime.now()+e.message)

def save_contact_to_hub(vid,first_name,last_name,email,phone_number):
    ''' calls hubspot api and created a contact (if not exists) and saves it to 
        the HubSpot Account registered 
    '''
    try:
        authentication_key = APIKey("3dd24ad4-62c4-4d39-bacf-7616362648b2")
        with PortalConnection(authentication_key, "Test_App") as connection:
            contact = []
            contact.append(Contact(vid=vid, email_address=unicode(email,'utf-8'), \
            properties={u'lastname':unicode(last_name,'utf-8'), u'firstname': unicode(first_name,'utf-8'),\
            u'phone':unicode(phone_number,'utf-8')},))
            save_contacts(contact,connection)
    except Exception as e:
        logging.error(datetime.datetime.now()+e.message)
 

def stasis_end_cb(channel, ev):
    """Handler for StasisEnd event"""
    """When caller cuts the call """
    print "Channel %s just left our application" % channel.json.get('name')


def stasis_start_cb(channel_obj, ev):
    """Handler for StasisStart event"""
    """When caller starts the call """
    try:
        ch = channel_obj.get('channel')
        channel = ev.get('channel')
        caller_name = channel.get('caller').get('name')
        caller_number = channel.get('caller').get('number')
        channel_id = channel.get('id')
        print caller_name,caller_number,channel_id
	'''
	uncomment the following two lines to get connection to the established database
	'''
        # vid, first_name, last_name, email = fetch_from_db(caller_name, caller_number)
        # save_contact_to_hub(vid,first_name,last_name,email,str(caller_number)) 
        """
        continue back to the dial plan
        """
        ch.continueInDialplan() 
    except Exception as e:
        logging.error(datetime.datetime.now()+e.message)


client.on_channel_event('StasisStart', stasis_start_cb)
client.on_channel_event('StasisEnd', stasis_end_cb)

'create this app in the extensions for statis event to occur'
client.run(apps='hello-world')
