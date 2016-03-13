from ScandalWidgets import *

import Driver
import Configurator

from Drivers import ScandalDriver

import Scandal

import Graphing
import GraphingMPL

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import time

class rolldownLogger:
    def __init__(self):
        self.enabled = False
        self.logfile = None
        self.log = {}
    def new_log(self, filename):
        if self.logfile is not None:
            self.logfile.close()
        self.logfile = open(filename, "w+")
    def enable(self):
        self.enabled = True
        for label in self.log.keys():
            self.log[label] = []
    def disable(self):
        self.enabled = False
        
    def add_label(self, label):
        self.log[label] = []

    def deliver(self, label, pkt):
        if self.logfile is None:
            return
        if self.enabled is False:
            return
        self.log[label].append( (pkt.get_time(), pkt.get_value()) )

    def write(self):
        # Presently only works for one label
        self.logfile.write("Time")
        labels = self.log.keys()
        labels.sort()
        for label in labels:
            self.logfile.write("," + label)
        self.logfile.write("\n")

        for label in labels:
            self.log[label].sort()

        # Should summarise and average the data here to re-align it
        primary = "Speed"        
        (time0, value0) = self.log[primary][0]        
        print "First timestamp was: " + str(time0)

        while len(self.log[primary]) > 0:
            values = {}
            (thistime,thisvalue) = self.log[primary][0]
            print "thistime is: %f"%(thistime-time0)

            self.logfile.write("%f"%(thistime-time0))

            for label in labels:
                if len(self.log[label]) == 0:
                    writeval = None
                else:
                    (labtime, labval) = self.log[label][0]
                    if labtime == thistime: 
                        writeval = labval
                    else:
                        if len(self.log[label]) > 1:
                            while len(self.log[label]) > 1:
                                (nexttime, nextval) = self.log[label][1]
                                if nexttime < thistime:
                                    del self.log[label][0]
                                    continue
                                else:
                                    break;
                        
                            if labtime < thistime and thistime < nexttime:
                                writeval = labval + (nextval - labval) * (nexttime - thistime) / (nexttime - labtime)
                            else:
                                writeval = None
                        else:
                            writeval = None

                if writeval == None:
                    self.logfile.write(",")
                else:
                    self.logfile.write(",%f"%writeval)
                
            del self.log[primary][0]
            self.logfile.write("\n")
                
        self.logfile.flush()

class rolldownSeries(Graphing.SeriesTime):
    def __init__(self, sa, nodename, channelname, label, logger, **kwargs):
        Graphing.SeriesTime.__init__(self, sa, nodename, channelname, **kwargs)
        self.logger = logger
        self.label = label
        self.enabled = False
        self.firstPkt = None
        self.lastPkt = None
        
        self.logger.add_label(label)

    def enable(self):
        Graphing.SeriesTime.enable(self)
        self.firstPkt = None
        self.lastPkt = None

    def deliver(self, pkt):
        if self.enabled is False:
            return
        if self.firstPkt is None:
            self.firstPkt = pkt
        if self.lastPkt is None:
            self.lastPkt = pkt
        if self.lastPkt.get_time() > pkt.get_time():
            return
        self.logger.deliver(self.label, pkt)
        timestamp = pkt.get_time() - self.firstPkt.get_time()
        newpkt = Driver.Deliverable(pkt.get_value(), timestamp=timestamp)
        Graphing.SeriesTime.deliver(self, newpkt)
    

class Rolldown(gtk.VBox):
    def dorun(self, button):
        if self.running == False:
            for series in self.logseries:
                series.clear()
                
            (year,mon,day,hour,minute,second,_,_,_) = time.gmtime()
            myfilename = "rolldown_%04d%02d%02d_%02d%02d%02d.csv"%(year,mon,day,hour,minute,second)
            self.logger.new_log(myfilename)
    
            self.logger.enable()
            for series in self.logseries:
                series.enable()
            self.go_button.set_label("Stop")
            
            self.running = True

            self.vmin.set_text("")
            self.vmax.set_text("")

        else:
            self.logger.disable()

            data = self.logger.log["Speed"]
            times,values = zip(*data)
            # These statements seem to cause a beep. Why!?!?
            self.vmin.set_text("%.03f" % min(values))
            self.vmax.set_text("%.03f" % max(values))

            self.logger.write()
            for series in self.logseries:
                series.disable()
            self.go_button.set_label("Start")
            self.running = False
            
            
        
    def __init__(self, sa):
        gtk.VBox.__init__(self)

        print "INitialising with " + str(sa)

        self.sa = sa
        self.running = False

        rollplot = GraphingMPL.Graph(self.sa, \
                                       xlabel="Time (s)", \
                                       ylabel="Speed (km/h)", 
                                        maxupdate=200)
                                        
        self.logger = rolldownLogger()
        self.logseries = []
        self.speedSeries = rolldownSeries(sa, "SteeringWheel", "Speed", "Speed", self.logger)
        self.logseries.append(self.speedSeries)
#        self.speedSeries = rolldownSeries(sa, "Messages", "Packet Rate", "Speed", self.logger)
        self.modelSeries = Graphing.SeriesStatic(self.sa, [], [], label="Model", format={"color":"green", "linewidth":2.0})

        self.latSeries = rolldownSeries(sa, "GPS", "Latitude", "Latitude", self.logger)
        self.logseries.append(self.latSeries)
        self.longSeries = rolldownSeries(sa, "GPS", "Longitude", "Longitude", self.logger)
        self.logseries.append(self.longSeries)
        self.windspeedSeries = rolldownSeries(sa, "WindSpeed", "Speed", "WindSpeed", self.logger)
        self.logseries.append(self.windspeedSeries)
        self.winddirSeries = rolldownSeries(sa, "WindSpeed", "Direction", "WindDirection", self.logger)
        self.logseries.append(self.winddirSeries)
        self.yaxisSeries = rolldownSeries(sa, "Tilt Sensor", "Y-axis", "TiltY", self.logger)
        self.logseries.append(self.yaxisSeries)
        self.xaxisSeries = rolldownSeries(sa, "Tilt Sensor", "X-axis", "TiltX", self.logger)
        self.logseries.append(self.xaxisSeries)
        self.motorCurrentSeries = rolldownSeries(sa, "Negsum", "Battery Current", "MotorCurrent", self.logger)
        self.logseries.append(self.motorCurrentSeries)

        rollplot.add_series(self.speedSeries)
        rollplot.add_series(self.windspeedSeries)

        rollplot.add_series(self.modelSeries)
        self.pack_start(rollplot.get_widget())

        # Display values generated by the sweep
        frame = gtk.Frame(label="Analysis")
        self.pack_start(frame, expand=False)

        bigbox = gtk.VBox()
        frame.add(bigbox)
        
        box = gtk.HBox()
        bigbox.pack_start(box, expand=False)

        self.vmax = gtk.Entry(max=8)
        self.vmax.set_editable(False)
        self.vmax.set_width_chars(15)
        label = gtk.Label(str="Vmax")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        box.pack_start(label)
        box.pack_start(self.vmax)

        self.vmin = gtk.Entry(max=8)
        self.vmin.set_editable(False)
        self.vmin.set_width_chars(15)
        label = gtk.Label(str="Vmin")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        box.pack_start(label)
        box.pack_start(self.vmin)

        # Button
        go = gtk.Button(label="Start")
        self.go_button = go
        self.pack_start(go, expand=False)

        go.connect("clicked", self.dorun)


class RolldownSummary(Driver.Driver):
    def __init__(self, sa, config, name="Rolldown"):      
        Driver.Driver.__init__(self, sa, config, name)
        self.page = page = gtk.HBox()

        col1 = gtk.VBox()
        page.pack_start(col1, expand=False)
        col2 = gtk.VBox()
        page.pack_start(col2)

### Speed graph
        graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Speed (km/h)",\
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        graph.add_axis(axis=(1,2), ylabel="Altitude")


        series = Graphing.SeriesTime(self.sa, "SteeringWheel", "Speed", \
                                               label="Speed", \
                                              maxtimediff=120.0) 
        graph.add_series(series)

        series = Graphing.SeriesTime(self.sa, "Tilt Sensor", "Y-axis", \
                                               label="TiltY", \
                                              maxtimediff=120.0) 
        graph.add_series(series)#, axis=(1,2)   )

        series = Graphing.SeriesTime(self.sa, "Tilt Sensor", "X-axis", \
                                               label="TiltX", \
                                              maxtimediff=120.0) 
        graph.add_series(series)#, axis=(1,2))

        series = Graphing.SeriesTime(self.sa, "GPS", "Speed", \
                                               label="GPS Speed", \
                                              maxtimediff=120.0) 
        graph.add_series(series)

        series = Graphing.SeriesTime(self.sa, "GPS", "Altitude", \
                                               label="GPS Altitude", \
                                              maxtimediff=120.0) 
        graph.add_series(series, axis=(1,2))


        rolldown = Rolldown(sa)
        col1.pack_start(rolldown)

        self.sa.add_notebook_page(self.get_display_name(), self.page)

    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page)

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Rolldown", RolldownSummary)
