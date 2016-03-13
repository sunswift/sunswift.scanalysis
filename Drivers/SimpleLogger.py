import Driver
import gobject
import gtk
import Configurator

class LogMe:
    def __init__(self, file, chan_id):
        self.file = file
        self.id = chan_id

    def deliver(self, pkt):
        self.file.write(str(self.id) + "\t" + \
                            str(pkt.get_value()) + "\t" + \
                            str(pkt.get_time()) + "\n")

class SimpleLogger(Driver.Driver):
    def __init__(self, sa, config, name="SimpleLogger"):
        Driver.Driver.__init__(self, sa, config, name)
        
        if "filename" not in config:
            config["filename"] = "default.log"

        filename = config["filename"]
        self.file = open(filename, "a+")

        for source in self.sa.store:
            for channel in self.sa.store[source]:
                self.update_func(self.sa.store[source][channel])
        self.sa.store.register_for_updates(self.update_func)

    def update_func(self, item):
        if isinstance(item, Driver.Channel):
            id = item.get_source().get_name() + "\t" + item.get_name()
            logger = LogMe(self.file, id)
            item.register_for_delivery(logger.deliver)

        if isinstance(item, Driver.Source):
            item.register_for_updates(self.update_func)

    def flush_file(self):
        self.file.flush()

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("filename", self.config, "Log File Name")
        w.pack_start(e, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("SimpleLogger", SimpleLogger)

