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

class EfficiencyBuddy(Driver.Driver):
    def __init__(self, sa, config, name="EfficiencyBuddy"):      
        Driver.Driver.__init__(self, sa, config, name)
        self.page = page = gtk.VBox()

        if "nodename" not in config:
            config["nodename"] = self.get_name()

        nodename = config["nodename"]

        self.values = {"InV":None, "InI":None, "OutV":None, "OutI":None}

#        col1 = gtk.VBox()
#        page.pack_start(col1, expand=False)
#        col2 = gtk.VBox()
#        page.pack_start(col2)

        graph = self.graph = GraphingMPL.Graph(  self.sa, 
                                    ylabel="Efficiency (%)", 
                                    xlabel="Time (s)", 
                                    maxupdate=1000)

        self.timeseries = Graphing.SeriesTime(self.sa, None, None, maxtimediff=60.0,
                                              label="Efficiency", 
                                              format={"linewidth":2.0, "color":"blue"}) 
        graph.add_series(self.timeseries)

        page.pack_start(graph.get_widget())

        hbox = gtk.HBox()
        page.pack_start(hbox)
        self.avgeff_entry = gtk.Entry(max=8)
        self.avgeff_entry.set_editable(False)
        self.avgeff_entry.set_width_chars(6)
        label = gtk.Label(str="Average Efficiency")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        hbox.pack_start(label)
        hbox.pack_start(self.avgeff_entry)

        self.sa.add_notebook_page(self.get_display_name(), self.page)

        self.sa.store.register_for_channel(nodename, "Input Voltage", lambda pkt: self.deliver_value("InV", pkt))
        self.sa.store.register_for_channel(nodename, "Input Current", lambda pkt: self.deliver_value("InI", pkt))
        self.sa.store.register_for_channel(nodename, "Output Voltage", lambda pkt: self.deliver_value("OutV", pkt))
        self.sa.store.register_for_channel(nodename, "Output Current", lambda pkt: self.deliver_value("OutI", pkt))

    def deliver_value(self, value_name, pkt):
        self.values[value_name] = pkt
        theirtime = None
        for value in self.values: 
            if self.values[value] is None:
                return
            if theirtime is None:
                theirtime = self.values[value].get_time()
            elif self.values[value].get_time() != theirtime:
                return
        # If we get to here, we've got all the values for this sample. 
        inv = self.values["InV"].get_value()
        ini = self.values["InI"].get_value()
        outv = self.values["OutV"].get_value()
        outi = self.values["OutI"].get_value()

        efficiency = 100.0 * (outv * outi) / (inv * ini)

        self.timeseries.deliver(Driver.Deliverable(efficiency, timestamp=theirtime))

        py = self.timeseries.get_ypoints()
        avgeff = sum(py) / len(py)
        self.avgeff_entry.set_text(str(avgeff))


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
Driver.modfac.add_type("EfficiencyBuddy", EfficiencyBuddy)
