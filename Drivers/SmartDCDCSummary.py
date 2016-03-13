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

class SmartDCDCSummary(Driver.Driver):
    def __init__(self, sa, config, name="SmartDCDC"):      
        Driver.Driver.__init__(self, sa, config, name)
        self.page = page = gtk.HBox()

        if "nodename" not in config:
            config["nodename"] = self.get_name()

        nodename = config["nodename"]

        col1 = gtk.VBox()
        page.pack_start(col1, expand=False)
        col2 = gtk.VBox()
        page.pack_start(col2)

### Voltage Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Voltage (V)",\
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, nodename, "Batt Voltage", \
                                               label="Battery Voltage", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, nodename, "Wavesculptor Voltage", \
                                               label="Wavesculptor Voltage", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)

## Ignition channel
        ignition = ScandalWidgets.ChannelWidget(self.sa, 123, 456, nodename, default="789", label="Ignition")
        col1.pack_start(ignition)

## Relay channel
	relay = ScandalWidgets.ChannelWidget(self.sa, 12, 5, nodename, default="0", label="Relay")
        col1.pack_start(relay)
	
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
Driver.modfac.add_type("SmartDCDCSummary", SmartDCDCSummary)
