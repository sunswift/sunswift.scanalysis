import gobject
import gtk
import time
import Driver

class Listener:
    def __init__(self, store, nodename, channame):
        store.register_for_channel(nodename, channame, self.deliver)
        self.store = store
        self.value = 0.0

    def __del__(self):
        self.stop()

    def stop(self):
        self.store.unregister_for_all_deliveries(self.deliver)

    def deliver(self, pkt):
        self.value = pkt.get_value()
        
    def get_value(self):
        return self.value

class NewListener(Listener):
    def __init__(self, deliverer, nodename, channame):
        Listener.__init__(self, deliverer, nodename, channame)
        self.last_packet = None

    def deliver(self, pkt):
        if self.last_packet is not None:
            if self.last_packet.get_time() >= pkt.get_time():
                return

        Listener.deliver(self, pkt)
        self.last_packet = pkt

class ManualEntry(gtk.Frame):
    def __init__(self, sa, name):
        gtk.Frame.__init__(self, label=name)

        self.sa = sa
        self.myname = name

        hbox = gtk.HBox()

        self.entry = gtk.Entry()
        hbox.pack_start(self.entry)

        button = gtk.Button(label="Send")
        hbox.pack_start(button, expand=False)

        button.connect("clicked", self.button_click)
        self.entry.connect("activate", self.button_click)

        self.add(hbox)

        self.source = Driver.Source(self.sa.store, name)
        self.channel = Driver.Channel(self.source, "name")


    def button_click(self, widg):
        newvalue = self.entry.get_text()
        self.channel.deliver(Driver.Deliverable(newvalue))
        self.entry.set_text("")

class Calibrateable: 
    m=1.0
    b=0.0
    def get_mb(self):
        return (self.m, self.b)
    def set_mb(self, (m,b)):
        self.m = m
        self.b = b