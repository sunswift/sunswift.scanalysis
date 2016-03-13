import gobject
import gtk

import Driver 
import thread
import sys
import Configurator
import struct
import serial
import time
import BMS

class BMSDriver(Driver.Driver):
    def __init__(self, sa, config, name="BMS"):
        Driver.Driver.__init__(self, sa, config, name=name)

        if "port" not in config:
            config["port"] = "/dev/ttyUSB0"

        self.pkt_queue_lock = thread.allocate_lock()
        self.pkt_queue = []

        self.source = Driver.Source(sa.store, self.get_name())
        self.chans = {"Voltage":{}, "Temp":{}}

        gobject.timeout_add(100, self.poll)

        self.worker_thread = thread.start_new_thread(self.worker, () )
        
    def worker(self):
        while self.running:
            try:
                self.bms = BMS.BMS(self.config["port"])
                break
            except:
                self.sa.console.write("Could not open serial port -- %s, retrying" % self.config["port"],\
                                          mod=self)
                time.sleep(1)

        self.valid_addrs = self.bms.scan_bus()

        print "Valid addresses were: " + str(self.valid_addrs)

        if len(self.valid_addrs) == 0:
            return

        while self.running:
            for addr in self.valid_addrs:
                volt = self.bms.get_voltage(addr)
                self.pkt_queue_lock.acquire()
                self.pkt_queue.append( ("Voltage", addr, \
                                            Driver.Deliverable(volt)) )
                self.pkt_queue_lock.release()

                temp = self.bms.get_temperature(addr)
                self.pkt_queue_lock.acquire(addr)
                self.pkt_queue.append( ("Temp", addr, \
                                            Driver.Deliverable(temp)) )
                self.pkt_queue_lock.release()

                
    def poll(self):
        self.pkt_queue_lock.acquire()
        for (chan, addr, pkt) in self.pkt_queue:
            if addr not in self.chans[chan]:
                self.chans[chan][addr] = \
                    Driver.Channel(self.source, "%d %s" % (addr, chan))

            self.chans[chan][addr].deliver(pkt)
        self.pkt_queue_lock.release()
        return 1

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

    def stop(self):
        self.running = False
        

# Register our driver with the driver module's module factory
Driver.modfac.add_type("BMS", BMSDriver)
