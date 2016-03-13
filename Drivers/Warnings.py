from ScandalWidgets import *
import Driver
import gobject
import time
import math
import gtk
import Configurator

class Warning(NewListener):

    DIALOG = "Dialog"

    def __init__(self, sa, nodename, channame, descriptor, min, max, warn_type, message):
        NewListener.__init__(self, sa.store, nodename, channame)
        self.sa = sa
        self.channame = channame
        self.descriptor = descriptor
        self.min_value = min
        self.max_value = max
        self.warn_type = warn_type
        self.message = message
        self.sa.console.write("Warnings: Warning '%s' added..." % descriptor)
        self.dialog = None
        self.dismissed_permanently = False

    def clear_dismissed_flag(self, item, event, data):
        self.dismissed_permanently = False
        return

    def dismiss_forever(self, event, data):
        if data:
            self.dismissed_permanently = True
        self.sa.console.write("Warning: %s dismissed" % self.descriptor)
        self.dialog.destroy()
        self.dialog = None

    def dismiss(self, item, event, data=None):
        self.sa.console.write("Warning: %s dismissed" % self.descriptor)
        self.dialog.destroy()
        self.dialog = None
        return

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)

        message = ""
        warn = False

        if self.last_packet.get_value() < self.min_value:
            warn = True
            message = "Value %lf is less than defined level (%lf)" % (float(self.last_packet.get_value()), float(self.min_value))
        if self.last_packet.get_value() > self.max_value:
            warn = True
            message = "Value %lf is greater than defined level (%lf)" % (float(self.last_packet.get_value()), float(self.max_value))

        if warn:
            self.sa.console.write("Warning: %s" % self.message)
            if self.warn_type == Warning.DIALOG and self.dialog is None and not self.dismissed_permanently:
                button_dismiss = gtk.Button("Dismiss")
                button_dismiss.connect("clicked", self.dismiss, False)
                button_dismiss_forever = gtk.Button("Dismiss forever")
                button_dismiss_forever.connect("clicked", self.dismiss_forever, True)
                self.dialog = gtk.Dialog("Warning!", self.sa.window, gtk.DIALOG_MODAL, None)
                self.dialog.connect("delete_event", self.dismiss)
                self.dialog.action_area.pack_start(button_dismiss, True, True, 0)
                button_dismiss.show()
                self.dialog.action_area.pack_start(button_dismiss_forever, True, True, 0)
                button_dismiss_forever.show()
                label = gtk.Label(self.message)
                self.dialog.vbox.pack_start(label, True, True, 0)
                label.show()
                label = gtk.Label(message)
                self.dialog.vbox.pack_start(label, True, True, 0)
                label.show()
                self.dialog.set_default_size(450, 120)
                self.dialog.show()

        return

class Warnings(Driver.Driver):
    def __init__(self, sa, config, name="Warnings"):
        Driver.Driver.__init__(self, sa, config, name)
        self.cfg = config
        self.warnings = []
        if "nodes" in self.cfg.keys():
             for node in self.cfg["nodes"]:
                 for channel in self.cfg["nodes"][node]:
                     self.warnings.append(Warning(self.sa, node, channel, self.cfg["nodes"][node][channel]["descriptor"], self.cfg["nodes"][node][channel]["min"], self.cfg["nodes"][node][channel]["max"], self.cfg["nodes"][node][channel]["type"], self.cfg["nodes"][node][channel]["message"]))
        else:
             self.cfg["nodes"] = {}
        self.sa.nodelist.register_menu_cb(self.add_menu_items)

    def add_menu_items(self, data):
        entry1, entry2 = data.get_selection().get_selected()
        channel = entry1.get_value(entry2, 0)
        value = entry1.get_value(entry2, 1)
      
        buttons = []
        has_warning = False
 
        for warning in self.warnings:
            if warning.channame == channel:
                buttons.append(["Remove Warning", self.remove_warning])
                has_warning = True
            if warning.channame == channel and warning.dismissed_permanently:
                buttons.append(["Clear dismissed flag", warning.clear_dismissed_flag])
        
        if value is not "" and not has_warning:
             buttons.append(["Add Warning", self.add_warning])
       
        return buttons
      
    def remove_warning(self, item, event, data):
        entry1, entry2 = data.get_selection().get_selected()
        channel = entry1.get_value(entry2, 0)
        parent = data.get_model().iter_parent(entry2)
        nodename = entry1.get_value(parent, 0)
        
        n = 0
        for i in self.warnings:
            if i.channame == channel:
                self.warnings[n].stop()
                del self.warnings[n]
                del self.cfg["nodes"][nodename][channel]
            n = n + 1
        self.sa.console.write("Warnings: removed warning '%s'" % channel)   

    def add_warning(self, item, event, data):
        entry1, entry2 = data.get_selection().get_selected()
        channel = entry1.get_value(entry2, 0)
        parent = data.get_model().iter_parent(entry2)
        nodename = entry1.get_value(parent, 0)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title("Add Warning")
        self.window.set_resizable(False)

        table = gtk.Table()
        table.set_col_spacings(3)

        descriptor_label = gtk.Label("Descriptor")
        table.attach(descriptor_label, 0, 1, 0, 1, gtk.FILL, gtk.FILL, 20, 20)
        self.descriptor_field = gtk.Entry()
        table.attach(self.descriptor_field, 1, 2, 0, 1, gtk.FILL, gtk.FILL, 20, 5)

        min_value_label = gtk.Label("Minimum Value")
        table.attach(min_value_label, 0, 1, 1, 2, gtk.FILL, gtk.FILL, 20, 5)
        self.min_value_field = gtk.Entry()
        table.attach(self.min_value_field, 1, 2, 1, 2, gtk.FILL, gtk.FILL, 20, 5)

        max_value_label = gtk.Label("Maximum Value")
        table.attach(max_value_label, 0, 1, 2, 3, gtk.FILL, gtk.FILL, 20, 5)
        self.max_value_field = gtk.Entry()
        table.attach(self.max_value_field, 1, 2, 2, 3, gtk.FILL, gtk.FILL, 20, 5)

        warn_type_label = gtk.Label("Warning Type")
        table.attach(warn_type_label, 0, 1, 3, 4, gtk.FILL, gtk.FILL, 20, 5)
        self.warn_type_field = gtk.Combo()
        self.warn_type_field.set_popdown_strings(["Dialog", "Status Bar Warning", "Dialog with Sound", "Sound"])
        table.attach(self.warn_type_field, 1, 2, 3, 4, gtk.FILL, gtk.FILL, 20, 5)

        message_label = gtk.Label("Message")
        table.attach(message_label, 0, 1, 4, 5, gtk.FILL, gtk.FILL, 20, 5)
        self.message_field = gtk.Entry()
        table.attach(self.message_field, 1, 2, 4, 5, gtk.FILL, gtk.FILL, 20, 5)

        vbox = gtk.VBox()
	
        valign = gtk.Alignment(0, 1, 0, 0)
        valign.add(table)
        vbox.add(valign)

        self.window.add(vbox)

        buttons_hbox = gtk.HBox()
	but_save = gtk.Button(label="Save & Close")
        but_save.connect("clicked", self.save_warning, nodename, channel)
        buttons_hbox.add(but_save)
	but_cancel = gtk.Button(label="Cancel")
        but_cancel.connect("clicked", self.cancel)
        buttons_hbox.add(but_cancel)
	
        halign = gtk.Alignment(1, 1, 0, 0)
        halign.set_padding(20,20,20,20)
        halign.add(buttons_hbox) 
	
        vbox.pack_start(halign)
 
        self.window.show_all()

    def destroy(self, widget, data=None):
        return

    def cancel(self, widget):
        self.window.destroy()
        return

    def save_warning(self, item, nodename, channel):
        new_warning = {}
        new_warning[nodename] = {}
        new_warning[nodename][channel] = {}
        new_warning[nodename][channel]["descriptor"] = self.descriptor_field.get_text()
        new_warning[nodename][channel]["message"] = self.message_field.get_text()
        new_warning[nodename][channel]["min"] = self.min_value_field.get_text()
        new_warning[nodename][channel]["max"] = self.max_value_field.get_text()
        new_warning[nodename][channel]["type"] = self.warn_type_field.entry.get_text()
        self.warnings.append(Warning(self.sa, nodename, channel, new_warning[nodename][channel]["descriptor"], new_warning[nodename][channel]["min"], new_warning[nodename][channel]["max"], new_warning[nodename][channel]["type"], new_warning[nodename][channel]["message"]))
        self.cfg["nodes"].update(new_warning)
        self.window.destroy()
        return
 
# Register our driver with the driver module's module factory
Driver.modfac.add_type("Warnings", Warnings)
