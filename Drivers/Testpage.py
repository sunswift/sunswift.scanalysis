from ScandalWidgets import *
import Driver
import Misc
import Console
import Car3D
import Configurator

import Graphing
import GraphingMPL

# This is just a spot to try things out without having to create new files, etc. 

class Testpage(Driver.Driver):
    def __init__(self, sa, config, name="Test"):
        Driver.Driver.__init__(self, sa, config, name)

        self.page = page = gtk.HBox()

        if "car_model_file" not in config:
            config["car_model_file"] = "../data/cars/ss4/aero_model.stl"

    
        col1 = gtk.VBox()
        page.pack_start(col1)

### A Graph
        graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Voltage (ADC Reading)",
                                  title="Voltage",
                                  maxupdate=300)
        series = Graphing.SeriesTime(self.sa, "BMS", "3 Voltage", \
                                               label="3 Voltage", \
                                              maxtimediff=60.0, \
                                              format={"color":"blue"}) 
        graph.add_series(series)
        series = Graphing.SeriesTime(self.sa, "BMS", "2 Voltage", \
                                               label="2 Voltage", \
                                              maxtimediff=60.0, \
                                              format={"color":"blue"}) 
        graph.add_series(series)
        col1.pack_start(graph.get_widget())


#       myframe = gtk.Frame(label = "3D Car")
#        col1.pack_start(myframe, expand=True)

#        car = Car3D.Car3D(config["car_model_file"])
#        myframe.add(car)

        col2 = gtk.VBox()
        page.pack_start(col2)

        myframe = gtk.Frame(label = "Race Log")
        col2.pack_start(myframe, expand=True)

        racelog = gtk.VBox()
        myframe.add(racelog)

        self.logview = Console.Console(self.sa)
        racelog.pack_start(self.logview, expand=True)

        logentry = Misc.ManualEntry(self.sa, "Log Entry")
        racelog.pack_start(logentry, expand=False)

        self.sa.store.register_for_channel("Log Entry", "name", \
                                               lambda x: self.logview.deliver("Log Entry", x))

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

        textconf = Configurator.TextConfig("car_model_file", self.config, "Car Model File")
        vbox.pack_start(textconf, expand=False)
    
        return widg


# Register our driver with the driver module's module factory
Driver.modfac.add_type("Testpage", Testpage)
