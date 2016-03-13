from ScandalWidgets import *
#from Calculate import *
import pygtk
import gtk
import Driver
import Configurator
import time
import gobject
import numpy

import pystrategy

import Graphing
import GraphingMPL

class CourseProfile(Driver.Driver):
    def __init__(self, sa, config, name):
	Driver.Driver.__init__(self, sa, config, name)

	if "course_file" not in config:
            config["course_file"] = "../data/M5/Road.csv"

        if "stops_file" not in config:
	    config["stops_file"] = "../data/M5/Stops.csv"

        if "nodename" not in config:
            config["nodename"] = "GPS"
        nodename = config["nodename"]

        self.last_lat = None
        self.last_long = None

    # Playing with pystrategy. 
	pystrategy.init(config["course_file"], config["stops_file"], "../data/weather/WSC.hires.031018.1200.tsd")

	#reads and adjusts the settings according to the course profile
	counter = 0

        try:
            cp = open(config["course_file"], "r")
        except IOError:
            sa.console.write("Could not open course file: %s" % \
                                 config["course_file"], mod=self)
            return

        profile = {}
        fieldnames = []

	for line in cp:
            # If it is the first line, we use it as headers
            if counter == 0:
                line = line.strip()
                fieldnames = line.split(",")
                for field in fieldnames:
                    profile[field] = []

            else:
                # Ignore lines that start with #
                if line[0] == '#':
                    continue

                values = line.split(",")
                valuedict = dict(zip(fieldnames, values))

                for field in fieldnames:
                    profile[field].append(float(valuedict[field]))

	    counter = counter + 1
	cp.close()

### Read the stops file
	counter = 0

        try:
            stopsfile = open(config["stops_file"], "r")
        except IOError:
            sa.console.write("Could not open stops file: %s" % \
                                 config["stops_file"], mod=self)
            return

        stops = {}
        stopsnames = []

        for line in stopsfile:
            # If it is the first line, we use it as headers
            if counter == 0:
                line = line.strip()
                stopsnames = line.split(",")
                for stopname in stopsnames:
                    stops[stopname] = []

            else:
                # Ignore lines that start with #
                if line[0] == '#':
                    continue

                values = line.split(",")
                valuedict = dict(zip(stopsnames, values))

                for stopname in stopsnames:
                    if stopname == "Label":
                        stops[stopname].append(valuedict[stopname].strip())
                    else:
                        stops[stopname].append(float(valuedict[stopname]))

	    counter = counter + 1
	stopsfile.close()

### Get on with things

        #Keep the profile around for later
        newprofile = {}
        for key in profile:
            newprofile[key] = numpy.array(profile[key])
        self.profile = newprofile
        self.stops = stops

        # Set the last known location to the start of the race 
        self.last_known_index = 0

        # Set up the source and channels
        self.source = Driver.Source(sa.store, self.get_name())
        self.chans = {}
        for name in fieldnames:
            self.chans[name] = Driver.Channel(self.source, name)

        # Set ourselves up for lat/long delivery
        self.sa.store.register_for_channel(nodename, "Latitude", 
                                           self.lat_deliver)
        self.sa.store.register_for_channel(nodename, "Longitude", 
                                           self.long_deliver)


	# adding labels and text
	self.page = page = gtk.HBox()

	col1 = gtk.VBox()
        page.pack_start(col1)
        col2 = gtk.VBox()
        page.pack_start(col2)

        # Set up the source
        

        # GPS coordinates
        class LabelIndicatorDiv60(LabelIndicator):
            def deliver(self, pkt):
                pktval = pkt.get_value() / 60.0
                pkttime = pkt.get_time()
                LabelIndicator.deliver(self, Driver.Deliverable(pktval, timestamp=pkttime))


        # Local class definition -- expects to be subscribed to the chainage. 
        class CompletedCourseIndicator(TextIndicator):
            def __init__(self, sa, profile, nodename, channame, **kwargs):
                TextIndicator.__init__(self, **kwargs)
                self.sa = sa
                self.sa.store.register_for_channel(nodename, channame, self.deliver)
                self.last_pkt = None
                self.profile = profile
                
            def deliver(self, pkt):
                if self.last_pkt is None:
                    self.last_pkt = pkt
                if pkt.get_time() > self.last_pkt.get_time():
                    self.last_pkt = pkt
                    completeKm = pkt.get_value()
                    completePercent = 100.0 * completeKm / self.profile["Chainage"][-1]
                    self.set_text("%.3fkm (%.1f%%)" % (completeKm, completePercent))

        # Course to go -- expects to be subscribed ot the chainage. 
        class CourseToGoIndicator(TextIndicator):
            def __init__(self, sa, profile, nodename, channame, **kwargs):
                TextIndicator.__init__(self, **kwargs)
                self.sa = sa
                self.sa.store.register_for_channel(nodename, channame, self.deliver)
                self.last_pkt = None
                self.profile = profile
                
            def deliver(self, pkt):
                if self.last_pkt is None:
                    self.last_pkt = pkt
                if pkt.get_time() > self.last_pkt.get_time():
                    self.last_pkt = pkt
                    toGoKm = self.profile["Chainage"][-1] - pkt.get_value()
                    toGoPercent = 100.0 * toGoKm / self.profile["Chainage"][-1]
                    self.set_text("%.3fkm (%.1f%%)" % (toGoKm, toGoPercent))#

        # End of day location
        class EndOfDayLocation(TextIndicator):
            def __init__(self, sa, nodename, **kwargs):
                TextIndicator.__init__(self, **kwargs)
                self.sa = sa
                self.sa.store.register_for_channel(nodename, "Chainage", self.deliverChainage)
                self.sa.store.register_for_channel("Motor Controller", "Speed", self.deliverSpeed)
                self.last_chainage_pkt = None
                self.last_speed_pkt = None

            def deliverSpeed(self, pkt):
                if self.last_speed_pkt is None:
                    self.last_speed_pkt = pkt
                elif self.last_speed_pkt.get_time() < pkt.get_time():
                    self.last_speed_pkt = pkt
                
            def deliverChainage(self, pkt):
                if self.last_chainage_pkt is None:
                    self.last_chainage_pkt = pkt
                if pkt.get_time() > self.last_chainage_pkt.get_time():
                    self.last_chainage_pkt = pkt
                
                if self.last_chainage_pkt is None:
                    return
                if self.last_speed_pkt is None: 
                    return

                # If the last speed and chainage are less than 1s apart
                if abs(self.last_chainage_pkt.get_time() - self.last_speed_pkt.get_time()) < 1.0: 
                    # Get the present time
                    componentTime = list(time.localtime(self.last_chainage_pkt.get_time()))
                    
                    # Work out when the end of the day is -- 5:00PM
                    componentTime[3] = 17
                    componentTime[4] = 0
                    componentTime[5] = 0
                    endOfDayTime = time.mktime(componentTime)
                    
                    # Calculate the number of seconds to go (note: does not include stops of any kind)
                    timeUntilEndOfDay = endOfDayTime - self.last_chainage_pkt.get_time()

                    # Calculate the distange that will be covered at the present speed
                    speed = self.last_speed_pkt.get_value()
                    hours = timeUntilEndOfDay / 3600.0 # Convert to hours
                    distance = speed * hours
                    
                    # Calculate the start of the window -- the end of the window is at 5:10PM
                    windowStart = self.last_chainage_pkt.get_value() + distance
                    windowEnd = windowStart + speed * (10.0 / 60.0)

                    # Put the text together
                    self.set_text("Between %.1fkm and %.1fkm" % (windowStart, windowEnd))

### Next stop
        class NextStopName(TextIndicator):
            def __init__(self, sa, stops, nodename, **kwargs):
                TextIndicator.__init__(self, **kwargs)
                self.sa = sa
                self.last_chainage_pkt = None
                self.last_speed_pkt = None
                self.profile = profile
                self.stops = stops
                self.sa.store.register_for_channel(nodename, "Chainage", self.deliverChainage)
                self.sa.store.register_for_channel("Motor Controller", "Speed", self.deliverSpeed)


            def deliverSpeed(self,pkt):
                if self.last_speed_pkt is None:
                    self.last_speed_pkt = pkt
                if pkt.get_time() > self.last_speed_pkt.get_time():
                    self.last_speed_pkt = pkt

            def deliverChainage(self, pkt):
                if self.last_chainage_pkt is None:
                    self.last_chainage_pkt = pkt
                if pkt.get_time() > self.last_chainage_pkt.get_time():
                    self.last_chainage_pkt = pkt
                    
                if self.last_chainage_pkt is None:
                    return
                if self.last_speed_pkt is None:
                    return
                
#                if abs(self.last_speed_pkt.get_time() - \
#                           self.last_chainage_pkt.get_time()) < 1.0:
                if True:
                    chainage = self.last_chainage_pkt.get_value()
                    
                    for i in range(len(self.stops.keys()[0])):
                        if chainage <= self.stops["Chainage"][i]:
                            break

                    distance = self.stops["Chainage"][i] - chainage
                    speed = self.last_speed_pkt.get_value()

                    if speed > 0.01:
                        time_to_stop = "%.2f" %(distance / speed)
                    else:
                        time_to_stop = "inf"

                    self.set_text("%s (%.1fkm, %sh)" % \
                                      (self.stops["Label"][i],\
                                           distance,\
                                           time_to_stop))

        class seriesxy_divided60(Graphing.SeriesXY):
            def xdeliver(self, pkt):
                pktval = pkt.get_value() / 60.0
                pkttime = pkt.get_time()
                Graphing.SeriesXY.xdeliver(self, Driver.Deliverable(pktval, timestamp=pkttime))
            def ydeliver(self, pkt):
                pktval = pkt.get_value() / 60.0
                pkttime = pkt.get_time()
                Graphing.SeriesXY.ydeliver(self, Driver.Deliverable(pktval, timestamp=pkttime))


        # Start adding things to the course. 

        widg = LabelIndicatorDiv60(sa.store, "GPS", "Latitude", "Latitude")
        col2.pack_start(widg, expand=False)
        widg = LabelIndicatorDiv60(sa.store, "GPS", "Longitude", "Longitude")
        col2.pack_start(widg, expand=False)

        # Lat long course profile
	widg = gtk.HSeparator()
        col2.pack_start(widg, expand=False)
        latlong_series = Graphing.SeriesStatic(self.sa, profile["Longitude"], 
                                               profile["Latitude"],
                                               label="Latitude vs. Longitude", 
                                               format={"linewidth":2.0, "color":"blue"}) 
        solarcar_location_series = seriesxy_divided60(
            self.sa, "GPS", "Longitude", 
            "GPS", "Latitude", 
            label = "Solar Car Location", 
            maxpoints=2, 
            format={"linewidth":1.0, "marker":"o", "color":"red"})
        latlong_stops = Graphing.SeriesStatic(self.sa, 
                                              stops["Longitude"], 
                                              stops["Latitude"],
                                              label="Stops",
                                              format={"color":"green", 
                                                      "marker":"o", 
                                                      "linestyle":"None"})

	graph = GraphingMPL.Graph(self.sa, \
                                           ylabel="Latitude", \
                                           xlabel="Longitude", \
                                  maxupdate=200)
        graph.add_annotation(stops["Longitude"], stops["Latitude"], 
                             stops["Label"])
        graph.add_series(latlong_series)
        graph.add_series(latlong_stops)
        graph.add_series(solarcar_location_series)


        col1.pack_start(graph.get_widget())

### Column 2
        widg = CompletedCourseIndicator(sa, self.profile, self.get_name(), "Chainage", label="Course Completed")
        col2.pack_start(widg, expand=False)

        widg = CourseToGoIndicator(sa, self.profile, self.get_name(), "Chainage", label="Course To Go")
        col2.pack_start(widg, expand=False)

  	widg = gtk.HSeparator()
        col2.pack_start(widg, expand=False)
        
        widg = LabelIndicator(sa.store, "Motor Controller", "Speed", label="Solar car speed", units="km/h")
        col2.pack_start(widg, expand=False)
        
        widg = EndOfDayLocation(sa, self.get_name(), label="End of day location")
        col2.pack_start(widg, expand=False)

        widg = NextStopName(sa, self.stops, self.get_name(), label="Next Stop")
        col2.pack_start(widg, expand=False)

# Altitude vs. Chainage graph. 

	graph = GraphingMPL.Graph(self.sa, 
                                  ylabel="Altitude (m)", 
                                  xlabel="Chainage (km)", 
                                  maxupdate=1000)
        altchainage_series = Graphing.SeriesStatic(self.sa, profile["Chainage"], 
                                               profile["Altitude"],
                                               label="Altitude vs. Chainage", 
                                               format={"linewidth":1.0, "color":"blue"}) 
        altchainage_location_series = Graphing.SeriesXY(
            self.sa, self.get_name(), "Chainage", 
            self.get_name(), "Altitude", 
            label = "Solar Car Location", 
            maxpoints=2, 
            format={"linewidth":2.0, "marker":"o", "color":"red"})
        altchainage_stops = Graphing.SeriesStatic(self.sa, 
                                              stops["Chainage"], 
                                              stops["Altitude"],
                                              label="Stops",
                                              format={"color":"green", 
                                                      "marker":"o", 
                                                      "linestyle":"None"})
        graph.add_annotation(stops["Chainage"], stops["Altitude"], 
                             stops["Label"], yoffset=10, format={})
        graph.add_series(altchainage_series)
        graph.add_series(altchainage_stops)
        graph.add_series(altchainage_location_series)

        col2.pack_start(graph.get_widget())




	self.sa.add_notebook_page(self.get_display_name(), page)






    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("course_file", self.config, "File Location (Course Profile)")
        w.pack_start(e, expand = False)

	e = Configurator.TextConfig("stops_file", self.config, "File Loctaion (Stops)")
	w.pack_start(e, expand = False)

        return widg

    def lat_deliver(self, pkt):
        if self.last_lat == None:
            self.last_lat = pkt
        elif self.last_lat.get_time() < pkt.get_time():
            self.last_lat = pkt
            self.gps_coord_deliver()

    def long_deliver(self, pkt):
        print pkt.get_value()
        if self.last_long == None:
            self.last_long = pkt
        elif self.last_long.get_time() < pkt.get_time():
            self.last_long = pkt
        self.gps_coord_deliver()

    def gps_coord_deliver(self):
        if self.last_lat == None: 
            return
        if self.last_long == None: 
            return
        if self.last_lat.get_time() == self.last_long.get_time():
            starttime = time.time()
            
            #lats = self.profile["Latitude"]
            #longs = self.profile["Longitude"]
        
            #min_i = self.last_known_index
            #min_distance = lats[min_i] * lats[min_i] + longs[min_i] * longs[min_i]

            cur_lat = self.last_lat.get_value() / 60.0
            cur_long = self.last_long.get_value() / 60.0

            # Use the pystrategy map. 
            min_i = pystrategy.map_lookup(cur_lat, cur_long)
        
            endtime = time.time()
            print "Did course profile lookup in %fs" % (endtime - starttime)
                    
#            for i in range(min_i, len(lats)):
#                lat = lats[i] - cur_lat
#                long = longs[i] - cur_long
#                distance = lat * lat + long * long
#                if min_distance > distance: 
#                    min_i = i
#                    min_distance = distance
#                elif distance < 1.0:
#                    print "Distance at %d is %f" % (i, distance)
#                    print "Distance at %d is %f" % (min_i, min_distance)
#                    ## Assume that we go forward along the race route
#                    self.last_known_index = i
#                    print "Found index %d" % i
#                    break
    

            deliv_time = self.last_lat.get_time()
            for name in self.profile.keys():
                self.chans[name].deliver(Driver.Deliverable(
                        self.profile[name][min_i], 
                        timestamp=deliv_time))
        
            

def stop(self):
    Driver.Driver.stop(self)
    self.sa.remove_notebook_page(self.page)

# Register our driver with the driver module's module factory
Driver.modfac.add_type("CourseProfile", CourseProfile)
