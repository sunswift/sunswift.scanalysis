import gobject
import gtk
import Driver
import Configurator
import Logging

from sqlite3 import dbapi2 as sqlite

class LogDB(Driver.Driver, Logging.Logger):
    def __init__(self, sa, config, name="LogDB"):
        Logging.Logger.__init__(self)
        Driver.Driver.__init__(self, sa, config, name)
        if "logfile" not in config:
            config["logfile"] = "logdb_default.db"

        self.con = sqlite.connect(config["logfile"])

        self.cur = self.con.cursor()
        
        try:
            self.cur.executescript("""
                create table channels(
                    id, 
                    nodename, 
                    channelname
                );

                create table data(
                    chanid, 
                    value, 
                    timestamp
                );
            """)
        except:
            print self.sa.console.write("An exception occurred trying to create the database tables. This may be totally normal.", mod=self)

        self.sa.register_logger(self)


    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("logname", self.config, "Log Database File Name")
        w.pack_start(e, expand=False)

        return widg


# Register our driver with the driver module's module factory
Driver.modfac.add_type("LogDB", LogDB)

