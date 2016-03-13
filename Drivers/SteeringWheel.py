from ScandalWidgets import *

import Driver
import Configurator

from Drivers import ScandalDriver

import Scandal

import Graphing
import GraphingMPL

class SteeringWheel(Driver.Driver):
    def __init__(self, sa, config, name="SteeringWheel"):      
        Driver.Driver.__init__(self, sa, config, name)
        self.page = page = gtk.HBox()

        if "nodename" not in config:
            config["nodename"] = self.get_name()

        nodename = config["nodename"]

        col1 = gtk.VBox()
        page.pack_start(col1, expand=False)
        col2 = gtk.VBox()
        page.pack_start(col2)

### Speed Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Speed (km/h)",\
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, nodename, "Speed", \
                                               label="Speed", \
                                              maxtimediff=120.0, 
                                     format={"lw":2}) 
        graph.add_series(series)

### Current Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Current (A)",
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, nodename, "Current A", \
                                               label="Current B", \
                                         format={"lw":2},
                                              maxtimediff=120.0) 
        graph.add_series(series)

        series = Graphing.SeriesTime(self.sa, nodename, "Current B", \
                                               label="Current B", \
                                         format={"lw":2},
                                              maxtimediff=120.0) 
        graph.add_series(series)


        widg = ChannelWidget(sa, 10, 0, "SteeringWheel",
                             label="Velocity Setpoint")
        col1.pack_start(widg, expand=False)

        widg = ChannelWidget(sa, 10, 1, "SteeringWheel",
                             label="Current Setpoint")
        col1.pack_start(widg, expand=False)

        widg = ChannelWidget(sa, 10, 2, "SteeringWheel",
                             label="Bus Current Setpoint")
        col1.pack_start(widg, expand=False)

        box = gtk.HBox()
        col1.pack_start(box)
        
        frame = gtk.Frame(label="Velocity Setpoint")
        box.pack_start(frame, expand=True)
        widg = VScaleChannel(sa, 10, 0, "SteeringWheel",
                             label="Velocity Setpoint")
        frame.add(widg)

        frame = gtk.Frame(label="Current Setpoint")
        box.pack_start(frame, expand=True)
        widg = VScaleChannel(sa, 10, 1, "SteeringWheel",
                             label="Current Setpoint")
        frame.add(widg)

        frame = gtk.Frame(label="Bus Current Setpoint")
        box.pack_start(frame, expand=True)
        widg = VScaleChannel(sa, 10, 2, "SteeringWheel",
                             label="Bus Current Setpoint")
        frame.add(widg)

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
Driver.modfac.add_type("SteeringWheel", SteeringWheel)
