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
import byzantine_behavior

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
        self.number_of_loyal_nodes = len(self.vessels) - 1
        self.final_decision = ""

#------------------------------------------------------------------------------------------------------
    # We add a value received to the vote one store
    def add_vote(self, sender, vote):

        # Prevent a node from voting more than once
        if not sender in self.vote_one_store:
            self.vote_one_store[int(sender)] = vote
            # We add the value to the store
            self.number_of_votes_collected += 1

        print self.vote_one_store
    # We add a value received to the vote two store
    def add_result_vector(self, vector):
        add_vector = {}
        for key in vector:
            add_vector[int(key)] = vector[key]
        self.vote_two_store.append(add_vector)

    def get_vote_vector(self):
        # The python API needs keys to be in a string format for urlencoding
        # r_val = {}
        # for key in self.vote_one_store:
        #     r_val[str(key)] = self.vote_one_store[key]
        # return r_val
        return self.vote_one_store

    def make_final_decision(self):
        # We use the vote 2 store to make our decision
        # Default behavior is to attack
        num_attacks = 0
        num_retreats = 0

        for dictionary in self.vote_two_store:
            for key in dictionary:
                if dictionary[key] == "attack":
                    num_attacks += 1
                else:
                    num_retreats += 1
        self.final_decision = "attack" if num_attacks >= num_retreats else "retreat"
        print self.final_decision

        # final_vector = [] # We just need a list for this
        # temp_vector = []
        # i = 0 # col number
        # j = 0 # row number
        # print self.vote_two_store
        # while i < len(self.vote_two_store):
        #     while j < len(self.vote_two_store):
        #         temp_vector.append(self.vote_two_store[j][i + 1])
        #         j += 1
        #     final_vector.append(self.compute_result(temp_vector))
        #     i += 1
        # self.final_decision = self.compute_final_result(final_vector)
        
            
    def compute_result(self, vector):
        if "attack" in vector and "retreat" in vector:
            return "attack" # Default stategy
        elif "attack" in vector:
            return "attack" # all nodes voted attack
        else:
            return "retreat" # all nodes voted retreat
            
    def compute_final_result(self, vector):
        num_attacks = 0
        num_retreats = 0
        for i in vector:
            if i == "attack":
                num_attacks += 1
            else:
                num_retreats += 1
        return "attack" if num_attacks >= num_retreats else "retreat"


#------------------------------------------------------------------------------------------------------
# Contact a specific vessel with a set of variables to transmit to it
    def contact_vessel(self, vessel, path, data):
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
    def byzantine_vote_one_to_other_vessels(self, d):
        count = 1
        print '\n'
        print "BYZANTINE VOTE PROPOGATIONS >>>>>>>>>>>>>>>"
        data = {}
        data["sender"] = self.vessel_id
        print data
        print '\n'
        for vessel in self.vessels:
            if vessel != ("10.1.0.%s" % self.vessel_id):
                if count % 2 == 0:
                    self.contact_vessel(vessel, "/vote/attack", data)
                else:
                    self.contact_vessel(vessel, "/vote/retreat", data)
                count += 1
    
    def byzantine_vote_two_to_other_vessels(self, data):
        i = 0
        print "WE ARE SENDING OUR VOTE VECTORS TO OTHERS FROM BYZANTINE"
        print data
    
        for vessel in self.vessels:
            if vessel != ("10.1.0.%s" % self.vessel_id):

                # We need to format the dict so that we have consistency when sending
                sending_data = {}
                j = 1
                for el in data[i]:
                    sending_data[j] = el
                    j += 1
                print "sending vessel: %s" % vessel
                print sending_data
                self.contact_vessel(vessel, "/vote/result", sending_data)
                i += 1
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
        self.set_HTTP_headers(200)
        # Here, we should check which path was requested and call the right logic based on it
        # We should also parse the data received
        # and set the headers for the client

        if self.server.final_decision != "":
            return

        data = self.parse_POST_request()
        path_parts = self.path[1:].split('/')

        if "result" in path_parts:
            # We are dealing with round 2 voting
            data = self.reformat_data(data)
            self.server.add_result_vector(data)
            if self.server.is_byzantine and len(self.server.vote_two_store) == self.server.number_of_loyal_nodes:
                # We have received all honest nodes' vectors and now we need to call external function
                # and cast our byzantine vote
                vote_vectors = byzantine_behavior.compute_byzantine_vote_round2(self.server.number_of_loyal_nodes, len(self.server.vessels), True)
                vote_vectors = self.reformat_vectors(vote_vectors)
                self.byzantine_vote_two_prop(vote_vectors)
                self.server.add_result_vector(self.compute_fake_data())
                # Need to make sure that we compute result when all of our vectors are here
                # If we have more than one byzantine entity, it will be caught in the if statment in the 
                # else statment below
                if len(self.server.vote_two_store) == len(self.server.vessels):
                    self.server.make_final_decision()

            else:
                if len(self.server.vote_two_store) == len(self.server.vessels):
                    print "MAKING FINAL DECISION"
                    # We need to make a final decision on our strategy
                    self.server.make_final_decision()
        else:
            if self.server.number_of_votes_collected == len(self.server.vessels):
                print "\nWe are getting extra props\n"
                return
            if "sender" in data:
                sender = data["sender"][0] # Don't know if this is str or int
                print "GETTING A RELAY"
                self.handle_relay(path_parts, data)
            else:
                print "HANDLING LOCAL REQUEST"
                print path_parts
                print data
                self.handle_local(path_parts, data)

            if self.server.is_byzantine and self.server.number_of_loyal_nodes == self.server.number_of_votes_collected:
                self.byzantine_vote_one_prop() # Maybe make to int
            if self.server.number_of_votes_collected == len(self.server.vessels) and not self.server.is_byzantine:
                # Now it is time for us to send out our result vectors
                self.server.add_result_vector(self.server.vote_one_store)
                print "HONEST NODE SENDING RESULT VECTOR TO OTHER NODES"
                self.retransmit("/vote/result", self.server.get_vote_vector())

        return
        
    def compute_fake_data(self):
        r_val = {}
        i = 0
        while i < len(self.server.vessels):
            r_val[i + 1] = "retreat"
        return r_val
    def reformat_data(self, data):
        r_val = {}
        for key in data:
            r_val[key] = data[key][0]
        return r_val

    def reformat_vectors(self, vectors):
        r_vectors = []
        for vector in vectors:
            r_vectors.append(["attack" if x else "retreat" for x in vector])
        return r_vectors
#------------------------------------------------------------------------------------------------------
# POST Logic
#------------------------------------------------------------------------------------------------------
    # We might want some functions here as well
#------------------------------------------------------------------------------------------------------

    def byzantine_vote_one_prop(self):
        thread = Thread(target=self.server.byzantine_vote_one_to_other_vessels,args=({"sender": self.server.vessel_id}))
        thread.daemon = True
        thread.start()

    def byzantine_vote_two_prop(self, data):
        thread = Thread(target=self.server.byzantine_vote_two_to_other_vessels, args=(data,))
        thread.daemon = True
        thread.start()

    def retransmit(self, path, data):
        thread = Thread(target=self.server.propagate_value_to_vessels,args=(path, data)) # May need to reformat data 
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

    def handle_relay(self, path_parts, data):
        # We are handling a relay coming from another vessel
        # Once we have received all of the non byzantine votes, we will let byzantine nodes vote
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
