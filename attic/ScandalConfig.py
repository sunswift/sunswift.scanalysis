from ScandalWidgets import *
from TimeGraph import *
from XYGraph import *
from Can import *

class AddressChanger(gtk.HBox):
    def change(self, button):
        # Send the message 
        msg = ScandalAddrChangePacket(0, 26)
        self.solarcar.send(msg)
    
    def __init__(self, solarcar):
        gtk.HBox.__init__(self)

        self.solarcar = solarcar

        change = gtk.Button(label="Change")
        self.pack_start(change, expand=False)

        change.connect("clicked", self.change); 

class ScandalConfig(gtk.HBox):
    def __init__(self, sa, nodename="MPPTNG"):
        gtk.HBox.__init__(self)

        col1 = gtk.VBox()
        self.pack_start(col1)
        col2 = gtk.VBox()
        self.pack_start(col2)

        

        addrChanger = AddrChangerWidget(sa)
        col1.pack_start(addrChanger)
