from ScandalWidgets import *
import pygtk
import gtk
import Driver
import Configurator
import time
import gobject
import os

import pystrategy

import Graphing
import GraphingMPL

import numpy

class Strategy(Driver.Driver):
    def __init__(self, sa, config, name):
        Driver.Driver.__init__(self, sa, config, name)

        if "course_file" not in config:
            config["course_file"] = "../data/wsc/Road.csv"

        if "stops_file" not in config:
            config["stops_file"] = "../data/wsc/Stops.csv"

        if "weather_file" not in config:
            config["weather_file"] = "../data/weather/theweather"

#        if "program" not in config:
#            config["program"] = "../strategy/strategy"
            
        if "gpsnode" not in config:
            config["gpsnode"] = "GPS"

        if "currentintnode" not in config:
            config["currentintnode"] = "Current Integrator"

        if "currentintchan" not in config:
            config["currentintchan"] = "Current Int"

        if "arraypnode" not in config:
            config["arraypnode"] = "Negsum"

        if "arraypchan" not in config:
            config["arraypchan"] = "Array Power"

            
        pystrategy.init(config["course_file"], \
                        config["stops_file"], \
                        config["weather_file"])


        self.graphs = []

        # Add the strategy notebook 
        self.notebook = gtk.Notebook()
        self.sa.add_notebook_page(self.get_display_name(), self.notebook)
        self.add_overview_graph();
        self.add_battery_page();
        self.add_array_page();
        self.add_mech_page();
        
        # Register for interesting channels 
        self.sa.store.register_for_channel(self.config["gpsnode"], "Latitude", self.deliver_lat)
        self.sa.store.register_for_channel(self.config["gpsnode"], "Longitude", self.deliver_lon)
        
        self.last_lat = None
        self.last_lon = None
        
        self.parse_courseprofile(config["course_file"])
        self.parse_stopsfile(config["stops_file"])
        
        # Set up the source and channels
        self.source = Driver.Source(sa.store, self.get_name())
        print self.get_name()
        self.chans = {}
        for name in self.profile.keys():
            self.chans[name] = Driver.Channel(self.source, name)

        self.latest_map_index = 0
        
        self.output_chans = None
        self.output = None
        
## FIXME: Add a plot for the expected motor power


    def add_overview_graph(self):
        # adding labels and text
        self.overview = page = gtk.VBox()

        
        graph = self.graph = GraphingMPL.Graph(  self.sa, 
                                    ylabel="Battery State of Charge (kWh)", 
                                    xlabel="Distance (km)", 
                                    maxupdate=1000)

        self.bsoc_series = Graphing.SeriesStatic(self.sa, [], [],
                                                        label="BSOC", 
                                                        format={"linewidth":2.0, "color":"blue"}) 
        self.alt_series = Graphing.SeriesStatic(self.sa, [], [],
                                                        label="Altitude", 
                                                        format={"linewidth":1.0, "color":"green"})
        self.arrayp_series = Graphing.SeriesStatic(self.sa, [], [],
                                                        label="Array Power", 
                                                        format={"linewidth":1.0, "color":"magenta"})
                                                         
        graph.add_axis(axis=(1,2), ylabel="Speed (km/h)")
        graph.add_axis(axis=(1,3), ylabel="Power / Altitude")
        self.speed_series = Graphing.SeriesStatic(self.sa, [], [],
                                                        label="Speed", 
                                                        format={"linewidth":1.0, "color":"red"})  

        graph.add_series(self.bsoc_series, axis=(1,1) )
        graph.add_series(self.alt_series, axis=(1,3) )
        graph.add_series(self.arrayp_series, axis=(1,3) )
        graph.add_series(self.speed_series, axis=(1,2) )
    
        self.graphs.append(graph)
    
        page.pack_start(graph.get_widget(), expand=True)

        hbox = gtk.HBox()
        self.index_entry = gtk.Entry()
        hbox.pack_start(self.index_entry)
        self.index_entry.set_text("0")

        self.time_entry = gtk.Entry()
        hbox.pack_start(self.time_entry)
        self.time_entry.set_text("%f" % time.time())
        
        self.amphours_entry = gtk.Entry()
        hbox.pack_start(self.amphours_entry)
        self.amphours_entry.set_text("35")
        
        page.pack_start(hbox, expand=False)
        

        vbox = gtk.VBox()
        but = gtk.Button(label="Run Strategy")
        vbox.pack_end(but, expand=False)
        page.pack_start(vbox, expand=False)
        but.connect("clicked", self.run_strategy)
        
        self.notebook.append_page(page, gtk.Label(str="Overview"))
        
    def add_battery_page(self):
        # adding labels and text
        self.overview = page = gtk.VBox()

        
        graph =  GraphingMPL.Graph(  self.sa, 
                                    ylabel="Battery State of Charge (kWh)", 
                                    xlabel="Distance (km)", 
                                    maxupdate=1000)


        class adjusted_SeriesTime(Graphing.SeriesTime):
            def deliver(self, pkt):
                newvalue = 73.0 - pkt.get_value()
                newpkt = Driver.Deliverable(newvalue, timestamp=pkt.get_time())
                Graphing.SeriesTime.deliver(self, pkt)

        self.currentint_series = adjusted_SeriesTime(self.sa, \
													self.config["currentintnode"], \
                                                    self.config["currentintchan"], \
                                               label="Actual BSOC", \
                                              format={"color":"red"}) 

        self.expected_bsoc_series = Graphing.SeriesTime(self.sa, \
													self.get_name(), \
                                                    "strat_BSOC", \
                                               label="Expected BSOC", \
                                              format={"color":"blue"}) 


#        graph.add_series(self.bsoc_series2 )
        graph.add_series(self.currentint_series )
        graph.add_series(self.expected_bsoc_series )

        self.graphs.append(graph)

        page.pack_start(graph.get_widget())

        vbox = gtk.VBox()
        but = gtk.Button(label="Run Strategy")
        vbox.pack_end(but, expand=False)
        page.pack_start(vbox, expand=False)
        but.connect("clicked", self.run_strategy)
        
        self.notebook.append_page(page, gtk.Label(str="Battery"))

    def add_array_page(self):
        # adding labels and text
        self.overview = page = gtk.VBox()

        
        graph =  GraphingMPL.Graph(  self.sa, 
                                    ylabel="Array Power (W)", 
                                    xlabel="Distance (km)", 
                                    maxupdate=1000)
                                    
        self.actual_array_series = Graphing.SeriesTime(self.sa, \
													"Negsum", \
                                                    "Array Power", \
                                               label="Actual Array Power", \
                                              format={"color":"red"}) 

        self.expected_arraypower_series = Graphing.SeriesTime(self.sa, \
													self.get_name(), \
                                                    "strat_ArrayP_weather", \
                                               label="Expected BSOC", \
                                              format={"color":"blue"}) 

        graph.add_series(self.actual_array_series )
        graph.add_series(self.expected_arraypower_series )

        self.graphs.append(graph)

        page.pack_start(graph.get_widget())

        vbox = gtk.VBox()
        but = gtk.Button(label="Run Strategy")
        vbox.pack_end(but, expand=False)
        page.pack_start(vbox, expand=False)
        but.connect("clicked", self.run_strategy)
        
        self.notebook.append_page(page, gtk.Label(str="Array"))


    def add_mech_page(self):
        # adding labels and text
        self.overview = page = gtk.VBox()
        
        graph =  GraphingMPL.Graph(  self.sa, 
                                    ylabel="Power (W)", 
                                    xlabel="Time (s)", 
                                    maxupdate=1000)

        motorp_time_series = Graphing.SeriesTime(self.sa, "Negsum", "Motor Power", \
                                               label="Motor Power", \
                                              maxtimediff=600.0, \
                                              format={"color":"red"})
                                               
        exp_motorp_time_series = Graphing.SeriesTime(self.sa, self.get_name(), "strat_Mech_Power", \
                                               label="Expected Motor Power", \
                                              maxtimediff=600.0, \
                                              format={"color":"blue"}) 

        graph.add_series(motorp_time_series )
        graph.add_series(exp_motorp_time_series )

        self.graphs.append(graph)

        page.pack_start(graph.get_widget())

        vbox = gtk.VBox()
        but = gtk.Button(label="Run Strategy")
        vbox.pack_end(but, expand=False)
        page.pack_start(vbox, expand=False)
        but.connect("clicked", self.run_strategy)
        
        self.notebook.append_page(page, gtk.Label(str="Mech"))

        


    def run_strategy(self, widget):
#        try:
#            os.system(self.config["program"] + " " + \
#                        self.config["course_file"] + " " +\
#                        self.config["stops_file"] + " " +\
#                        self.config["weather_file"])
#        except:
#            self.sa.console.write("Could not run strategy program", mod=self)
#            return

        print "Time Entry:"
        
        runfrom_time = float( self.time_entry.get_text() )
        runfrom_index = int(self.index_entry.get_text() )
        runfrom_amphours = float(self.amphours_entry.get_text() )

#        pystrategy.run(runfrom_index, runfrom_time, runfrom_amphours)
#        pystrategy.print_data()
    
        try:
            outfile = open("output.dat", "r")
        except IOError:
            sa.console.write("Could not open output file: %s" % "output.dat", mod=self)
            return

        output = {}
        fieldnames = []
        counter = 0

        for line in outfile:
            # If it is the first line, we use it as headers
            if counter == 0:
                line = line.strip()
                fieldnames = line.split(",")
                for field in fieldnames:
                    output[field] = []

            else:
                # Ignore lines that start with #
                if line[0] == '#':
                    continue

                values = line.split(",")
                valuedict = dict(zip(fieldnames, values))

                for field in fieldnames:
                    output[field].append(float(valuedict[field]))

            counter = counter + 1
        outfile.close()
        
        self.bsoc_series.set_xpoints(output["Chainage"])
        self.bsoc_series.set_ypoints(output["BSOC"])
        
        self.alt_series.set_xpoints(output["Chainage"])
        self.alt_series.set_ypoints(output["Altitude"])

        self.speed_series.set_xpoints(output["Chainage"])
        self.speed_series.set_ypoints(output["Speed"])

        self.arrayp_series.set_xpoints(output["Chainage"])
        self.arrayp_series.set_ypoints(output["ArrayP_weather"])
        
        for graph in self.graphs:
            graph.flag_update();
        
        self.output = output
        if self.output_chans is None:
            self.output_chans = {}
            for name in self.output.keys():
                self.output_chans[name] = Driver.Channel(self.source, "strat_" + name)
            


    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("program", self.config, "Strategy program location")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("course_file", self.config, "File Location (Course Profile)")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("stops_file", self.config, "File Loctaion (Stops)")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("weather_file", self.config, "File Loctaion (Weather)")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("gpsnode", self.config, "GPS Node")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("currentintnode", self.config, "Current Int Node")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("currentintchan", self.config, "Current Int Channel")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("arraypnode", self.config, "Array Power Node")
        w.pack_start(e, expand = False)

        e = Configurator.TextConfig("arraypchan", self.config, "Array Power Channel")
        w.pack_start(e, expand = False)
                
        return widg

    def deliver_lat(self, pkt):
        if self.last_lat is None:
            self.last_lat = pkt 
            return;
            
        if pkt.get_time() > self.last_lat.get_time():
            self.last_lat = pkt
            self.new_latlong()
        
    def deliver_lon(self, pkt):
        if self.last_lon is None:
            self.last_lon = pkt 
            return;
            
        if pkt.get_time() > self.last_lon.get_time():
            self.last_lon = pkt
            self.new_latlong()
        
    def update_latest_position(self, latest_map_index):
        self.latest_map_index = latest_map_index
        deliv_time = self.last_lat.get_time()
        for name in self.profile.keys():
            self.chans[name].deliver(Driver.Deliverable(\
                self.profile[name][latest_map_index], \
                timestamp=deliv_time))
#            self.chans[name].deliver(Driver.Deliverable(
#                self.profile[name][latest_map_index], 
#                timestamp=deliv_time))

        if self.output_chans is not None:
            for chan in self.output_chans.keys():
                print "Output,keys()"
                print self.output.keys()
                
                hack_index = len(self.profile["Latitude"])
                hack_index -= len(self.output["Time"])

                out_index = self.latest_map_index - hack_index
                                
                self.output_chans[chan].deliver(Driver.Deliverable(\
                    self.output[chan][out_index], \
                    timestamp=deliv_time))
                                        

    def new_latlong(self):
        if self.last_lat is None:
            return
        if self.last_lon is None: 
            return
                        
        # If the latitude and longitude numbers are close together... Update everything.
        if abs(self.last_lon.get_time() - self.last_lat.get_time()) >= 0.5:
            return
        
        # If we get here we've got a match
        cur_lat = self.last_lat.get_value() / 60.0
        cur_long = self.last_lon.get_value() / 60.0
        
        # Use the pystrategy map. 
        latest_map_index = pystrategy.map_lookup(cur_lat, cur_long)
        self.latest_map_index = latest_map_index
                
        self.update_latest_position(latest_map_index)
                
    def parse_courseprofile(self, filename):
    	#reads and adjusts the settings according to the course profile
        counter = 0

        try:
            cp = open(filename, "r")
        except IOError:
            sa.console.write("Could not open course file: %s" % \
                                 filename, mod=self)
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
        
        #Keep the profile around for later
        newprofile = {}
        for key in profile:
            newprofile[key] = numpy.array(profile[key])
        self.profile = newprofile


    def parse_stopsfile(self, filename):
        ### Read the stops file
        counter = 0

        try:
            stopsfile = open(filename, "r")
        except IOError:
            sa.console.write("Could not open stops file: %s" % \
                                 filename, mod=self)
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

        self.stops = stops

    

def stop(self):
    Driver.Driver.stop(self)
    self.sa.remove_notebook_page(self.page)
    
    

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Strategy", Strategy)
