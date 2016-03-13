from ScandalWidgets import *

import Driver
import Configurator

import twitter
import time
import thread

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class Twitter(Driver.Driver):
    def __init__(self, sa, config, name="Twitter"):      
        Driver.Driver.__init__(self, sa, config, name)
        self.page = page = gtk.VBox()

        if "status_string" not in config:
            config["status_string"] = "Oops. Someone forgot to configure the twitter module in Scanalysis! Give them a hard time about it... ;-)"

        if "username" not in config:
            config["username"] = "sunswiftdata"
            
        if "password" not in config:
            config["password"] = "scanalysis!"
            
        if "period" not in config:
            config["period"] = 60.0

        # Parse the twitter string here
#        self.sa.store.register_for_channel(nodename, "Input Voltage", lambda pkt: self.deliver_value("InV", pkt))
#        self.sa.store.register_for_channel(nodename, "Input Current", lambda pkt: self.deliver_value("InI", pkt))
#        self.sa.store.register_for_channel(nodename, "Output Voltage", lambda pkt: self.deliver_value("OutV", pkt))
#        self.sa.store.register_for_channel(nodename, "Output Current", lambda pkt: self.deliver_value("OutI", pkt))

        # Thread to do twitter updates for us so that the UI doesn't freeze while it does        
        self.ws_tread = thread.start_new_thread(self.worker_thread, () )


    def deliver_value(self, value_name, pkt):
        return

    def worker_thread(self):
        while self.running:
            self.update_status()
            time.sleep(self.config["period"])
        return

    def update_status(self):
        update_string = self.generate_status(self.config["status_string"])
        if update_string is None:
            self.sa.console.write("Error occurred when updating the twitter status", mod=self)
        else:
            try:
                api = twitter.Api(username=self.config["username"], password=self.config["password"])
                status = api.PostUpdate(update_string)
                del api
                self.sa.console.write("Updated twitter feed with: \"" + update_string + "\"", mod=self)
            except:
                self.sa.console.write("Could not update twitter feed", mod=self)
            
        return self.running

    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page)

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("status_string", self.config, "Status String")
        w.pack_start(e, expand=False)

        e = Configurator.TextConfig("username", self.config, "User Name")
        w.pack_start(e, expand=False)

        e = Configurator.TextConfig("password", self.config, "Password")
        w.pack_start(e, expand=False)

        e = Configurator.FloatConfig("period", self.config, "Period")
        w.pack_start(e, expand=False)
        
        return widg

### Below here is lifted straight from the LiveView code. We should really try and share this between the two, but
### I'm sick at the moment and so I don't care. 

    def generate_status(self, input_status):
        new_status = ""
                
        while True:
            i = input_status.find("<<<<")
            if i == -1:
                break; 

            # Write up to the tag 
            new_status = new_status + input_status[0:i]
                        
            # Get rid of the stuff we just wrote
            # and the < characters
            input_status = input_status[i+1:]
            input_status = input_status.lstrip("<")

            # Find the end of the token and split it off
            i = input_status.find(">>>>")
            if i == -1:
                self.sa.console.write("Invalid input_status -- no end >>>>", mod=self)
                return None

            mytok = input_status[0:i]
            input_status = input_status[i+4:] # Get rid of the <<<<

            parms = mytok.split("/")

            # Get rid of any leading or trailing whitespace
            for i in range(len(parms)):
                parms[i] = parms[i].lstrip().rstrip()

            new_status = new_status + self.do_parse_tag(parms)
            
        return new_status + input_status

    def do_parse_tag(self, parms):
        if len(parms) < 1:
            self.sa.console.write("Error parsing status -- blank tag!", mod=self)
            return ""
        
        if parms[0] == "CHANNEL":
            if len(parms) != 3:
                self.sa.console.write("Error parsing status -- not enough params to CHANNEL tag -- usual form is <<<<CHANNEL/NodeName/ChannelName>>>>", mod=self)

#FIXME: Should have some kind of synchronisation here, since this is happening in a different thread. 
            node = parms[1]
            chan = parms[2]
            if node not in self.sa.store:
                self.sa.console.write("Could not find source \"%s\"" % node, mod=self)
                return "N/A"      
            elif chan not in self.sa.store[node]:
                self.sa.console.write("Could not find channel \"%s\" in source \"%s\"" % (chan, node), mod=self)
                return "N/A"
            else:
                channel = self.sa.store[node][chan]

            val = channel.get_last_delivered().get_value()
            
            return str(val)

        elif parms[0] == "TIME":
            return time.strftime("%I:%M%p %dth %B, %Y")
                
        else:
            self.sa.console.write("Didn't recognise this tag: %s" %(parms[0]), mod=self)
            return ""



# Register our driver with the driver module's module factory
Driver.modfac.add_type("Twitter", Twitter)
