import Driver 
import thread
import sys
import Configurator
import struct
import serial
import time
import TDKLambda

import Scandal
import ScandalWidgets

import Graphing
import GraphingMPL

import pygtk
pygtk.require('2.0')
import gtk
import gobject


class TDKLambdaDriver(Driver.Driver):
    def __init__(self, sa, config, name="TDK"):
        Driver.Driver.__init__(self, sa, config, name=name)

        if "port" not in config:
        	config["port"] = "/dev/ttyS0"

        self.pkt_queue_lock = thread.allocate_lock()
        self.pkt_queue = []

        self.source = Driver.Source(sa.store, self.get_name())
        self.chans = {"TDKVoltage":{}, "TDKCurrent":{}}

        gobject.timeout_add(200, self.poll)

        self.worker_thread = thread.start_new_thread(self.worker, () )

        self.page = page = gtk.HBox()
        col1 = gtk.VBox()
        page.pack_start(col1)

	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Voltage (V)",\
                                  maxupdate=500)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, "TDKLambda", "TDKVoltage", \
                                               label="TDK Voltage", \
                                              maxtimediff=1800.0) 
        graph.add_series(series)

        self.sa.add_notebook_page(self.get_display_name(), self.page)

        self.sa.nodelist.register_menu_cb(self.add_menu_items)

    def add_menu_items(self, data):
        entry1, entry2 = data.get_selection().get_selected()
        channel = entry1.get_value(entry2, 0)
        value = entry1.get_value(entry2, 1)
      
        buttons = []
        
	if channel == "TDKVoltage":
        	buttons.append(["Change Voltage", self.change_voltage_popup])
       
        return buttons

    def change_voltage_popup(self,item,event,data):
	
	entry1, entry2 = data.get_selection().get_selected()
        channel = entry1.get_value(entry2, 0)
	if channel != "TDKVoltage":
		self.sa.console.write("tried to change voltage on something bad!")
		return
	
        parent = data.get_model().iter_parent(entry2)
        nodename = entry1.get_value(parent, 0)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title("Change Voltage")
        self.window.set_resizable(False)

        table = gtk.Table()
        table.set_col_spacings(3)

        voltage_label = gtk.Label("Voltage")
        table.attach(voltage_label, 0, 1, 0, 1, gtk.FILL, gtk.FILL, 20, 20)
        self.voltage_field = gtk.Entry()
        table.attach(self.voltage_field, 1, 2, 0, 1, gtk.FILL, gtk.FILL, 20, 5)

        vbox = gtk.VBox()
	
        valign = gtk.Alignment(0, 1, 0, 0)
        valign.add(table)
        vbox.add(valign)

        self.window.add(vbox)

        buttons_hbox = gtk.HBox()
	but_save = gtk.Button(label="set voltage")
        but_save.connect("clicked", self.set_voltage, nodename, channel)
        buttons_hbox.add(but_save)
	but_cancel = gtk.Button(label="Cancel")
        but_cancel.connect("clicked", self.cancel)
        buttons_hbox.add(but_cancel)
	
        halign = gtk.Alignment(1, 1, 0, 0)
        halign.set_padding(20,20,20,20)
        halign.add(buttons_hbox) 
	
        vbox.pack_start(halign)
 
        self.window.show_all()

    def set_voltage(self, item, nodename, channel):
	try:
		voltage=self.voltage_field.get_text()
		if len(voltage)>12:
			self.voltage_field.set_text("you're stupid and it is too long! less than 12 char")
		else:
			voltage = float(voltage)
			if voltage < 0:	
				self.voltage_field.set_text("you're stupid, it should be a positive num")
			elif voltage > 300.00:
				self.voltage_field.set_text("you're stupid, it is too big")
			else:
				self.sa.console.write("got voltage %s" % voltage)
				self.tdk.set_voltage(voltage)
        			self.window.destroy()
	except ValueError:
		self.voltage_field.set_text("you're stupid")

	
	return

    def cancel(self, widget):
        self.window.destroy()
        return

    def destroy(self, widget, data=None):
        return

    def worker(self):
	self.sa.console.write("tdk starting...")

        while self.running:
            try:
                self.tdk = TDKLambda.TDK(self.config["port"], self.sa)
		self.sa.console.write("tdk successfully opened serial port")
                break
            except Exception, e:
		print "exception message: %s" % e.message
	        self.sa.console.write("Could not open serial port -- %s, retrying" % self.config["port"],\
                                          mod=self)
                time.sleep(1)

	self.sa.console.write("tdk running...")

        while self.running:

   	    time.sleep(0.2)

	    # get the voltage
	    volts = self.tdk.get_voltage()

	    amps = self.tdk.get_current()

            #self.sa.console.write("%d",  volt)
            self.pkt_queue_lock.acquire()

	    self.pkt_queue.append( ("TDKVoltage", 0, \
                                            Driver.Deliverable(volts)) )
	    self.pkt_queue.append( ("TDKCurrent", 1, \
                                            Driver.Deliverable(amps)) )

	    self.pkt_queue_lock.release()

    
    def poll(self):
        self.pkt_queue_lock.acquire()
        for (chan, addr, pkt) in self.pkt_queue:
            if addr not in self.chans[chan]:
                self.chans[chan][addr] = \
                    Driver.Channel(self.source, "%s" % chan)

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
	self.sa.console.write("tdk stopped")
        self.running = False
        

# Register our driver with the driver module's module factory
Driver.modfac.add_type("TDKLamdba", TDKLambdaDriver)
