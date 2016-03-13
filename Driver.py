# --------------------------------------------------------------------------                                 
#  Scanalysis Driver Support Architecture 
#  File name: Driver.py
#  Author: David Snowdon
#  Description: Part of the driver support architecture
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

import time
import gtk

class Deliverable:
    def __init__(self, value, timestamp=None):
        if timestamp is None:
            self.time = time.time()
        else:
            self.time = timestamp
        self.value = value

    def get_value(self):
        return self.value

    def get_time(self):
        return self.time

    def __str__(self):
        return str(self.get_value())

class Namable:
    def __init__(self, defaultname="Default"):
        self.name = defaultname

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name     
    
    def get_display_name(self):
        return self.name

    def __cmp__(self, other):
        if isinstance(other, Namable):
            return cmp(self.get_name(), other.get_name())
        else:
            return 0

class Deliverer:
    def __init__(self):
        self.delivery_list = []
        self.count = 0
        self.last_update = 0.0
        self.last_delivered = None

    def register_for_delivery(self, delivery_func):
        if delivery_func not in self.delivery_list:
            self.delivery_list.append(delivery_func)

    def unregister_for_delivery(self, delivery_func):
        if delivery_func in self.delivery_list:
            self.delivery_list.remove(delivery_func)
        
    def deliver(self, pkt):
        if not isinstance(pkt, Deliverable):
            print "Error - attempted to deliver non-deliverable item: " + str(pkt)
            return
        self.count += 1
        self.last_update = time.time()
        if self.last_delivered is None:
            self.last_delivered = pkt
        else:
            if self.last_delivered.get_time() <= pkt.get_time():
                self.last_delivered = pkt

        for delivery_func in self.delivery_list:
            delivery_func(pkt)

    def get_count(self):
        return self.count

    def get_last_update(self): 
        return self.last_update

    def get_last_delivered(self):
        return self.last_delivered

class Updateable:
    def __init__(self):
        self.update_list = []

    def update_me(self, value):
        for func in self.update_list:
            func(value)

    def register_for_updates(self, update_func):
        if update_func not in self.update_list:
            self.update_list.append(update_func)

    def unregister_for_updates(self, update_func):
        if update_func in self.update_list:
            self.update_list.remove(update_func)

class Channel(Deliverer, Namable):
    def __init__(self, source, name):
        Deliverer.__init__(self)
        Namable.__init__(self, name)
        self.source = source
        self.source[name] = self

    def deliver(self, deliverable):
        self.source.deliver(deliverable)
        Deliverer.deliver(self, deliverable)

    def get_source(self):
        return self.source

    def __cmp__(self, other):
        return Namable.__cmp__(self, other)

    def set_name(self, name):
        oldname = Namable.get_name(self)
        Namable.set_name(self, name)
        del self.source[oldname]
        self.source[name] = self

# Can be treated as a dictionary (DelivererContainer subclasses dict)
class Source(Deliverer, dict, Namable, Updateable):
    def __init__(self, store, name):
        dict.__init__(self)
        Deliverer.__init__(self)
        Namable.__init__(self, name)
        Updateable.__init__(self)

        self.store = store
        self.store[name] = self

    # Whenever we add a Channel, we set its name
    # to the same as the key we've used. 
    def __setitem__(self, key, value):
        dict.__setitem__(self,key,value)
        self.update_me(value)

    def set_name(self, name):
        oldname = Namable.get_name(self)
        Namable.set_name(self, name)
        del self.store[oldname]
        self.store[name] = self
 
    def deliver(self, deliverable):
        self.store.deliver(deliverable)
        Deliverer.deliver(self, deliverable)

    def get_store(self):
        return self.store

    def __cmp__(self, other):
        # Sort by class name first -- mostly this will be "source"
        val = cmp(self.__class__.__name__, other.__class__.__name__)
        if val == 0:
            return Namable.__cmp__(self, other)
        else:
            return val


# Can be treated as a dictionary (DelivererContainer subclasses dict)
class Datastore(Deliverer, dict, Updateable):
    def __init__(self):
        dict.__init__(self)
        Deliverer.__init__(self)
        Updateable.__init__(self)

        # List of channels we're waiting on
        self.sourcewaitlist = {}
        self.chanwaitlist = {}
        
        self.register_for_updates(self.waitlist_new_source)


    # For implementing the waitlist
    def waitlist_new_chan(self, chan):
        # value is a channel
        source = chan.get_source()
        if source.get_name() in self.chanwaitlist:
            if chan.get_name() in self.chanwaitlist[source.get_name()]:
                for delivery_func in self.chanwaitlist[source.get_name()][chan.get_name()]:
                    chan.register_for_delivery(delivery_func)

    def waitlist_new_source(self, source):
        source.register_for_updates(self.waitlist_new_chan)
        if source.get_name() in self.sourcewaitlist:
            for delivery_func in self.sourcewaitlist[source.get_name()]:
                source.register_for_delivery(delivery_func)

        if source.get_name() in self.chanwaitlist:
            for channel in source:
                if channel in self.chanwaitlist[source.get_name()]:
                    for delivery_func in self.chanwaitlist[source.get_name()][channel]:
                        source[channel].register_for_delivery(delivery_func)
        
    def __setitem__(self, key, source):
        dict.__setitem__(self,key,source)
        self.update_me(source)

    # Convenience functions
    def register_for_channel(self, nodename, channame, delivery_func):
        if nodename is None or channame is None:
            return None
        if nodename not in self.chanwaitlist:
            self.chanwaitlist[nodename] = {}
        if channame not in self.chanwaitlist[nodename]:
            self.chanwaitlist[nodename][channame] = []
        self.chanwaitlist[nodename][channame].append(delivery_func)

        if nodename in self:
            if channame in self[nodename]:
                self[nodename][channame].register_for_delivery(delivery_func)
                return self[nodename][channame]
        return None

    def register_for_node(self, nodename, delivery_func):
        if nodename not in self.sourcewaitlist:
            self.sourcewaitlist[nodename] = []
        self.sourcewaitlist[nodename].append(delivery_func)
        
        if nodename in self:
            self[nodename].register_for_delivery(delivery_func)
            return self[nodename]
        
        return None

    def unregister_for_all_deliveries(self, delivery_func):
        self.unregister_for_delivery(delivery_func)
        for source in self:
            self[source].unregister_for_delivery(delivery_func)
            for channel in self[source]:
                self[source][channel].unregister_for_delivery(delivery_func)

        for source in self.sourcewaitlist:
            if delivery_func in self.sourcewaitlist[source]:
                self.sourcewaitlist[source].remove(delivery_func)

        for source in self.chanwaitlist:
            for channel in self.chanwaitlist[source]:
                if delivery_func in self.chanwaitlist[source][channel]:
                    self.chanwaitlist[source][channel].remove(delivery_func)

    def unregister_for_all_updates(self, update_func):
        self.unregister_for_updates(update_func)
        for source in self:
            self[source].unregister_for_updates(update_func)

                

###
### Module class definition
###

# The module is initialised with a scanalysis structure, 
# a config (string indexed dictionary), and a name

# The sa object is expected to have the following attributes:
# "store" : a Datastore instance
# "console": a console instance

class Module(Namable):
    def __init__(self, sa, config, name="Default"):
        Namable.__init__(self, name)
        self.config = config
        self.sa = sa
        self.sa.console.write("Created", mod=self)
        self.running = True

    # Stops any activity in the module
    # Usually in preparation for deallocation
    def stop(self):
        self.running = False
        self.sa.console.write("Stopped", mod=self)
        
    # Create and return a widget which configures the driver
    # Returns a NULL widget
    def configure(self):
        return gtk.HBox()
        
class Driver(Module):
    def __init__(self, sa, config, name="DefaultDriver", *args, **kwds):
        Module.__init__(self, sa, config, name=name)
        self.deliverer = sa.store


class ModuleFactory(dict):
    def __init__(self):
        dict.__init__(self)

    # Convenience function
    def add_type(self, typename, typeclass):
        self[typename] = typeclass

    def create_module(self, typename, sa, config, name):
        if typename not in self:
            print "Tried to create a module of non-existant type! (%s)" % typename
            return None

        newmod = self[typename](sa, config, name=name)

        return newmod

# Note that this should only be instantiated after all the
# module factory stuff is set up. 
class ModuleDB(dict):
    def __init__(self, sa, config):
        dict.__init__(self)
        self.sa = sa
        self.config = config

        # Config is a dictionary of name:(typename, config) pairs
        names = self.config.keys()
        names.sort()
        for name in names:
            (typename, modconfig) = self.config[name]
            self.create_module(typename, modconfig, name)

    def create_module(self, typename, modconfig, name):
        self[name] = modfac.create_module(typename, self.sa, modconfig, name=name)
        
    def new_module(self, typename, name):
        modconfig = {}
        self.config[name] = (typename, modconfig)
        self.create_module(typename, modconfig, name)

    def remove_module(self, name):
        if name in self:
            self[name].stop()
            del self[name]
            del self.config[name]

    def rename_module(self, oldname, newname):
        oldconf = self.config[oldname]
        oldmod = self[oldname]
        del self.config[oldname]
        del self[oldname]
        self.config[newname] = oldconf
        self[newname] = oldmod
        oldmod.set_name(newname)

               
# Global
modfac = ModuleFactory()
