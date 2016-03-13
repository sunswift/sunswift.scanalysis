import gobject
import time
import gc

import Driver

class Messages(Driver.Module):
    def __init__(self, sa, config, name="Messages"):
        Driver.Module.__init__(self, sa, config, name)

        self.last_timeout_time = time.time()
        self.last_timeout_count = 0

        source = Driver.Source(self.sa.store, name)
        self.rate = Driver.Channel(source, "Packet Rate")
        self.objects = Driver.Channel(source, "PyObjects")
        self.packets = Driver.Channel(source, "Packets")

        gobject.timeout_add(1000, self.timeout_cb)        

        self.start = time.time()

    def deliver_packet(self, pkt):
	if pkt.type == ScandalPacket.USER_ERROR_TYPE:
		errstring = self.cfg.error_string(pkt.addr, pkt.device_type, pkt.error)
		self.sa.console.write("Node %d gave error %s" % (pkt.addr, errstring))

    def timeout_cb(self):
        timediff = time.time() - self.last_timeout_time; 
        self.last_timeout_time = time.time()
        countdiff = self.sa.store.get_count() - self.last_timeout_count
        self.last_timeout_count = self.sa.store.get_count()
        
        print "Time since start: " + str(time.time() - self.start)

        self.rate.deliver( Driver.Deliverable( countdiff / timediff ) )
        self.objects.deliver( Driver.Deliverable( len(gc.get_objects()) ) )
        self.packets.deliver( Driver.Deliverable( self.sa.store.get_count() ) ) 
        return True

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Messages", Messages)
