import Driver
import gobject
import time
import math
import gtk
import Configurator
import serial
import thread
import time
import datetime

class GPS(Driver.Driver):
    def __init__(self, sa, config, \
                     name="GPS"):
        Driver.Driver.__init__(self, sa, config, name)
        
        # Default configuration
        # Check to see if we don't have sourcename, 
        # which we should. 
        if "port" not in config:
            config["port"] = "/dev/ttyS0"

        self.source = Driver.Source(sa.store, self.get_name())
        self.chan_time = Driver.Channel(self.source, "Time")
        self.chan_lat = Driver.Channel(self.source, "Latitude")
        self.chan_long = Driver.Channel(self.source, "Longitude")
        self.chan_alt = Driver.Channel(self.source, "Altitude")
        self.chan_speed = Driver.Channel(self.source, "Speed")
        self.chan_direction = Driver.Channel(self.source, "Direction")
        self.chan_numsats = Driver.Channel(self.source, "Satelites")
        self.chan_hdop = Driver.Channel(self.source, "HDOP")
        self.chan_vpdop = Driver.Channel(self.source, "VPDOP")
        self.chan_horiz_err = Driver.Channel(self.source, "Horiz Err")
        self.chan_vert_err = Driver.Channel(self.source, "Vert Err")

        self.queue_lock = thread.allocate_lock()
        self.time_queue = []
        self.lat_queue = []
        self.long_queue = []
        self.alt_queue = []
        self.speed_queue = []
        self.direction_queue = []
        self.numsats_queue = []
        self.hdop_queue = []
        self.vpdop_queue = []
        self.horiz_err_queue = []
        self.vert_err_queue = []

        self.worker_thread = thread.start_new_thread(self.worker, () )

        gobject.timeout_add(500, self.dequeue_packets)
        
    def dequeue_packets(self):
        self.queue_lock.acquire()

        while len(self.time_queue) > 0:
            self.chan_time.deliver(self.time_queue.pop(0))
        while len(self.lat_queue) > 0:
            self.chan_lat.deliver(self.lat_queue.pop(0))
        while len(self.long_queue) > 0:
            self.chan_long.deliver(self.long_queue.pop(0))
        while len(self.alt_queue) > 0:
            self.chan_alt.deliver(self.alt_queue.pop(0))
        while len(self.speed_queue) > 0:
            self.chan_speed.deliver(self.speed_queue.pop(0))    
        while len(self.direction_queue) > 0:
            self.chan_direction.deliver(self.direction_queue.pop(0))    
        while len(self.hdop_queue) > 0:
            self.chan_hdop.deliver(self.hdop_queue.pop(0))    
        while len(self.vpdop_queue) > 0:
            self.chan_vpdop.deliver(self.vpdop_queue.pop(0))    
        while len(self.numsats_queue) > 0:
            self.chan_numsats.deliver(self.numsats_queue.pop(0))    
        while len(self.horiz_err_queue) > 0:
            self.chan_horiz_err.deliver(self.horiz_err_queue.pop(0))    
        while len(self.vert_err_queue) > 0:
            self.chan_vert_err.deliver(self.vert_err_queue.pop(0))    

        self.queue_lock.release()

        return self.running

    def worker(self):
        while self.running:
            try:
                self.ser = serial.Serial(self.config["port"], 9600)
                break
            except:
                self.sa.console.write("Could not open serial port -- %s, retrying" % self.config["port"],\
                                          mod=self)
                time.sleep(1)

        while self.running:
            line = self.ser.readline()

#            try:
            if True:
                # Get rid of the checksum
                tokens = line.split('*')
                if len(tokens) < 1:
                    self.sa.console.write("Got a bad NMEA message (blank line)", mod=self)
                    continue

                tokens = tokens[0].split(',')
                if len(tokens) < 1:
                    self.sa.console.write("Got a bad NMEA message (no commas)", mod=self)
                    continue

                if len(tokens[0]) < 1:
                    self.sa.console.write("Got a bad NMEA message (no real data)", mod=self)
                    continue 

                if tokens[0][0] != '$':
                    self.sa.console.write("Got a bad NMEA message (no $)", mod=self)
                    continue

                if tokens[0] == "$GPGSA":
                    #               fix = int(tokens[2])
                    #               satcount = 0
                    #               for i in range(3,15):
                    #                   if tokens[i] != "":
                    #                       satcount = satcount + 1
                    #               pdop = float(tokens[15])
                    #               horizpdop = float(tokens[16])
                    
                    if tokens[17] == "":
                        #self.sa.console.write("Empty VPDOP in GPGSA message -- no lock?", mod=self)
                        continue
                        
                    vertpdop = float(tokens[17])
                    
                    self.queue_lock.acquire()
                    self.vpdop_queue.append(Driver.Deliverable(vertpdop))
                    self.queue_lock.release()
               
                elif tokens[0] == "$PGRME":
                    if tokens[1] == "": 
                        #self.sa.console.write("Empty horizontal error in PGRME message -- no lock?", mod=self)
                        continue
                    if tokens[3] == "": 
                        #self.sa.console.write("Empty vertical error in PGRME message -- no lock?", mod=self)
                        continue
                        
                    est_horiz_err = float(tokens[1])
                    est_vert_err = float(tokens[3])
                    
                    self.queue_lock.acquire()
                    self.horiz_err_queue.append(Driver.Deliverable(est_horiz_err))
                    self.vert_err_queue.append(Driver.Deliverable(est_vert_err))
                    self.queue_lock.release()

    #            elif tokens[0] == "$PGRMZ":
    #                alt_feet = float(tokens[1])

                elif tokens[0] == "$GPRMC":
                    timestr = tokens[1]
                    mytime = 3600.0 * float(timestr[0:2]) + \
                        60.0 * float(timestr[2:4]) + \
                        1.0  * float(timestr[4:6])
 
                    status = tokens[2]
                    if status != "A":
                        continue

                    # Latitude  is in the format: 3356.052
                    # Which is 33 degrees and 56.052 minutes
                    # We output in minutes. 
                    latstr = tokens[3]
                    lattoks = latstr.split(".")
                    befdec = lattoks[0]
                    lat = 60.0 * float(befdec[0:-2]) + float(befdec[-2:]) + float("." + lattoks[1])
                    if tokens[4] == "S":
                        lat = -lat

                    # Longitude is in a similar format to latitude. 
                    longstr = tokens[5]
                    longtoks = longstr.split(".")
                    befdec = longtoks[0]
                    long = 60.0 * float(befdec[0:-2])
                    long += float(befdec[-2:])
                    long += float("." + longtoks[1])
                    if tokens[6] == "W":
                        long = -long

                    # Speed -- convert from knots
                    speed = float(tokens[7]) * 1.85200

                    # Track angle
                    direction = float(tokens[8])

                    # Date
                    datestr = tokens[9]

                    mytime = time.mktime(time.strptime(timestr + datestr, "%H%M%S%d%m%y"))
                    mytime -= time.timezone #mktime returns local time -- convert to UTC
                    
                    thetime = time.time()

                    self.queue_lock.acquire()
                    self.time_queue.append(Driver.Deliverable(mytime, timestamp=thetime))
                    self.lat_queue.append(Driver.Deliverable(lat, timestamp=thetime))
                    self.long_queue.append(Driver.Deliverable(long, timestamp=thetime))
                    self.speed_queue.append(Driver.Deliverable(speed, timestamp=thetime))
                    self.direction_queue.append(Driver.Deliverable(direction, timestamp=thetime))
                    self.queue_lock.release()

                elif tokens[0] == "$GPGGA":
                    # Latitude  is in the format: 3356.052
                    # Which is 33 degrees and 56.052 minutes
                    # We output in minutes. 
                    latstr = tokens[2]
                    lattoks = latstr.split(".")
                    befdec = lattoks[0]
                    if befdec[0:-2] == "" or \
                        befdec[-2:] == "" or \
                        lattoks[1] == "":
                        return
                    lat = 60.0 * float(befdec[0:-2]) + float(befdec[-2:]) + float("." + lattoks[1])
                    if tokens[3] == "S":
                        lat = -lat

                    # Longitude is in a similar format to latitude. 
                    longstr = tokens[4]
                    longtoks = longstr.split(".")
                    befdec = longtoks[0]
                    long = 60.0 * float(befdec[0:-2])
                    long += float(befdec[-2:])
                    long += float("." + longtoks[1])
                    if tokens[5] == "W":
                        long = -long

                    # Number of satelites
                    numsats = int(tokens[7])

                    # Horiz DOP
                    hdop = float(tokens[8])

                    # Altitude
                    alt = float(tokens[9])

                    self.queue_lock.acquire()
                    self.lat_queue.append(Driver.Deliverable(lat))
                    self.long_queue.append(Driver.Deliverable(long))
                    self.hdop_queue.append(Driver.Deliverable(hdop))
                    self.numsats_queue.append(Driver.Deliverable(numsats))
                    self.alt_queue.append(Driver.Deliverable(alt))

                    self.queue_lock.release()
                    

                else:
                    continue            
#            except:
#                self.sa.console.write("Caught an exception in the NMEA parsing code. Trying again.", mod=self)


    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("GPS", GPS)

