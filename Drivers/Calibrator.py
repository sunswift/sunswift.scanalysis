from ScandalWidgets import *
import Driver
import gobject
import time
import math
import gtk
import Configurator
import Misc
import ScandalWidgets
import Graphing
import GraphingMPL

from rpy2 import *
import rpy2

class CalibrateWindow(gtk.Window):
    def __init__(self, sa, channel):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.connect("destroy", self.destroy)
        self.set_default_size(750,550)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title("Calibrate \"" + channel.get_source().get_name() + ":" + channel.get_name() + "\"")

        self.sa = sa
        self.channel = channel
        self.target_callback_ref = None

        box = gtk.VBox()
        self.add(box)
        
        # Set up the "Potential capture" frame
        frame = gtk.Frame(label="Potential Capture")
        box.pack_start(frame, expand=False)

        potential=gtk.VBox()
        frame.add(potential)
        
        self.listen = ScandalWidgets.LabelIndicator(self.sa.store, channel.get_source().get_name(), channel.get_name(), label="Source")
        potential.pack_start(self.listen, expand=False)

        hbox = gtk.HBox()
        potential.pack_start(hbox)
        label = gtk.Label(str="Target")
        hbox.pack_start(label, expand=False)
        self.entry = gtk.Entry()
        hbox.pack_start(self.entry)
        self.entry.connect("activate", self.take_sample)
        button = gtk.Button(label="Take Sample")
        button.connect("clicked", self.take_sample)
        hbox.pack_start(button, expand=False)
        
        treestore = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.target_list = gtk.ComboBox(treestore)
        cell = gtk.CellRendererText()
        self.target_list.pack_start(cell, True)
        self.target_list.add_attribute(cell, 'text', 0)
     
        # Append a row
        iter = treestore.append(None)
        treestore.set(iter, 0, "None", 1, None)

        # Append the menus for the rest of the nodelist
        for target_source in self.sa.store:
            source_iter = treestore.append(None)
            treestore.set(source_iter, 0, target_source, 1, None)
            for target_channel in self.sa.store[target_source]:
                channel_iter = treestore.append(source_iter)
                treestore.set(channel_iter, 0, target_channel, 1, self.sa.store[target_source][target_channel])
        
        potential.pack_start(self.target_list)
        self.target_list.connect("changed", self.target_list_edited_cb)
        self.target_list.set_active(0)
        self.target_callback_ref = None

        frame = gtk.Frame(label="Old settings")
        box.pack_start(frame, expand=False)

        oldbox = gtk.HBox()
        frame.add(oldbox)

        self.oldmentry = gtk.Entry(max=8)
        self.oldmentry.set_editable(True)
        self.oldmentry.set_width_chars(6)
        label = gtk.Label(str="Old M")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        oldbox.pack_start(label)
        oldbox.pack_start(self.oldmentry)

        self.oldbentry = gtk.Entry(max=8)
        self.oldbentry.set_editable(True)
        self.oldbentry.set_width_chars(6)
        label = gtk.Label(str="Old B")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        oldbox.pack_start(label)
        oldbox.pack_start(self.oldbentry)

        (m,b) = self.channel.get_mb()
        self.oldmentry.set_text(str(m))
        self.oldbentry.set_text(str(b))

        button = gtk.Button(label="Update With Old")
        oldbox.pack_start(button)
        button.connect("clicked", self.update_with_old_cb)
        
        # Set up the "captured data" frame
        frame = gtk.Frame(label="Captured Data")
        box.pack_start(frame)
    
        # Set up the graph
        captured = gtk.VBox()
        frame.add(captured)
        self.plot = GraphingMPL.Graph(self.sa, \
                                       xlabel=channel.get_name(), \
                                       ylabel="Target", 
                                        maxupdate=200)
        self.captured_series = Graphing.SeriesStatic(self.sa, [], [], label="Captured", format={"marker":"+", "linestyle":" ","color":"red", "linewidth":2.0})
        self.predicted_series = Graphing.SeriesStatic(self.sa, [], [], label="Predicted", format={"color":"black", "linewidth":2.0})

        self.plot.add_series(self.captured_series)
        self.plot.add_series(self.predicted_series)
        captured.pack_start(self.plot.get_widget())

        statsbox = gtk.HBox()
        captured.pack_start(statsbox, expand=False)

        self.r2entry = gtk.Entry(max=8)
        self.r2entry.set_editable(False)
        self.r2entry.set_width_chars(6)
        label = gtk.Label(str="R^2")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        statsbox.pack_start(label)
        statsbox.pack_start(self.r2entry)

        self.newmentry = gtk.Entry(max=8)
        self.newmentry.set_editable(False)
        self.newmentry.set_width_chars(6)
        label = gtk.Label(str="New M")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        statsbox.pack_start(label)
        statsbox.pack_start(self.newmentry)

        self.newbentry = gtk.Entry(max=8)
        self.newbentry.set_editable(False)
        self.newbentry.set_width_chars(6)
        label = gtk.Label(str="New B")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        statsbox.pack_start(label)
        statsbox.pack_start(self.newbentry)

        frame = gtk.Frame(label="Predicted")
        box.pack_start(frame, expand=False)

        predicted = gtk.HBox()
        frame.add(predicted)

        self.predictedentry = gtk.Entry(max=8)
        self.predictedentry.set_editable(False)
        self.predictedentry.set_width_chars(6)
        label = gtk.Label(str="Predicted with New M/B")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(1.0, 0.5)
        label.set_padding(1, 1)
        predicted.pack_start(label)
        predicted.pack_start(self.predictedentry)
        
        self.channel.register_for_delivery(self.update_predicted_value_cb)
        
        hbox = gtk.HBox()
        box.pack_start(hbox, expand=False)        
        button = gtk.Button(label="Send Calibration")
        button.connect("clicked", self.send_calibration)
        hbox.pack_start(button, expand=False)

        # Initialised M and B to the expected constants
        self.newm = 1.0
        self.newb = 0.0
        self.channel.set_mb( (self.newm, self.newb) )
        
        # Initialise data values
        self.xvals = []
        self.yvals = []

        self.show()
        self.show_all()

    def destroy(self,widget,data=None):
        # Do any finalising when the window is destroyed
        self.sa.store.unregister_for_all_deliveries(self.update_target_value_cb)
        self.sa.store.unregister_for_all_deliveries(self.update_predicted_value_cb)
        self.listen.stop()
        
    def send_calibration(self, widget, data=None):
        self.channel.set_mb( (self.newm, self.newb) )

    def target_get_value(self):
        return float(self.entry.get_text())
        
    def update_target_value_cb(self, pkt):
        self.entry.set_text(str(pkt))

    def update_predicted_value_cb(self, pkt):
        newvalue = pkt.get_value() * self.newm + self.newb
        self.predictedentry.set_text(str(newvalue))

    def update_with_old_cb(self, widget, data=None):
        oldm = float(self.oldmentry.get_text())
        oldb = float(self.oldbentry.get_text())
        self.channel.set_mb( (oldm, oldb) )

    def target_list_edited_cb(self, widget, data=None):
        treemodel = self.target_list.get_model()
        active_iter = self.target_list.get_active_iter()
        (channel,) = treemodel.get(active_iter, 1)
        
        if self.target_callback_ref is not None:
            self.sa.store.unregister_for_all_deliveries(self.target_callback_ref)
                    
        if channel is not None:
            channel.register_for_delivery(self.update_target_value_cb)
            self.target_callback_ref = self.update_target_value_cb
        else:
            self.target_callback_ref = None
            
    def take_sample(self, widget, data=None):    
        self.xvals.append(self.listen.get_value())
        self.yvals.append(self.target_get_value())

        if len(self.xvals) > 1:
            # Should update the regression, newm, newb, etc here
            data={}
            data["x"] = self.xvals
            data["y"] = self.yvals

            df = rpy.r.as_data_frame(data)
            model = rpy.r("y~x")
            rpy.set_default_mode(rpy.NO_CONVERSION)
            fit = rpy.r.lm(model, data=df)
            rpy.set_default_mode(rpy.BASIC_CONVERSION)
            
            results = fit.as_py()
            summary = rpy.r.summary(fit)
            
            self.newm = results["coefficients"]["x"]
            self.newb = results["coefficients"]["(Intercept)"]
            r2 = summary["r.squared"]

            self.newmentry.set_text("%.3f" % self.newm)
            self.newbentry.set_text("%.3f" % self.newb)
            self.r2entry.set_text("%f" % r2)

        self.captured_series.set_xpoints(self.xvals)
        self.captured_series.set_ypoints(self.yvals)
        
        predicted_vals = []
        for val in self.xvals:
            predicted_vals.append(self.newm * val + self.newb)
        
        self.predicted_series.set_xpoints(self.xvals)
        self.predicted_series.set_ypoints(predicted_vals)
        self.plot.flag_update()

class Calibrator(Driver.Driver):
    def __init__(self, sa, config, name="Calibrator"):
        Driver.Driver.__init__(self, sa, config, name)
        self.cfg = config

        self.sa.nodelist.register_menu_cb(self.add_menu_items)

    def add_menu_items(self, data):
        entry1, entry2 = data.get_selection().get_selected()
        channel = entry1.get_value(entry2, 3)
              
        buttons = []
        if isinstance(channel, Misc.Calibrateable):
            buttons.append(["Calibrate", lambda x,y,z: self.calibrate(channel)])
       
        return buttons
      
    def calibrate(self, channel):
        window = CalibrateWindow(self.sa, channel)
        
# Register our driver with the driver module's module factory
Driver.modfac.add_type("Calibrator", Calibrator)
