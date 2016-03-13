import Driver
import gobject
import time
import math
import gtk
import Configurator
import thread
import socket

class NetworkDriver(Driver.Driver):
    def __init__(self, sa, config, \
                     name="Network"):
        Driver.Driver.__init__(self, sa, config, name)
        
        # Default configuration
        # Check to see if we don't have sourcename, 
        # which we should. 
        if "address" not in config:
            self.config["address"] = "localhost"
        if "port" not in config:
            self.config["port"] = 4000

        self.data = ""
        self.running = True

        self.in_queue = []
        self.in_queue_lock = thread.allocate_lock()

        self.out_queue = []
        self.out_queue_lock = thread.allocate_lock()
        
        gobject.timeout_add(100, self.poll)

        self.worker_thread = thread.start_new_thread(self.worker, ())

    # Do the network communications. 
    def worker(self):
        print "Started worker thread!"
        while self.running:
            while self.running:
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect( (self.config["address"], self.config["port"]) )
                    print
                    break
                except socket.error, (value, message):
                    self.sa.console.write("Got an error attempting to connect to " + 
                                          self.config["address"] + " on port %d." % 
                                          self.config["port"], 
                                          mod = self)
                    self.sa.console.write("Error was: " + message, 
                                          mod = self)
                    time.sleep(1)

            while self.running:
                print "Running receive loop"
		try:
                	newdata = self.socket.recv(1024)
                except socket.error, (value,message):
			self.sa.console.write(message, mod=self)
			break

		self.data = self.data + newdata
                print "Received some data!"
                print self.data

               # Do something with the above data
#                self.pkt_queue_lock.acquire()
#                self.pkt_queue.append( Can.Packet(id,data) )
#                self.pkt_queue_lock.release()



    # Take stuff from the in queue and send them off to scanalysis. 
    def poll(self):
        return 1

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("address", self.config, "Server Address")
        w.pack_start(e, expand=False)

        e = Configurator.IntConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("NetworkDriver", NetworkDriver)

