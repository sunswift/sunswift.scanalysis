import Driver
import Configurator

from Drivers import ScandalDriver

import Scandal
import ScandalWidgets

import Graphing
import GraphingMPL

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class TyreSummary(Driver.Driver):
    def __init__(self, sa, config, name="TyreDCDC"):      
        Driver.Driver.__init__(self, sa, config, name)
        self.page = page = gtk.HBox()

        if "nodename" not in config:
            config["nodename"] = self.get_name()

        nodename = config["nodename"]

        col1 = gtk.VBox()
        page.pack_start(col1)
        col2 = gtk.VBox()
        page.pack_start(col2)

### Pressure Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Pressure (kPa)",\
                                  maxupdate=500)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, nodename, "1 Pressure", \
                                               label="Wheel 1", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "2 Pressure", \
                                               label="Wheel 2", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "3 Pressure", \
                                               label="Wheel 3", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "4 Pressure", \
                                               label="Wheel 4", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)


### Temperature Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Temperature (deg C)",\
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, nodename, "1 Air Temperature", \
                                               label="Wheel 1", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "2 Air Temperature", \
                                               label="Wheel 2", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "3 Air Temperature", \
                                               label="Wheel 3", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "4 Air Temperature", \
                                               label="Wheel 4", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)

### Battery Voltage Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Battery Voltage (V)",\
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, nodename, "1 Battery Voltage", \
                                               label="Wheel 1", \
                                              maxtimediff=86400.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "2 Battery Voltage", \
                                               label="Wheel 2", \
                                              maxtimediff=86400.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "3 Battery Voltage", \
                                               label="Wheel 3", \
                                              maxtimediff=86400.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "4 Battery Voltage", \
                                               label="Wheel 4", \
                                              maxtimediff=86400.0) 
        graph.add_series(series)
	
        self.sa.add_notebook_page(self.get_display_name(), self.page)

    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page)

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("nodename", self.config, "Node Name")
        w.pack_start(e, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("TyreSummary", TyreSummary)
