# coding=utf-8
#------------------------------------------------------------------------------------------------------
# TDA596 Labs - Server Skeleton
# server/server.py
# Input: Node_ID total_number_of_ID
# Student Group:
# Student names: John Doe & John Doe
#------------------------------------------------------------------------------------------------------
# We import various libraries
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler # Socket specifically designed to handle HTTP requests
import sys # Retrieve arguments
from urlparse import parse_qs # Parse POST data
from httplib import HTTPConnection # Create a HTTP connection, as a client (for POST requests to the other vessels)
from urllib import urlencode # Encode POST content into the HTTP header
from codecs import open # Open a file
from threading import  Thread # Thread Management
#------------------------------------------------------------------------------------------------------

import os
# Global variables for HTML templates
board_frontpage_footer_template = 'board_frontpage_footer_template.html'
board_frontpage_header_template =  'board_frontpage_header_template.html'
boardcontents_template = 'boardcontents_template.html'
entry_template = 'entry_template.html'

#------------------------------------------------------------------------------------------------------
# Static variables definitions
PORT_NUMBER = 80

# Added global variables
client_base_path = '/board'
server_base_path = '/relay'
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------

# Store will look something like the following
# A dictionary with the key as an integer and a value as a dictionary
# in the value we will want to hold 1. the entry 2. the clock count 3. board who sent entry 
# ex., [{'entry': 'hi','clock': 1, 'sender': 10}, {'entry': 'hello', 'clock': 1, 'sender': 5}]


#------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
#------------------------------------------------------------------------------------------------------
    def __init__(self, server_address, handler, node_id, vessel_list):
    # We call the super init
        HTTPServer.__init__(self,server_address, handler)
        # we create the dictionary of values
        self.store = []
        # We keep a variable of the next id to insert
        self.current_key = -1
        # our own ID (IP is 10.1.0.ID)
        self.vessel_id = vessel_id
        # The list of other vessels
        self.vessels = vessel_list
        self.clock = 0
#------------------------------------------------------------------------------------------------------
    # We add a value received to the store
    def add_value_to_store(self, data):
        self.current_key += 1
        value = {}
        value['entry'] = data['entry'][0]
        value['clock'] = data['clock'][0]
        value['sender'] = data['sender'][0]
        self.store.append({self.current_key: value})
        self.sort_store()

    def sort_store(self):
        # We sort the messages based on logical clock values first and if there is a tie, we use IP address
        # The UI will later assign ids to these messages but the ids will hold no real significant values
        # except to display which position the message is at.
        self.store = sorted(self.store, key = lambda x: (x['clock'], x['sender']))
        
#------------------------------------------------------------------------------------------------------
    # We modify a value received in the store
    # TODO we need to change this function to take an index in and then we modify the message at that index
    def modify_value_in_store(self, key, value):
        self.store[key] = value
        self.sort_store()
#------------------------------------------------------------------------------------------------------
    # We delete a value received from the store
    # TODO we need to change this function to take an index in and delete it at that index
    def delete_value_in_store(self, key):
        if key in self.store:
            del self.store[key]
        self.sort_store()
#------------------------------------------------------------------------------------------------------
# Contact a specific vessel with a set of variables to transmit to it
    def contact_vessel(self, vessel, path, data):
        # the Boolean variable we will return
        success = False

        post_content = urlencode(data)
        # the HTTP header must contain the type of data we are transmitting, here URL encoded
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        # We should try to catch errors when contacting the vessel
        try:
            # We contact vessel:PORT_NUMBER since we all use the same port
            # We can set a timeout, after which the connection fails if nothing happened
            connection = HTTPConnection("%s:%d" % (vessel, PORT_NUMBER), timeout = 30)
            # We only use POST to send data (PUT and DELETE not supported)
            action_type = "POST"
            # We send the HTTP request
            connection.request(action_type, path, post_content, headers)
            # We retrieve the response
            response = connection.getresponse()
            # We want to check the status, the body should be empty
            status = response.status
            # If we receive a HTTP 200 - OK
            if status == 200:
                success = True
                print('Success on sending post to: {0}'.format(vessel))
            else:
                print('Something went wrong contacting: {0}'.format(vessel))
        # We catch every possible exceptions
        except Exception as e:
            print "Error while contacting %s" % vessel
            # printing the error given by Python
            print(e)

        # we return if we succeeded or not
        return success
#------------------------------------------------------------------------------------------------------
    # We send a received value to all the other vessels of the system
    def propagate_value_to_vessels(self, path, data):
        # We iterate through the vessel list
        for vessel in self.vessels:
            # We should not send it to our own IP, or we would create an infinite loop of updates
            if vessel != ("10.1.0.%s" % self.vessel_id):
                # A good practice would be to try again if the request failed
                # Here, we do it only once
                self.contact_vessel(vessel, path, data)
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# This class implements the logic when a server receives a GET or POST request
# It can access to the server data through self.server.*
# i.e. the store is accessible through self.server.store
# Attributes of the server are SHARED accross all request hqndling/ threads!
class BlackboardRequestHandler(BaseHTTPRequestHandler):
#------------------------------------------------------------------------------------------------------
    # We fill the HTTP headers
    def set_HTTP_headers(self, status_code = 200):
         # We set the response status code (200 if OK, something else otherwise)
        self.send_response(status_code)
        # We set the content type to HTML
        self.send_header("Content-type","text/html")
        # No more important headers, we can close them
        self.end_headers()
#------------------------------------------------------------------------------------------------------
    # a POST request must be parsed through urlparse.parse_QS, since the content is URL encoded
    def parse_POST_request(self):
        post_data = ""
        # We need to parse the response, so we must know the length of the content
        length = int(self.headers['Content-Length'])
        # we can now parse the content using parse_qs
        post_data = parse_qs(self.rfile.read(length), keep_blank_values=1)
        # we return the data
        return post_data
#-----------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Request handling - GET
#------------------------------------------------------------------------------------------------------
    # This function contains the logic executed when this server receives a GET request
    # This function is called AUTOMATICALLY upon reception and is executed as a thread!
    def do_GET(self):
        print("Receiving a GET on path %s" % self.path)
        # Here, we should check which path was requested and call the right logic based on it
        self.do_GET_Index()
#------------------------------------------------------------------------------------------------------
# GET logic - specific path
#------------------------------------------------------------------------------------------------------
    def do_GET_Index(self):
        # We set the response status code to 200 (OK)
        self.set_HTTP_headers(200)

        # Build board title
        board_title = 'Blackboard {0}'.format(self.server.vessel_id)

        # Build message entries
        entry_fo = list(open(os.path.join(os.getcwd(), "server", entry_template), 'r'))
        entry_template_string = '\n'.join(entry_fo)
        entries_string = ''
        count = 0
        for key in self.server.store:
            path = client_base_path + '/' + str(count)
            entry = entry_template_string % (path, count, self.server.store[count]['entry']) + '\n'
            entries_string += entry
            count += 1

        # Turn the lines into strings (necessary to make the html work)
        header_string = '\n'.join(header_fo)
        body_string = '\n'.join(body_fo) % (board_title, entries_string)  # Format in the title and entries
        footer_string = '\n'.join(footer_fo) % ('Gabriel Wagner & Lucas Nordmeyer')  # Format in the authors

        # Concatenate the different parts of the html page
        html_response = '{0}\n{1}\n{2}'.format(header_string, body_string, footer_string)

        self.wfile.write(html_response)
#------------------------------------------------------------------------------------------------------
    # we might want some other functions
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Request handling - POST
#------------------------------------------------------------------------------------------------------
    def do_POST(self):
        print("Receiving a POST on %s" % self.path)
        self.set_HTTP_headers(200)
        # Here, we should check which path was requested and call the right logic based on it
        # We should also parse the data received
        # and set the headers for the client

        data = self.parse_POST_request()

        # Path should be /base/ID
        path_parts = self.path[1:].split('/')
        try:
            base = path_parts[0]
            if base == client_base_path[1:]:
                if len(path_parts) > 1:
                    # A post containing an ID (delete/modify)
                    entry_id = int(path_parts[1])
                    self.handle_user_entry(data, entry_id)
                else:
                    self.handle_user_entry(data)
            elif base == server_base_path[1:]:
                if len(path_parts) > 1:
                    # A post containing an ID (delete/modify)
                    entry_id = int(path_parts[1])
                    self.handle_entry(data,  entry_id)
                else:
                    self.handle_entry(data)
        except IndexError:
            print('Incorrect path formatting, should be /path/ID')
            print('Your path was: {0}'.format(self.path))
        except ValueError:
            print('Wrong type of ID, should be integer')
            print('Your ID was: {0}'.format(path_parts[1]))
        return
#------------------------------------------------------------------------------------------------------
# POST Logic
#------------------------------------------------------------------------------------------------------
    # We might want some functions here as well
#------------------------------------------------------------------------------------------------------
    def handle_user_entry(self, data, entry_id=None):
        # Method for handling entry and retransmitting

        data['sender'] = [self.server.vessel_id]
        data['clock'] = [self.server.clock]

        # Handle the new data locally
        self.handle_entry(data, entry_id)

        # Create the new path
        if entry_id is not None:
            # Delete / Modify
            path = server_base_path + '/' + str(entry_id)
        else:
            # New entry
            path = server_base_path

        # If we want to retransmit what we received to the other vessels
        retransmit = True # Like this, we will just create infinite loops!
        if retransmit:
            # do_POST send the message only when the function finishes
            # We must then create threads if we want to do some heavy computation
            # Random content
            thread = Thread(target=self.server.propagate_value_to_vessels,args=(path, self.reformat_data(data)))
            # We kill the process if we kill the server
            thread.daemon = True
            # We start the thread
            thread.start()

    def handle_entry(self, data, entry_id=None):
        keys = list(data.keys())

        # We assume that every request has a clock value associated with it
        # New message's clock is greater than ours

        print data

        message_clock = int(data["clock"][0])
        if self.server.clock < message_clock:
            self.server.clock = message_clock + 1
        else:
            self.server.clock += 1
        # Operate as usual
        if 'delete' in keys and entry_id is not None:
            delete_flag = data['delete'][0]
            if delete_flag == '1':
                print('Deleting value at: {0}'.format(entry_id))
                self.server.delete_value_in_store(entry_id)
            else:
                print('Modifying value at {0}'.format(entry_id))
                self.server.modify_value_in_store(entry_id, data['entry'][0])
        else:
            print('Adding value!')
            self.server.add_value_to_store(data)

    def reformat_data(self, data):
        return_dict = {}
        for key in data:
            return_dict[key] = data[key][0]
        return return_dict

    
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':
    ## read the templates from the corresponding html files
    # .....
    # Open the html files
    # use ,"server" to run the lab1.py file 
    folder = os.path.join(os.getcwd(),"server", "")
    header_fo = list(open(folder + board_frontpage_header_template, 'r'))
    body_fo = list(open(folder + boardcontents_template, 'r'))
    footer_fo = list(open(folder + board_frontpage_footer_template, 'r'))

    vessel_list = []
    vessel_id = 0
    # Checking the arguments
    if len(sys.argv) != 3: # 2 args, the script and the vessel name
        print("Arguments: vessel_ID number_of_vessels")
    else:
        # We need to know the vessel IP
        vessel_id = int(sys.argv[1])
        # We need to write the other vessels IP, based on the knowledge of their number
        for i in range(1, int(sys.argv[2])+1):
            vessel_list.append("10.1.0.%d" % i) # We can add ourselves, we have a test in the propagation

    # We launch a server
    server = BlackboardServer(('', PORT_NUMBER), BlackboardRequestHandler, vessel_id, vessel_list)
    print("Starting the server on port %d" % PORT_NUMBER)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Stopping Server")
#------------------------------------------------------------------------------------------------------
