import Driver
import gobject
import time
import math
import gtk
import Configurator
import serial
import thread
import time

class WindSpeed(Driver.Driver):
    def __init__(self, sa, config, \
                     name="Wind Speed"):
        Driver.Driver.__init__(self, sa, config, name)
        
	# Creating source and channel at tree view in scanalysis.
        self.source = Driver.Source(sa.store, self.get_name())
        self.direction = Driver.Channel(self.source, "Direction")
        self.speed = Driver.Channel(self.source, "Speed")
        
        if "port" not in self.config.keys():
            self.config["port"] = "/dev/ttyUSB0"
		
        self.ws_tread = thread.start_new_thread(self.worker, () )
        self.ws_queue_lock = thread.allocate_lock()
        self.direction_queue = []
        self.speed_queue = []

        gobject.timeout_add(100, self.update)

    def worker(self):
        while self.running:
            try:
                print "Port is: " + self.config["port"]
                self.ser = serial.Serial(self.config["port"], 9600, timeout = 10)
                break
            except serial.serialutil.SerialException,e:
                    self.sa.console.write("Could not open serial port \"%s\"" % self.config["port"], mod=self);
                    time.sleep(1.0)

    
        while self.running:                   
            line = self.ser.readline()
            print "windspeed: " + line

            if len(line) == 0:
                continue
            if line[1] != 'Q':
                print "Got dodgy line from the wind speed sensor -- it starts with: %c" % line[1]
                continue
                
            temp = line.split(",")
            if temp[1] == "":
                direction = 0
            else:
                direction = float(temp[1])
                speed = float(temp[2])
                self.ws_queue_lock.acquire()
                self.direction_queue.append(Driver.Deliverable(direction))
                self.speed_queue.append(Driver.Deliverable(speed))
                self.ws_queue_lock.release()

    def update(self):
        self.ws_queue_lock.acquire()
        for direction in self.direction_queue:
            # To remove the data in the list so not to flood it?
            self.direction_queue.remove(direction)
            self.direction.deliver(direction)
            for speed in self.speed_queue:
                print "Windspeed"
                print time.localtime(speed.get_time())
                self.speed_queue.remove(speed)
                self.speed.deliver(speed)
        self.ws_queue_lock.release()
        return self.running

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Wind Speed", WindSpeed)

