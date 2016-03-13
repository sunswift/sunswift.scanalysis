#!/usr/bin/env python
# Fluke Hydra data logger interface software
# for Scanalysis.
#
# Sam May
#

# libs
import os
import gtk
import gobject
import threading
from time import sleep
import datetime
import time

# internal scanalysis libs
import Driver
import Configurator
from Fluke import *


# having this as a separate thread prevents lagging in the GUI, what with all
# the constant polling and waiting.
class FlukeControllerThread(threading.Thread):
    """A thread that will set up a Fluke Hydra with a given config, start it
    logging, and put continuously put measurements on a queue until the
    polling_event signal is unset, at which point it will cleanly shut down the
    Fluke and exit."""
    def __init__(self,config,log_queue,log_queue_lock,polling_event):
        threading.Thread.__init__(self)
	self.log_queue = log_queue
	self.log_queue_lock = log_queue_lock
	self.polling_event = polling_event

        print "Starting fluke on port " + config["port"]
	self.fluke = Fluke(config["port"])

        # make sure we are in idle mode
        self.fluke.stop_logging()

	# set the time
	self.fluke.set_datetime(datetime.datetime.now())

	# set the interval
	self.fluke.set_interval(config["interval"])

	# configure channel functions
	functions = config["channels"]
	self.channels = functions.keys()
     	self.channels.sort() # SIDE EFFECTS, sort() is IN PLACE!
     	for channel in self.channels:
            if "scaling" in functions[channel]:
                scaling = functions[channel]["scaling"]
            else:
                scaling = None
            self.fluke.set_function(channel,functions[channel]["function"],
                                    scaling=scaling)

        if config.has_key("monitor"):
            self.fluke.start_monitoring(config["monitor"])
        
	self.fluke.start_logging()
	
    def run(self):
	while self.polling_event.isSet():
	    data,timestamp = self.fluke.read_log()
            # we want seconds since the epoch
            t = time.mktime(timestamp.timetuple())
	    # data is in order of channel
	    packets = [(i,Driver.Deliverable(data[i],t)) for i in range(len(data))]

	    # THREADING BIT
	    self.log_queue_lock.acquire()
	    # put on the array of deliverables
	    self.log_queue.append(packets)
	    self.log_queue_lock.release()
	    #END THREADING BIT
	self.fluke.stop_logging()
	self.fluke.serial_link.close()

class FlukeDriver(Driver.Driver):
    """Scanalysis module for a Fluke Hydra. Takes a configuration hash and
    starts a FlukeControlThread, and sets up a notebook page in the main window
    with graphs for each channel."""

    def __init__(self,sa,config,name="Fluke Hydra"):
	Driver.Driver.__init__(self,sa,config,name)

	## CONFIGURATION ##
        if "port" not in config:
            config["port"] = "/dev/ttyUSB0"
	if "interval" not in config:
            config["interval"] = 1 # in secs
	if "rate" not in config:
            config["rate"] = Fluke.FAST_RATE

        # channels. each channel configuration is a list of arguments for the
        # Fluke.set_function() function. So, for channel 2 here, set_function()
        # will be called like set_function(2,"Temperature","J Thermocouple")
        #
        # the order is: channel,function,range,scaling values,terminals)
#	config["channels"] = {
#            2:{
#                "function":"Temperature",
#                "range":"J Thermocouple",
#            }, 
#            3:{
#                "function":"DC Voltage",
#                "range":"300mV",
#                "scaling":(0.0123,0,0),
#            },
#            4:{
#                "function":"DC Voltage",
#                "range":"300mV",
#                "scaling":(0.012285,0,0),
#            },
#        }

        if "channels" not in config:
            config["channels"] = {
                1:{
                    "function":"DC Voltage",
                    "range":"300V",
                    "name":"Output Voltage"
                    }, 
                2:{
                    "function":"DC Voltage",
                    "range":"300mV",
                    "scaling":(39.4186975521086,0.00121266137497,0),
                    "name":"Input Current"
                    }, 
                3:{
                    "function":"DC Voltage",
                    "range":"300mV",
                    "scaling":(40.0034500365415,0.00049343453048,0),
                    "name":"Output Current"
                    },
                11:{
                    "function":"DC Voltage",
                    "range":"300V",
                    "name":"Input Voltage"
                    },
                }
            
            
	self.source = Driver.Source(sa.store,self.get_name())
        channums = config["channels"].keys()
        channums.sort()
        self.channels = [Driver.Channel(self.source, config["channels"][c]["name"])
                         for c in channums]

#        self.page = gtk.VBox()
#        self.graphs = []
#        self.graphdatas = []
#        for c in config["channels"].keys():
#            graph = GraphingMPL.Graph(self.sa, 
#                                      xlabel="Time (s)", 
#                                      ylabel="Speed (m/s)", 
#                                      maxupdate=500)
#            col1.pack_start(graph.get_widget())
#            series = Graphing.SeriesTime(self.sa, self.get_name(), 
#                                         "Channel %d" % c, 
#                                         label="Channel %d (%s)" %
#                                         (c,config["channels"][c][0]), 
#                                         maxtimediff=10.0, 
#                                         format={"linewidth":1.0}) 
#            graph.add_series(series)
#
#        for g in self.graphs:
#            self.page.pack_end(g)
#
#        self.sa.add_notebook_page(self.get_display_name(), self.page)

        # set up a polling thread
	self.log_queue = []
	self.polling = threading.Event()
	self.polling.set()
	self.log_queue_lock = threading.Lock()
	self.polling_thread = FlukeControllerThread(self.config,
						    self.log_queue,
						    self.log_queue_lock,
						    self.polling)
	# set as daemon, otherwise the thread will keep on running if scanalysis
	# is killed unexpectedly
	self.polling_thread.setDaemon(True)
	self.polling_thread.start()
	# check once every interval, this should avoid too much
	# blocking/starvation
	gobject.timeout_add(config["interval"]*500, self.update)
	    
    def update(self):
        """Deliver all the packets on the FlukeControlThread's log queue."""
        # THREADING BIT
	self.log_queue_lock.acquire()
	for log in self.log_queue:
	    self.log_queue.remove(log)
            for i in range(len(log)):
		(num, pkt) = log[i]
                self.channels[i].deliver(pkt)
	self.log_queue_lock.release()
	# END THREADING BIT
	return self.running
	
    def configure(self):
        """Create a configuration dialogue for the Fluke module"""
        config = {}
        channels = {}
	widget = Driver.Driver.configure(self)
        for channel in range(0,21):
            dialogue = gtk.VBox()
            chan_config = {}
            label = gtk.Label("Channel %d" % channel)
            dialogue.pack_start(label)
            functions = Configurator.ListConfig("function",chan_config,Fluke.Fluke.FUNCTIONS,"Function")
            # just use 'Auto' for now.
#            ranges = Configurator.ListConfig("range",chan_config,Fluke.Fluke.RANGES["VAC"],"Range")
            chan_config["range"] = "Auto"
            dialogue.pack_end(functions)
            widget.pack_end(dialogue)
        #config["channels"] = {}
        #monitoring = Configurator.IntConfig("monitor",config
        return widget

    def stop(self):
        """Stop the FlukeControlThread and shut down cleanly"""
	# stop polling thread
	self.polling.clear()
	self.polling_thread.join()
	Driver.Driver.stop(self)

Driver.modfac.add_type("Fluke Hydra",FlukeDriver)
