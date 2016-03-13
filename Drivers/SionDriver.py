# Based on the CANUSB Driver. Sockets-based.

import gobject
import gtk

import Can
import Driver 
import socket
import thread
import sys
import Configurator
import struct
import socket
import ctypes
import time

"""
        if "port" not in config:
            config["port"] = "/dev/ttyUSB0"
"""

class SionDriver(Driver.Driver, Can.Interface):
    def __init__(self, sa, config, name="SION"):
		Can.Interface.__init__(self)
		Driver.Driver.__init__(self, sa, config, name=name)
		
		
		
		#single receiver
		self.host = "127.0.0.1"
		#self.port = 3491
		#multicast params
		#self.mcgroup = "239.0.0.157"
		self.port = 31337
		self.myaddr = (self.host, self.port)

		self.cielhost = "127.0.0.1"
		self.cielport = 3496
		self.cieladdr = (self.cielhost, self.cielport)
		
		self.buf = 13 #do NOT change, may or may not break shit
		
		self.ss = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.ss.bind(self.myaddr)
		print "binding success"
		
		self.data = ""
		self.dataout = ["","","","","","","","","","","","",""]
		self.dataout2 = ""
		self.content = ["","","","","","","",""]
		self.content2 = ""
		self.pkt_queue_lock = thread.allocate_lock()
		self.pkt_queue = []
		gobject.timeout_add(100, self.poll)
		self.worker_thread = thread.start_new_thread(self.worker, () )
		self.active = False

    def get_active(self):
        Can.Interface.is_active(self)
        return self.active
        
    def worker(self):
		while self.running:
			try:
				self.sa.console.write("activating",\
											mod=self)
				self.active = True
				break
			except:
				self.sa.console.write("wtf happened",\
											mod=self)
				time.sleep(1)
		while self.running:
			
			#I think this is a new variable and not self.data... objects, how do they work?
			self.data,senderaddr = self.ss.recvfrom(self.buf)
			
			self.header = ctypes.c_uint32( (	(ord(self.data[0]) << 26) | \
										(ord(self.data[1]) << 18) | \
										(ord(self.data[2]) << 10) | \
										(ord(self.data[3]) <<  0) | \
										(ord(self.data[4]) <<  8)  \
										) & 0xFFFFFFFF).value
			"""
			self.content = ctypes.c_uint64( ((ord(data[ 5]) << 32) | \
											(ord(data[ 6]) << 40) | \
											(ord(data[ 7]) << 48) | \
											(ord(data[ 8]) << 56) | \
											(ord(data[ 9]) <<  0) | \
											(ord(data[10]) <<  8) | \
											(ord(data[11]) << 16) | \
											(ord(data[12]) << 24)   \
											) & 0xFFFFFFFFFFFFFFFF).value
			"""
			#try:
			#sorry for the clusterfuck
			
			self.content[ 0] = ord(self.data[ 8])
			self.content[ 1] = ord(self.data[ 7])
			self.content[ 2] = ord(self.data[ 6])
			self.content[ 3] = ord(self.data[ 5])
			self.content[ 4] = ord(self.data[12])
			self.content[ 5] = ord(self.data[11])
			self.content[ 6] = ord(self.data[10])
			self.content[ 7] = ord(self.data[ 9])
			
			self.content2 = self.content[0:7]
					
			#except:
			#	self.sa.console.write("something broke :(",\
			#				mod=self)
			"""
			self.content[ 0] = data[ 8]
			self.content[ 1] = data[ 7]
			self.content[ 2] = data[ 6]
			self.content[ 3] = data[ 5]
			self.content[ 4] = data[12]
			self.content[ 5] = data[11]
			self.content[ 6] = data[10]
			self.content[ 7] = data[ 9]
			"""
			
			
			self.pkt_queue_lock.acquire()
			self.pkt_queue.append( Can.Packet(self.header,self.content2) )
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
	if self.is_active() is not True:
		return

	data = pkt.get_data()
	pkid = pkt.get_id()
	#see sion scandal.h for specs

	# THIS WORKS. DO NOT TOUCH.
	odata = [(pkid>>26) & 0x07, \
			(pkid>>18) & 0xFF, \
			(pkid>>10) & 0xFF, \
			(pkid>> 0) & 0xFF, \
			(pkid>> 8) & 0x03]
	odata = odata + [data[3]]
	odata = odata + [data[2]]
	odata = odata + [data[1]]
	odata = odata + [data[0]]
	odata = odata + [data[7]]
	odata = odata + [data[6]]
	odata = odata + [data[5]]
	odata = odata + [data[4]]
	tosend=""
	for byte in odata:
		tosend += struct.pack("B", byte)

	self.ss.sendto(tosend, self.cieladdr)




    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

    def stop(self):
        self.running = False
        

# Register our driver with the driver module's module factory
Driver.modfac.add_type("SION", SionDriver)
