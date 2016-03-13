from ScandalWidgets import *
import Driver
import Graphing
import GraphingMPL

class Wind_Speed_Graph(Driver.Driver):
    def __init__(self, sa, config, name="Wind Speed"):
        Driver.Driver.__init__(self, sa, config, name)

        self.page = page = gtk.HBox()

        col1 = gtk.VBox()
        page.pack_start(col1)

        graph = GraphingMPL.Graph(self.sa, 
                                  xlabel="Time (s)", 
                                  ylabel="Speed (m/s)", 
                                  maxupdate=500)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, "Wind Speed", "Speed", \
                                         label="Speed", \
                                         maxtimediff=10.0, \
                                         format={"color":"Blue",\
                                                     "linewidth":2.0}) 
        graph.add_series(series)

        # Add ourselves to the scanalysis notebook
        self.sa.add_notebook_page(self.get_display_name(), page)

    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page)

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Wind Speed Graph", Wind_Speed_Graph)
