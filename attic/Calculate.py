from Misc import *
from time import *
import gtk
import gobject
import os

class Global:
    speed = 0.0
    index = 0
    latitude = 0.0
    longitude = 0.0
    chainage = 0.0
    next_stop = ""
    next_stop_index = 0

class CalculateGPS(NewListener, gtk.HBox, Global):
    def __init__ (self, store, nodename, channame, label = None, units = ""):
	gtk.HBox.__init__(self)
        NewListener.__init__(self, store, nodename, channame)
	self.channame = channame
	self.units_string = units
	self.text = gtk.Label(str = "")
	self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
	if label is not None:
	    self.label = gtk.Label(str = label)
	    self.label.set_justify(gtk.JUSTIFY_LEFT)
	    self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
	value = self.value/60
        self.text.set_text("%.3f%s" % (value, self.units_string))
	if self.channame == "Latitude":
	    Global.latitude = value
	else:
	    Global.longitude = value

class CompletedCourse(NewListener, gtk.HBox, Global):
    def __init__ (self, store, nodename, channame, channame2, label = None, units = "", filename = "Road.csv"):
	gtk.HBox.__init__(self)
        NewListener.__init__(self, store, nodename, channame)
	self.units_string = units
	self.filename = filename
	self.percent = 0.0
	self.chainage = 0.0
	self.index = 0

	index_record = open("index.txt", "w")
	index_record.write("0")
	index_record.close()

	self.road = open(filename, "r")
	self.a = 0
	for line in self.road:
	    self.a = self.a + 1
	self.road.close()

	self.road = open(filename, "r")
	self.distance = 0.0
	for line in self.road:
	    temp = line.split(",")
	    if (int(temp[0])) == self.a:
		self.distance = float(temp[4])
	self.road.close()

	self.text = gtk.Label(str = "")
	self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
	if label is not None:
	    self.label = gtk.Label(str = label)
	    self.label.set_justify(gtk.JUSTIFY_LEFT)
	    self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
	    self.pack_start(self.label)
        self.pack_end(self.text)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
	self.longitude = self.value

	road = open(self.filename, "r")
	for line in road:
	    temp = line.split(",")
	    if (Global.index < int(temp[0])):
		if round((self.longitude/60), 3) == round(float(temp[2]), 3) and round(Global.latitude, 3) == round(float(temp[1]), 3):
		    self.index = float(temp[0])
		    print Global.chainage
		    if self.index > (20 + Global.index):
			self.index = Global.index + 20
		    Global.index = self.index
		    index_record = open("index.txt", "w")
		    index_record.write(str(self.index))
		    index_record.close()
		    self.percent = ((Global.chainage)/self.distance)*100
		    self.text.set_text("%.2f%s" % (self.percent, self.units_string))
		    break
		else:
		    continue
	    else:
		continue

class CurrentSpeed(NewListener, gtk.HBox, Global):
    def __init__ (self, store, nodename, channame, label = None, units = ""):
	gtk.HBox.__init__(self)
        NewListener.__init__(self, store, nodename, channame)
	self.units_string = units
	self.text = gtk.Label(str = "")
	self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
	if label is not None:
	    self.label = gtk.Label(str = label)
	    self.label.set_justify(gtk.JUSTIFY_LEFT)
	    self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
        self.text.set_text("%.3f%s" % (self.value, self.units_string))
	Global.speed = self.value

class TimeToEnd(NewListener, gtk.HBox, Global):
    def __init__ (self, store, nodename, channame, label = None, units1 = "", units2 = "", filename = "Road.csv"):
	gtk.HBox.__init__(self)
        NewListener.__init__(self, store, nodename, channame)
	self.units1 = units1
	self.units2 = units2
	self.filename = filename

	chain = []
	course = open(filename, "r")
	for line in course:
	    temp = line.split(",")
	    chain.append(float(temp[4]))
	course.close()
	self.max_chain = max(chain)

	self.text = gtk.Label(str = "")
	self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
	if label is not None:
	    self.label = gtk.Label(str = label)
	    self.label.set_justify(gtk.JUSTIFY_LEFT)
	    self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
	speed = self.value
	course = open(self.filename, "r")
	for line in course:
	    temp = line.split(",")
	    if float(temp[0]) == Global.index:
		chainage = float(temp[4])
		if speed == 0:
		    speed = 0.0001
	    	time = (self.max_chain - chainage)/speed
	    	hour = int(time)
	   	tmp = time - hour
	    	minute = round(tmp * 60)
		self.text.set_text("%d%s %d%s" % (hour, self.units1, minute, self.units2))
		break
	course.close()
	
class CalculateNextStop(NewListener, gtk.HBox, Global): #receive speed
    def __init__ (self, store, nodename, channame, label = None, course_file = "Road.csv", stop_file = "Stops.csv"):
	gtk.HBox.__init__(self)
        NewListener.__init__(self, store, nodename, channame)
	#self.a = 0
	#stops = open("Stops.csv", "r")
	#for line in stops:
	#    self.a = self.a + 1
	#stops.close()
	#self.stop = [[]*1]*(self.a)
	#stops = open("Stops.csv", "r")
	#for i in range(self.a):
	#    self.stop[i] = stops.readline()
	self.course_file = course_file
	self.stop_file = stop_file
	self.text = gtk.Label(str = "")
	self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 1.0)
        self.text.set_padding(4, 1)
	if label is not None:
	    self.label = gtk.Label(str = label)
	    self.label.set_justify(gtk.JUSTIFY_LEFT)
	    self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
	speed = self.value
	stops = open(self.stop_file, "r")
	for line in stops:
	    temp = line.split(",")
	    if int(temp[0]) > self.index:
		Global.next_stop = temp[4]
		Global.next_stop_index = int(temp[0])
		break
	stops.close()
	stop_chainage = 0.0
	current_chainage = 0.0
	road = open(self.course_file, "r")
	for line in road:
	    tmp = line.split(",")
	    if int(tmp[0]) == Global.next_stop_index:
		stop_chainage = float(tmp[4])
	    if int(tmp[0]) == Global.index:
		current_chainage = float(tmp[4])
	road.close()
	if speed == 0.0:
	    speed = 0.0001
	time = (stop_chainage - current_chainage)/speed
	hour = int(time)
	remain = time - hour
	minute = round(remain * 60)

        self.text.set_text("%s in %dh%dm" % (Global.next_stop, hour, minute))
	
class EndOfDayLocation(NewListener, gtk.HBox, Global): # take in speed
    def __init__ (self, store, nodename, channame, label = None, course_file = "Road.csv"):
	gtk.HBox.__init__(self)
        NewListener.__init__(self, store, nodename, channame)
	self.course_file = course_file
	self.text = gtk.Label(str = "")
	self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
	if label is not None:
	    self.label = gtk.Label(str = label)
	    self.label.set_justify(gtk.JUSTIFY_LEFT)
	    self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
	speed = self.value

	tm1 = strftime("%H", gmtime(time()))
	tm2 = strftime("%M", gmtime(time()))
	current_time = (int(tm1)) + ((int(tm2))/60)
	if current_time > 8 & current_time < 17:
	    remaining_time = 17.0 - current_time
	    distance = round((remaining_time * speed), 3)

	    road = open(self.course_file, "r")
	    est_chainage = 0.0
	    est_latitude = 0.0
	    est_longitude = 0.0
	    est_index = 0

	    for line in road:
	        temp = line.split(",")
	        if int(temp[0]) == Global.index:
	    	    Global.chainage = round(float(temp[4]), 3)
	        if Global.chainage != 0.0:
	    	    if round(float(temp[4]), 3) <= round((distance + Global.chainage), 3):
	    	        est_chainage = float(temp[4])
		        est_latitude = float(temp[2])
		        est_longitude = float(temp[1])
		        est_index = int(temp[0])	
	    road.close()

	#if (distance + Global.chainage) > float(temp[4]):
	    #est_chainage = float(temp[4])
	    #est_latitude = float(temp[2])
	    #est_longitude = float(temp[1])
	    #est_index = int(temp[0])
	    
            self.text.set_text("Lon:%.3f Lat:%.3f (%.3fkm)" % (est_longitude, est_latitude, est_chainage))









