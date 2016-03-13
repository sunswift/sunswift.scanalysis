import Driver
import gobject
import time
import math
import gtk
import Configurator

class SineWave(Driver.Driver):
    def __init__(self, sa, config, \
                     name="SineWave"):
        Driver.Driver.__init__(self, sa, config, name)
        
        # Default configuration
        # Check to see if we don't have sourcename, 
        # which we should. 
        if "resolution" not in config:
            config["resolution"] = 0.1
            config["period"] = 5.0
            config["amplitude"] = 1.0
            config["phase"] = math.pi * 2.0 / 3.0

        self.source = Driver.Source(sa.store, self.get_name())
        self.chan = Driver.Channel(self.source, "sine")

        gobject.timeout_add(int(config["resolution"] * 1000.0), self.update)

        self.sa.console.write("Started", mod=self)
        
    def update(self):
        value = self.config["amplitude"] * \
            math.sin((2.0 * math.pi * time.time()\
                          / self.config["period"]) + \
                         self.config["phase"])
        self.chan.deliver(Driver.Deliverable(value))
        return self.running

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.FloatConfig("amplitude", self.config, "Amplitude")
        w.pack_start(e, expand=False)

        e = Configurator.FloatConfig("phase", self.config, "Phase")
        w.pack_start(e, expand=False)

        e = Configurator.FloatConfig("period", self.config, "Period")
        w.pack_start(e, expand=False)

        e = Configurator.FloatConfig("resolution", self.config, "Resolution")
        w.pack_start(e, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("SineWave", SineWave)

