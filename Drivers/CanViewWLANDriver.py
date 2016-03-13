import gobject
import gtk

import Can
import Driver 
import socket
import thread
import sys
import Configurator
import struct

class CanViewWLANDriver(Driver.Driver, Can.Interface):
    def __init__(self, sa, config, name="CanBridge"):
        Can.Interface.__init__(self)
        Driver.Driver.__init__(self, sa, config, name=name)

        if "address" not in self.config:
            self.config["address"] = "192.168.0.52"

        if "port" not in self.config:
            self.config["port"] = 3491

        self.sa.console.write(self.get_display_name() + ": " + \
                                  "attempting to connect to " + \
                                  self.config["address"] + " on port %d." % \
                                  self.config["port"])

        self.data = ""
        self.running = True

        self.pkt_queue_lock = thread.allocate_lock()
        self.pkt_queue = []

        gobject.timeout_add(100, self.poll)

        self.worker_thread = thread.start_new_thread(self.worker, () )


    def worker(self):
        while self.running:
            while self.running:
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect( (self.config["address"], self.config["port"]) )
                    break
                except socket.error, (value, message):
                    
                    self.sa.console.write(self.get_display_name() + ": " + \
                                              "Got an error attempting to connect to " + \
                                              self.config["address"] + " on port %d." % \
                                              self.config["port"])
                    self.sa.console.write(self.get_display_name() + ": " + \
                                              "Error was: " + \
                                              message)


            while self.running:
		try:
                	newdata = self.socket.recv(1024)
                except socket.error, (value,message):
			self.sa.console.write(message, mod=self)
			break

		self.data = self.data + newdata
            
                while len(self.data) >= 17:
                    newdata = self.data[0:17]
                    self.data = self.data[len(newdata):]

                    unpacked = struct.unpack("cBBBBBBBBBBBBBBBc", newdata)
                    id = (unpacked[3] << 24) |\
                        (unpacked[4] << 16) |\
                        (unpacked[5] << 8) |\
                        (unpacked[6] << 0);
                    data = unpacked[7:15]
                
                    self.pkt_queue_lock.acquire()
                    self.pkt_queue.append( Can.Packet(id,data) )
                    self.pkt_queue_lock.release()
        
    def poll(self):
        # This is a _long_ critical section. Possibly not a great plan. 
        self.pkt_queue_lock.acquire()
        while len(self.pkt_queue) > 0:
            pkt = self.pkt_queue.pop(0)
            self.deliver(pkt)
        self.pkt_queue_lock.release()
        return 1

    def send(self, pkt):
        print ("Sending!\n")
        data = pkt.get_data()
        id = pkt.get_id()

        bytes = [0x43, 13, 0x02, \
                     (id >> 24) & 0xFF, \
                     (id >> 16) & 0xFF, \
                     (id >> 8) & 0xFF, \
                     (id >> 0) & 0xFF]
        bytes = bytes + data
        checksum = 0
        for elem in bytes:
              checksum ^= elem

        tosend = struct.pack("cBBBBBBBBBBBBBBBc", \
                          'C', 13, 0x02,\
                          bytes[3], \
                          bytes[4], \
                          bytes[5], \
                          bytes[6], \
                          bytes[7], \
                          bytes[8], \
                          bytes[9], \
                          bytes[10], \
                          bytes[11], \
                          bytes[12], \
                          bytes[13], \
                          bytes[14], \
                          checksum, \
                          '\r')
        self.socket.send(tosend)

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("address", self.config, "Address")
        w.pack_start(e, expand=False)
        
        e = Configurator.IntConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

    def stop(self):
        self.running = False
        

# Register our driver with the driver module's module factory
Driver.modfac.add_type("CanView WLAN", CanViewWLANDriver)
