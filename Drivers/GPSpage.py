from ScandalWidgets import *

import gtk
import Driver
import Configurator

import Graphing
import GraphingMPL

class GPSpage(Driver.Driver):
    def __init__(self, sa, config, name="GPS Barometer 30"):
        Driver.Driver.__init__(self, sa, config, name)

        if "nodename" not in self.config:
            self.config["nodename"] = "GPS Barometer 30"

        nodename = self.config["nodename"]

        self.page = page = gtk.HBox()

        col1 = gtk.VBox()
        page.pack_start(col1)
	col2 = gtk.VBox()
	page.pack_start(col2)

        ### Latitude vs. Longitude plot
        graph = GraphingMPL.Graph(self.sa, 
                                  ylabel="Latitude", 
                                  xlabel="Longitude", 
                                  maxupdate=5000)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesXY(self.sa, nodename, "Longitude", 
                                   nodename, "Latitude", 
                                   label="Solar car position",  
                                   format={"color":"blue", "linewidth":1.0}) 
        graph.add_series(series)

        ### Altitude vs. Longitude plot
        graph = GraphingMPL.Graph(self.sa, 
                                  ylabel="Altitude", 
                                  xlabel="Longitude", 
                                  maxupdate=5000)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesXY(self.sa, nodename, "Longitude", 
                                   nodename, "Altitude", 
                                   label="Solar car altitude",  
                                   format={"color":"red", "linewidth":1.0}) 
        graph.add_series(series)

        # Add ourselves to the scanalysis notebook
        self.sa.add_notebook_page(self.get_display_name(), page)

    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page)

    # Overrides the Module version
    def configure(self):
        widg = Driver.Driver.configure(self)

        vbox = gtk.VBox()
        widg.pack_start(vbox)

        textconf = Configurator.TextConfig("nodename", self.config, "Node Name")
        vbox.pack_start(textconf, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("GPSpage", GPSpage)
