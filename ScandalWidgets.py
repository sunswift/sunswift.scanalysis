# --------------------------------------------------------------------------                                 
#  Scanalysis Scandal Abstraction
#  File name: ScandalWidgets.py
#  Author: David Snowdon
#  Description: Support for Scandal Widgets
#
#  Copyright (C) David Snowdon, 2009. 
#   
#  Date: 01-10-2009
# -------------------------------------------------------------------------- 
#
#  This file is part of Scanalysis.
#  
#  Scanalysis is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Scanalysis is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Scanalysis.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import Scandal
import Drivers.ScandalDriver

from Misc import *

class ChannelWidget (gtk.HBox):
    def __init__(self, sa, nodeaddr, channum, same_bus_node_name, \
                 default="", label=None):
        gtk.HBox.__init__(self)

        self.button = gtk.Button(label="Set")
        self.pack_end(self.button)
        self.button.connect("clicked", self.do_set)

        self.text = gtk.Entry()
        self.text.set_text(default)
        self.text.set_editable(True); 
        if label is not None:
            self.label = gtk.Label(str=label)
            self.label.set_justify(gtk.JUSTIFY_LEFT)
            self.label.set_alignment(0.0, 0.5)
            self.pack_start(self.label)
        self.pack_end(self.text)

        self.sa = sa

        self.nodeaddr = nodeaddr
        self.channum = channum
        self.same_bus_node_name = same_bus_node_name
        
    def do_set(self, button):
        value = int(self.text.get_text())
        print "Sending channel item: %d" % value
        msg = Scandal.ChannelPacket(addr=self.nodeaddr, 
                                    channel=self.channum, 
                                    value=value)
        # Send the message 
        node = self.sa.store[self.same_bus_node_name]

        if not isinstance(node, Drivers.ScandalDriver.ScandalNode):
            self.sa.console.write("\"" + self.same_bus_node_name + \
                                      "\" was not a ScandalNode")
            return

        nodeaddr = node.get_addr()
        if nodeaddr is None:
            self.sa.console.write("Could not find node")

            return None

        print "Trying to find " + self.same_bus_node_name
        busnodeaddr = self.sa.get_scandal_node_addr(self.same_bus_node_name)
        if busnodeaddr is not None:
            print "Found node on the same network: %d" % busnodeaddr
            print "Sending to the bus"
            source = self.sa.store[self.same_bus_node_name]
            source.get_scandal().send(msg)

class ResetWidget (gtk.HBox):
    def __init__(self, sa, nodename, \
                 label="Reset"):
        gtk.HBox.__init__(self)

        self.button = gtk.Button(label=label)
        self.pack_end(self.button)
        self.button.connect("clicked", self.do_set)
        self.sa = sa

        self.nodename = nodename
        
    def do_set(self, button):
        # Send the message 
        node = self.sa.store[self.nodename]

        if not isinstance(node, Drivers.ScandalDriver.ScandalNode):
            self.sa.console.write("\"" + self.same_bus_node_name + \
                                      "\" was not a ScandalNode")
            return

        nodeaddr = node.get_addr()
        if nodeaddr is None:
            self.sa.console.write("Could not find node")
            return None

        print "Sending reset to node %d" % nodeaddr

        msg = Scandal.ResetPacket(addr=nodeaddr)
        node.get_scandal().send(msg)

class VScaleChannel (gtk.VScale):
    def __init__(self, sa, nodeaddr, channum, same_bus_node_name, minval=0.0, maxval=1.0, initvalue=0.0, label=None):
        gtk.VScale.__init__(self)        
        self.connect("value-changed", self.update)
        self.set_range(minval,maxval)
        self.set_value(initvalue)
        self.set_update_policy(gtk.UPDATE_CONTINUOUS)
        
        self.sa = sa

        self.nodeaddr = nodeaddr
        self.channum = channum
        self.nodename = same_bus_node_name
        
    def update(self, widget):
        print widget
        value = int(self.get_value() * 1000)
        print "Sending channel item: %d" % value
        msg = Scandal.ChannelPacket(addr=self.nodeaddr, 
                                    channel=self.channum, 
                                    value=value)

        # Send the message 
        node = self.sa.store[self.nodename]

        if not isinstance(node, Drivers.ScandalDriver.ScandalNode):
            self.sa.console.write("\"" + nodename + \
                                      "\" was not a ScandalNode when trying to configure " \
                                      + self.configname)
            return

        self.nodeaddr = node.get_addr()
        if self.nodeaddr is None:
            self.sa.console.write("Could not find node when trying to configure " \
                                      + self.configname)

            return None

        busnodeaddr = self.sa.get_scandal_node_addr(self.same_bus_node)
        if busnodeaddr is not None:
            source = self.sa.store[self.same_bus_node]
            source.get_scandal().send(msg)

## FIXME: Needs to be converted to the new "store" system
class UserConfigWidget (gtk.HBox):
    def __init__(self, sa, nodename, configname, default="", label=None):
        gtk.HBox.__init__(self)

        self.button = gtk.Button(label="Set")
        self.pack_end(self.button)
        self.button.connect("clicked", self.do_set)

        self.text = gtk.Entry()
        self.text.set_text(default)
#        self.text.set_alignment(1.0, 0.5)
 #       self.text.set_padding(4.0, 1.0)
        self.text.set_editable(True); 
        if label is not None:
            self.label = gtk.Label(str=label)
            self.label.set_justify(gtk.JUSTIFY_LEFT)
            self.label.set_alignment(0.0, 0.5)
            #self.label.set_padding(4.0, 1.0)
            self.pack_start(self.label)
        self.pack_end(self.text)


        self.sa = sa
        self.nodename = nodename
        self.configname = configname

    def do_set(self, button):
        if self.nodename not in self.sa.store:
            self.sa.console.write("Could not find node for config: " + self.nodename)
            return None
        
        node = self.sa.store[self.nodename]

        if not isinstance(node, Drivers.ScandalDriver.ScandalNode):
            self.sa.console.write("\"" + nodename + \
                                      "\" was not a ScandalNode when trying to configure " \
                                      + self.configname)
            return

        self.nodeaddr = node.get_addr()
        if self.nodeaddr is None:
            self.sa.console.write("Could not find node when trying to configure " \
                                      + self.configname)

            return None

        scandal = node.get_scandal()
        self.confignum = scandal.get_type_userconfig_number_from_name(
            node.get_node_type(), 
            self.configname)


        value = int(self.text.get_text())
        print "Setting configuration item to %d" % value
        msg = Scandal.UserConfigPacket(destaddr=self.nodeaddr, confignum=self.confignum, value=value)
        node.get_scandal().send(msg)

## FIXME: Needs to be converted to the new "store" system
class CommandValueWidget (gtk.HBox):
    def __init__(self, sa, nodename, commandname, default="Enter Value", label=None):
        gtk.HBox.__init__(self)

        self.button = gtk.Button(label="Send")
        self.pack_end(self.button)
        self.button.connect("clicked", self.do_set)

        self.text = gtk.Entry()
        self.text.set_text(default)
        self.text.set_editable(True); 
        if label is not None:
            self.label = gtk.Label(str=label)
            self.label.set_justify(gtk.JUSTIFY_LEFT)
            self.label.set_alignment(0.0, 0.5)
            self.pack_start(self.label)
        self.pack_end(self.text)

        self.sa = sa
        self.nodename = nodename
        self.commandname = commandname

    def do_set(self, button):
        if self.nodename not in self.sa.store:
            self.sa.console.write("Could not find node for config: " + self.nodename)
            return None
        
        node = self.sa.store[self.nodename]

        if not isinstance(node, Drivers.ScandalDriver.ScandalNode):
            self.sa.console.write("\"" + nodename + \
                                      "\" was not a ScandalNode when trying to send command " \
                                      + self.commandname)
            return

        self.nodeaddr = node.get_addr()
        if self.nodeaddr is None:
            self.sa.console.write("Could not find node when trying to send command " \
                                      + self.commandname)

            return None

        scandal = node.get_scandal()
        commandnum = scandal.get_type_command_number_from_name(
            node.get_node_type(), 
            self.commandname)

        if commandnum is None:
            self.sa.console.write("Could not find command number for: " + self.commandname)
            return

        value = int(self.text.get_text())
        print "Sending command with value %d" % value
        msg = Scandal.CommandPacket(destaddr=self.nodeaddr, commandnum=commandnum, value=value)
        node.get_scandal().send(msg)

## FIXME: Needs to be converted to the new "store" system
class AddrChangerWidget (gtk.HBox):
    def __init__(self, sa, label=None):
        gtk.HBox.__init__(self)

        self.button = gtk.Button(label="Set")
        self.pack_end(self.button)
        self.button.connect("clicked", self.do_set)

        lab = gtk.Label(str="To:");
        self.pack_end(lab);
        self.toentry = gtk.Entry()
        self.toentry.set_editable(True); 
        self.pack_end(self.toentry); 

        lab = gtk.Label(str="From:");
        self.pack_end(lab);
        self.fromentry = gtk.Entry()
        self.fromentry.set_editable(True); 
        self.pack_end(self.fromentry)

        if label is not None:
            self.label = gtk.Label(str=label)
            self.label.set_justify(gtk.JUSTIFY_LEFT)
            self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)

        self.sa = sa
        
    def do_set(self, button):
        from_value = int(self.fromentry.get_text())
        to_value = int(self.toentry.get_text())
        print "Setting configuration item from %d to %d" % (from_value, to_value)
        msg = ScandalConfigPacket(from_value, ScandalPacket.CONFIG_ADDR, to_value)
        self.sa.solarcar.send(msg)
        
class TextIndicator(gtk.HBox):
    def __init__(self, label=None):
        gtk.HBox.__init__(self)
        self.text = gtk.Label(str="")
        self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
        if label is not None:
            self.label = gtk.Label(str=label)
            self.label.set_justify(gtk.JUSTIFY_LEFT)
            self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

        self.connect("destroy", self.destroy_cb)

    def destroy_cb(self, widg):
        return

    def set_text(self, text):
        self.text.set_text(text)

class LabelIndicator (NewListener, gtk.HBox):
    def __init__(self, store, nodename, channame, label=None, units=""):        
        NewListener.__init__(self, store, nodename, channame)
        gtk.HBox.__init__(self)
        self.units_string = units
        self.text = gtk.Label(str="")
        self.text.set_justify(gtk.JUSTIFY_RIGHT)
        self.text.set_alignment(1.0, 0.5)
        self.text.set_padding(4, 1)
        if label is not None:
            self.label = gtk.Label(str=label)
            self.label.set_justify(gtk.JUSTIFY_LEFT)
            self.label.set_alignment(0.0, 0.5)
            self.label.set_padding(4, 1)
            self.pack_start(self.label)
        self.pack_end(self.text)

        self.connect("destroy", self.destroy_cb)

    def destroy_cb(self, widg):
        self.stop()

    def stop(self):
        NewListener.stop(self)

    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
        self.text.set_text("%.3f%s" % (self.value, self.units_string))

    def set_units(self, units_string):
        self.units_string = units_string


# Linear interpolation at the moment. 
class ProductLabelIndicator(gtk.Label):
    def __init__(self, store, node1name, chan1name, node2name, chan2name, units=""):
        gtk.Label.__init__(self, str="P")
        self.chan1_last = None
        self.chan1_this = None
        self.chan2_last = None
        self.chan2_this = None

        self.units = units

        self.delivfunc1 = lambda x: self.deliver(1,x)
        self.delivfunc2 = lambda x: self.deliver(2,x)

        store.register_for_channel(node1name, chan1name, self.delivfunc1)
        store.register_for_channel(node2name, chan2name, self.delivfunc2)

    def destroy(self):
        store.unregister_for_all_deliveries(self.delivfunc1)
        store.unregister_for_all_deliveries(self.delivfunc2)
        gtk.Label.destroy()

    def __del__(self):
        store.unregister_for_all_deliveries(self.delivfunc1)
        store.unregister_for_all_deliveries(self.delivfunc2)

    def deliver(self, chan, pkt):
        if chan is 1:
            if self.chan1_this is not None:
                if self.chan1_this.get_time() < pkt.get_time():
                    self.chan1_last = self.chan1_this
                    self.chan1_this = pkt
                    self.most_recent = chan
            else:
                self.chan1_this = pkt
                self.most_recent = chan
        else:
            if self.chan2_this is not None:
                if self.chan2_this.get_time() < pkt.get_time():
                    self.chan2_last = self.chan2_this
                    self.chan2_this = pkt
                    self.most_recent = chan
            else:
                self.chan2_this = pkt
                self.most_recent = chan

        if (self.chan1_last is not None) and \
                (self.chan1_this is not None) and \
                (self.chan2_last is not None) and \
                (self.chan2_this is not None):
            
            if self.most_recent is 1:
                x1 = self.chan1_last.get_time()
                x2 = self.chan1_this.get_time()
                y1 = self.chan1_last.get_value()
                y2 = self.chan1_this.get_value()
                otherval = self.chan2_this.get_value()
                othertime = self.chan2_this.get_time()
            else:
                x1 = self.chan2_last.get_time()
                x2 = self.chan2_this.get_time()
                y1 = self.chan2_last.get_value()
                y2 = self.chan2_this.get_value()
                otherval = self.chan1_this.get_value()
                othertime = self.chan1_this.get_time()
                
            if x1 <= othertime and x2 >= othertime:
                valA = y1 + ((othertime - x1) / (x2 - x1)) * (y2 - y1)
                value = otherval * valA
                self.set_text("%.03f%s"%(value, self.units))
