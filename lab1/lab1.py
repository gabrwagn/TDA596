# coding=utf-8
#------------------------------------------------------------------------------------------------------
# TDA596 - Lab 1
# This script creates the distributed system, runs the simulation and launches the servers app
# Contains two classes: Lab1Topology and Lab1
# This script does not need any modification
# Author: Valentin Poirot <poirotv@chalmers.se>
#------------------------------------------------------------------------------------------------------
# Import useful libraries
from mininet.topo import Topo # Network topology
from mininet.net import Mininet # Mininet environment, simulator
from mininet.link import TCLink, TCIntf, Intf # Customisable links & interfaces
from mininet.log import setLogLevel, info # Logger
from mininet.term import makeTerm, cleanUpScreens # Open xterm from mininet
from mininet.cli import CLI # Command Line Interface
#------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Lab1Topology - class inheriting from mininet.topo.Topo, defines the network topology
class Lab1Topology( Topo ):
	"Creates the network topology on which the lab 1 runs"
#------------------------------------------------------------------------------------------------------
	# Initialize variables
	def build(self, nbOfServersPerRegion = 5, nbOfClientsPerRegion = 2, nbOfRegions = 2, **opts):
		# local configuration parameters
		regionalLinkBandwidth = 100 # Mbps
		regionalLinkLosses = 0.00001 # 1e-5 PER
		regionalDelay = 10 # ms, delay = RTT/2
		# internet configuration parameters
		globalLinkBandwidth = 1000 # Mbps
		globalLinkLosses = 0.00001 # 1e-5 PER
		globalDelay = 50 # ms, delay = RTT/2
		# arrays
		switches = []
		servers = []
		clients = []
		# We create the network topology
		# We first add a central switch that connects regions; it emulates the Internet
		centralSwitch = self.addSwitch("s0")
		# For each region
		for regionId in range(0, nbOfRegions):
			# we create a regional switch
			switches.append(self.addSwitch("regSwitch%d" % regionId))
			# we add servers/vessels in that region, with a fixed IP
			for serverId in range(0, nbOfServersPerRegion):
				# serverId is a regional Id, we want a global one
				globalId = regionId*nbOfServersPerRegion+serverId
				# we create the server
				servers.append(self.addHost("vessel%d" % (globalId+1), ip=("10.1.0.%d/24" % (globalId+1))))
				# We add link towards the reginal switch
				self.addLink(switches[regionId], servers[globalId], bw = regionalLinkBandwidth, loss = regionalLinkLosses, delay = "%dms" % regionalDelay)
			# We do the same with clients
			for clientId in range(0, nbOfClientsPerRegion):
				# clientId is a regional Id, we want a global one
				globalId = regionId*nbOfClientsPerRegion+clientId
				# we create the server
				clients.append(self.addHost("client%d" % (globalId+1), ip=("10.1.0.%d/24" % (100+globalId))))
				# We add link towards the reginal switch
				self.addLink(switches[regionId], clients[globalId], bw = regionalLinkBandwidth, loss = regionalLinkLosses, delay = "%dms" % regionalDelay)
			# We must also connect the regional switch to the central switch
			self.addLink(centralSwitch, switches[regionId], bw = globalLinkBandwidth, loss = globalLinkLosses, delay = "%dms" % globalDelay)
#------------------------------------------------------------------------------------------------------








#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Lab1 - class running the Mininet environment and launching the servers
class Lab1():
#------------------------------------------------------------------------------------------------------
	# Open an xterm and launch a specific command
	def startServer(self, server, nbOfServers):
		# Call mininet.term.makeTerm
		makeTerm(node=server, cmd="python server/server.py %s %d" % (server.IP().replace("10.1.0.",""), nbOfServers) )
#------------------------------------------------------------------------------------------------------
	# run(self)
	# Run the lab 1
	def run(self):
		"Run the lab 1 simulation environment"
		# local variables
		nbOfServersPerRegion = 5
		nbOfClientsPerRegion = 2
		nbOfRegions = 2
		localJitter = 10 # ms, the evolution of the time between two consecutive packets
		# We create the topology
		topology = Lab1Topology(nbOfServersPerRegion, nbOfClientsPerRegion, nbOfRegions)
		# We create the simulation
		# Set the topology, the class for links and interfaces, the mininet environment must be cleaned up before launching, we should build now the topology
		simulation = Mininet(topo = topology, link = TCLink, intf = TCIntf, cleanup = True, build = True, ipBase='10.1.0.0/24')
		# We connect the network to Internet
		simulation.addNAT().configDefault()
		# We can start the simulation
		print "Starting the simulation..."
		simulation.start()
		# For each host
		for host in simulation.hosts:
			# We set the jitter (It can only be done after the simulation was started, not from the Topology)
			host.defaultIntf().config(jitter = ("%dms" % localJitter))
		# we create a dictionnary to store the popen
		popens = {}
		# for each server
		for server in simulation.hosts:
			if "vessel" in server.name:
				# We open a xterm and start the server
				self.startServer(server, nbOfServersPerRegion*nbOfRegions)
		# We also start the Command Line Interface of Mininet
		CLI(simulation)
		# Once the CLI is closed (with exit), we can stop the simulation
		print "Stopping the simulation NOW!"
		simulation.stop()
		# We close the xterms (mininet.term.cleanUpScreens)
		cleanUpScreens()
#------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# If the script was directly launched (and that should be the case!)
if __name__ == '__main__':
	# we set the log level to info, in order to display the server outputs as well
	#setLogLevel( 'info' )
	lab = Lab1 ()
	lab.run()
#------------------------------------------------------------------------------------------------------