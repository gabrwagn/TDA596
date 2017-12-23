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
from byzantine_behavior import *

#------------------------------------------------------------------------------------------------------
# Static variables definitions
PORT_NUMBER = 80
#------------------------------------------------------------------------------------------------------




#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
#------------------------------------------------------------------------------------------------------
    def __init__(self, server_address, handler, node_id, vessel_list):
    # We call the super init
        HTTPServer.__init__(self,server_address, handler)
        # we create the dictionary of values
        self.vote_one_store = {}
        self.vote_two_store = []
        # our own ID (IP is 10.1.0.ID)
        self.vessel_id = vessel_id
        # The list of other vessels
        self.vessels = vessel_list
        self.is_byzantine = False
        self.number_of_votes_collected = 0
        self.number_of_loyal_nodes = 2 # Will need to change this value for testing task 2 (maybe)

#------------------------------------------------------------------------------------------------------
    # We add a value received to the vote one store
    def add_vote(self, sender, vote):
        # We add the value to the store
        self.number_of_votes_collected += 1

    # We add a value received to the vote two store
    def add_result_vector(self, vector):
        # We add the value to the store
        pass
#------------------------------------------------------------------------------------------------------
# Contact a specific vessel with a set of variables to transmit to it
    def contact_vessel(self, vessel_ip, path, data):
        # the Boolean variable we will return
        success = False
        # The variables must be encoded in the URL format, through urllib.urlencode
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
    
    # This function incorporates the same logic as the function given to use in the 
    # Byzantine_behavior.py file but sends directly to nodes  
    def byzantine_vote_one_to_other_vessels(self, data):
        count = 1
        for vessel in self.vessels:
            if vessel != ("10.1.0.%s" % self.vessel_id):
                if count % 2 == 0:
                    self.contact_vessel(vessel, "/vote/attack", data)
                else:
                    self.contact_vessel(vessel, "/vote/retreat", data)
                count += 1
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
#------------------------------------------------------------------------------------------------------
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
        # We should do some real HTML here
        html_reponse = frontpage_template_fo
        #In practice, go over the entries list,
        #produce the boardcontents part,
        #then construct the full page by combining all the parts ...

        self.wfile.write(html_reponse)
#------------------------------------------------------------------------------------------------------
    # we might want some other functions
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Request handling - POST
#------------------------------------------------------------------------------------------------------
    def do_POST(self):
        print("Receiving a POST on %s" % self.path)
        # Here, we should check which path was requested and call the right logic based on it
        # We should also parse the data received
        # and set the headers for the client

        data = self.parse_POST_request()
        path_parts = self.path[1:].split('/')

        # If the sender field is in the data, we are receiving a relay message
        # else we are the node who is voting
        retransmit = True
        if "sender" in data:
            sender = data["sender"][0] # Don't know if this is str or int
            print data
            self.handle_reply(path_parts, data)
        else:
            self.handle_local(path_parts, data)

        if self.server.is_byzantine and self.server.number_of_loyal_nodes == self.server.number_of_votes_collected:
            self.server.byzantine_vote_one_to_other_vessels({"sender": self.server.vessel_id}) # Maybe make to int
        if self.server.number_of_votes_collected == len(self.server.vessels) and not self.server.is_byzantine:
            # Now it is time for us to send out our result vectors
            self.retransmit("/vote/result",self.server.get_vote_vector())
        # TODO Now we need to handle the case where we have all result vectors and we are byzantine 
        # TODO Also handle calculating the final result when we have received all result vectors
        
#------------------------------------------------------------------------------------------------------
# POST Logic
#------------------------------------------------------------------------------------------------------
    # We might want some functions here as well
#------------------------------------------------------------------------------------------------------

    def retransmit(self, path, data):
        thread = Thread(target=self.server.propagate_value_to_vessels,args=(self.path, data)) # May need to reformat data 
        thread.daemon = True
        thread.start()

    def handle_local(self, path_parts, data):
        # We are making the post on a local vessel
        # We need to add to the data and add to our data if we are not byzantine
        if path_parts[1] == "byzantine":
            self.server.is_byzantine = True
        else:
            self.server.add_vote(self.server.vessel_id, path_parts[1])
            data["sender"] = self.server.vessel_id
            self.retransmit(self.path, data)

    def handle_reply(self, path_parts, data):
        # We are handling a reply coming from another vessel
        # Once we have received all of the non byzantine votes, we will let byzantine nodes vote
        
        if not self.server.is_byzantine:
            self.server.add_vote(data["sender"][0], path_parts[1]) # Add to the list, byzantine will ignore this
            





#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':

    ## read the templates from the corresponding html files
    # .....

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


    folder = os.path.join(os.getcwd(), "server", "vote_frontpage_template.html")
    frontpage_template_fo = list(open(folder, 'r'))
    # We launch a server
    server = BlackboardServer(('', PORT_NUMBER), BlackboardRequestHandler, vessel_id, vessel_list)
    print("Starting the server on port %d" % PORT_NUMBER)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Stopping Server")
#------------------------------------------------------------------------------------------------------
