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
import random
import time
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
server_update_board_path = '/update' # this will be the endpoint to tell the non-leader servers that a update occured
leader_election_path = '/elect'
leader_selection_path = '/setleader'
leader = None
#------------------------------------------------------------------------------------------------------




#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
#------------------------------------------------------------------------------------------------------
    def __init__(self, server_address, handler, node_id, vessel_list):
    # We call the super init
        HTTPServer.__init__(self,server_address, handler)
        # we create the dictionary of values
        self.store = {}
        # We keep a variable of the next id to insert
        self.current_key = -1
        # our own ID (IP is 10.1.0.ID)
        self.vessel_id = vessel_id
        # The list of other vessels
        self.vessels = vessel_list
       
        # Start a thread to elect a leader
        # We let every node start a leader election during the start up
        if self.vessel_id == 1:
            thread = Thread(target=self.start_leader_election,args=())
            # We kill the process if we kill the server
            thread.daemon = True
            # We start the thread
            thread.start()
#------------------------------------------------------------------------------------------------------
    # We add a value received to the store
    def add_value_to_store(self, value):
        self.current_key += 1
        self.store[self.current_key] = value
#------------------------------------------------------------------------------------------------------
    # We modify a value received in the store
    def modify_value_in_store(self,key,value):
        self.store[key] = value
#------------------------------------------------------------------------------------------------------
    # We delete a value received from the store
    def delete_value_in_store(self,key):
        if key in self.store:
            del self.store[key]

    # We need to update our dictionary to be the same as the leaders
    def update_store(self, data):
        self.store = data

    def get_store(self, data):
        return self.store

#------------------------------------------------------------------------------------------------------
# Contact a specific vessel with a set of variables to transmit to it
    def contact_vessel(self, vessel, path, data):
        # the Boolean variable we will return
        success = False

        # Encode the content
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
                # We do not want to send to the leader again
                if leader != self.vessel_id:
                    # A good practice would be to try again if the request failed
                    # Here, we do it only once
                    self.contact_vessel(vessel, path, data)

    def start_leader_election(self):
        # Sleep so that all other nodes are up and running to receive requests
        time.sleep(1)
        print "Vessel: %s is starting election" % self.vessel_id
        data = {}
        # We are starting the leader election process
        data["max"] = random.randint(1,11)
        data["leader"] = self.vessel_id # this is a string
        data["contributingNodes"] = 1

        print "starting election with max: %s, leader: %s, and startingNode: %s" % (str(data["max"]), self.vessel_id,self.vessel_id )
        # Tell the next node to do election
        self.contact_vessel("10.1.0.%d" % self.get_next_vessel(), leader_election_path, data)

    def get_next_vessel(self):
        return 1 if self.vessel_id == len(self.vessels) else vessel_id + 1
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

        # According to the python docs, this function will return a dict with a key as key and 
        # values as lists for some reason. 
        post_data = parse_qs(self.rfile.read(length), keep_blank_values=1)
        # we return the data
        return post_data
#------------------------------------------------------i-----------------------------------------------
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
        global leader
        # We set the response status code to 200 (OK)
        self.set_HTTP_headers(200)

        # Build board title
        board_title = ""
        if (leader is not None) and (leader != self.server.vessel_id):
            board_title = "Blackboard: %s connected to Leader: %s" % (self.server.vessel_id, leader)
        else:
            board_title = 'Blackboard: {0}'.format(self.server.vessel_id)

        # Build message entries
        entry_fo = list(open(os.path.join(os.getcwd(), "server", entry_template), 'r'))
        entry_template_string = '\n'.join(entry_fo)
        entries_string = ''
        for key in self.server.store:
            path = client_base_path + '/' + str(key)
            entry = entry_template_string % (path, key, self.server.store[key]) + '\n'
            entries_string += entry

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
            # client_base_path is "/board"
            if base == client_base_path[1:]:
                if len(path_parts) > 1:
                    # A post containing an ID (delete/modify)
                    entry_id = int(path_parts[1])
                    self.handle_user_entry(data, entry_id)
                else:
                    self.handle_user_entry(data)
            # server_base_path is "/relay"
            elif base == server_base_path[1:]:
                if len(path_parts) > 1:
                    # A post containing an ID (delete/modify)
                    entry_id = int(path_parts[1])
                    self.handle_entry(data,  entry_id)
                else:
                    self.handle_entry(data)
            # Leader election path is "/elect"
            elif base == leader_election_path[1:]:
                self.do_leader_election(data)
            elif base == leader_selection_path[1:]:
                self.do_set_leader(data)
            elif base == server_update_board_path[1:]:
                self.update_board(data)
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
        global leader

        # If we are the leader, we handle the POST as usual but if we send the data differently
        # to all the other clients, we will send a new dict for them to display, that way we
        # keep the global ordering consistent.
        if leader == self.server.vessel_id:
            # Method for handling entry and retransmitting
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
                
                # Get the board to send to the non-leaders
                centralized_store = self.server.get_store()
                thread = Thread(target=self.server.propagate_value_to_vessels,args=(path, centralized_store))
                # We kill the process if we kill the server
                thread.daemon = True
                # We start the thread
                thread.start()
        # Otherwise we pass the POST to the leader
        else:
            self.server.contact_vessel("10.1.0.%s" % leader, client_base_path, self.reformat_data(data))


    def handle_entry(self, data, entry_id=None):
        keys = list(data.keys())
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
            self.server.add_value_to_store(data['entry'][0])

    # We have received a POST from the leader that there was an update to the board so we will now
    # set our local board to show the centralized version of the board
    def update_board(self, data):
        data = self.reformat_data(data)
        self.server.update_board(data) # Dict is not ordered so I have no idea how this will be ordered in GUI


    def do_leader_election(self, data):
        # Assuming we format the data as something like the following
        # data = {"max":"%d","leader":"%s","contributingNodes":"%s"}
        # At this point all nodes have generated a random value and election process is over, time to set leader
        
        # We check to see if we have 10 "votes" for a leader
        print self.server.vessel_id
        if int(data["contributingNodes"][0]) == len(self.server.vessels): # comparing strings
            print "should be setting leader to %s" % data["leader"][0]
            self.do_set_leader(data)
        # Keep electing
        else:
            data["contributingNodes"][0] = int(data["contributingNodes"][0]) + 1
            my_num = random.randint(1,11)
            if my_num >= int(data["max"][0]):
                data["max"][0] = my_num
                data["leader"][0] = self.server.vessel_id
            self.server.contact_vessel("10.1.0.%d" % self.get_next_vessel(), leader_election_path, self.reformat_data(data))


    def do_set_leader(self, data):
        print('setting leader to %s' % data["leader"])
        global leader
        # If we already have the correct leader then we do not need to send the message to the 
        # next vessel because they also have the same leader, thus the if statment
        if leader != data["leader"][0]:
            leader = data["leader"][0] # this will make it a string
            self.server.contact_vessel("10.1.0.%d" % self.get_next_vessel(), leader_selection_path, self.reformat_data(data))
        
        return
    
    def get_next_vessel(self):
        return 1 if self.server.vessel_id == len(self.server.vessels) else vessel_id + 1
#------------------------------------------------------------------------------------------------------

    def reformat_data(self, data):
        return_dict = {}
        for key in data:
            return_dict[key] = data[key][0]
        return return_dict
#------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':

    ## read the templates from the corresponding html files
    # .....
    # Open the html files
    folder = os.path.join(os.getcwd(), "server", "")
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
    #thread = Thread(target=self.start_leader_election,args=({}))
    #thread.daemon = True
    #thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Stopping Server")
#------------------------------------------------------------------------------------------------------
