# --------------------------------------------------------------------------                                 
#  Scanalysis NodeList
#  File name: NodeList.py
#  Author: David Snowdon, Etienne Le Sueur
#  Description: Suppot for the node list
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

import gobject
import gtk
import time
import Driver
from Drivers.ScandalDriver import *

#   Column numbering
(
    NAME_COLUMN, 
    VALUE_COLUMN, 
    COLOUR_COLUMN,
    OBJECT_COLUMN,
    NUM_COLUMNS
) = range(5)


INACTIVE_COLOUR = "Red"
ACTIVE_COLOUR = "Black"

class IterUpdater:
    def __init__(self, model, iter, nodelist):
        self.iter = iter
        self.model = model
        self.nodelist = nodelist
        self.last_pkt = None

    def deliver(self, value):
        if self.nodelist.updating:
            if self.last_pkt == None:
                self.last_pkt = value
            if self.last_pkt.get_time() < value.get_time():
                self.model.set(self.iter, VALUE_COLUMN, str(value),\
                                   COLOUR_COLUMN, ACTIVE_COLOUR)
            
class NodeList(gtk.TreeView):
    INACTIVE_TIMEOUT = 5.0
    NO_CHANNEL = -1

    def new_node(self, source):
        model = self.get_model()

        before_iter = model.get_iter_first()
        obj = None
        while before_iter is not None:
            (obj,) = model.get(before_iter, OBJECT_COLUMN)
            if obj is source: 
                break
            if cmp(obj, source) > 0: 
                break
            else:
                before_iter = model.iter_next(before_iter)
        
        if obj is source:
            node_iter = before_iter
        else:
            node_iter = model.insert_before(None, before_iter)
        nodename = source.get_display_name()
        
        # Set the data up
        model.set(node_iter, 
                    NAME_COLUMN, "%s" % (nodename), 
                    VALUE_COLUMN, "",
                    COLOUR_COLUMN, ACTIVE_COLOUR, 
                    OBJECT_COLUMN, source)

        source.register_for_updates(self.new_channel)

        for channel in source:
            self.new_channel(source[channel])

        return node_iter

    def new_channel(self, channel):
        model = self.get_model()
        source = channel.get_source()

        node_iter = model.get_iter_first()
        val = None
        while node_iter is not None:
            val = model.get_value(node_iter, OBJECT_COLUMN)
            if cmp(val, source) == 0:
                break
            node_iter = model.iter_next(node_iter)

        name = model.get_value(node_iter, NAME_COLUMN)

        before_iter = model.iter_children(node_iter)
        obj = None
        while before_iter is not None:
            obj = model.get_value(before_iter, OBJECT_COLUMN)
            
            if obj is channel:
                break

            if cmp(obj, channel) > 0: 
                break
            else:
                before_iter = model.iter_next(before_iter)
        
        # Don't add the same channel twice
        if obj is not channel: 
            chan_iter = model.insert_before(node_iter, before_iter)
        else:
            chan_iter = before_iter
        chan_name = channel.get_display_name()

        model.set(chan_iter, 
                    NAME_COLUMN, "%s" % chan_name, 
                    VALUE_COLUMN, "", 
                    COLOUR_COLUMN, "Black",
                    OBJECT_COLUMN, channel)

        iter_updater = IterUpdater(model, chan_iter, self)
        channel.register_for_delivery(iter_updater.deliver)

        return chan_iter        

    def update_colours(self):
        if self.updating is False:
            return True
            
        cur_time = time.time()
        model = self.get_model()

        iter = model.get_iter_first()
        while iter is not None:
            val = model.get_value(iter, OBJECT_COLUMN)

            if val.get_last_update() < cur_time - self.INACTIVE_TIMEOUT:
                model.set_value(iter, COLOUR_COLUMN, INACTIVE_COLOUR)
            else:
                model.set_value(iter, COLOUR_COLUMN, ACTIVE_COLOUR)
            iter = model.iter_next(iter)

            child = model.iter_children(iter)
            while child is not None:
                val = model.get_value(child, OBJECT_COLUMN)
                if val.get_last_update() < cur_time - self.INACTIVE_TIMEOUT:
                    model.set_value(child, COLOUR_COLUMN, INACTIVE_COLOUR)
                else:
                    model.set_value(child, COLOUR_COLUMN, ACTIVE_COLOUR)                
                child = model.iter_next(child)
                

        return 1
        
    def editing_started(self, cellrenderer, editable, path, data):
        self.saved_updating = self.updating
        self.updating = False
        
        # Set the editable text to the real name
        treestore = data
        obj = treestore[path][OBJECT_COLUMN]
        treestore[path][NAME_COLUMN] = obj.get_name()
        editable.set_text(obj.get_name())

        self.editing_iter = treestore[path]

    def editing_cancelled(self, cellrenderer):
        self.updating = self.saved_updating
        self.editing_iter[NAME_COLUMN] = \
            self.editing_iter[OBJECT_COLUMN].get_display_name()
        
    def edited_cb(self, cell, path, new_text, user_data):
        treestore = user_data
        obj = treestore[path][OBJECT_COLUMN]
        obj.set_name(new_text)
        treestore[path][NAME_COLUMN] = obj.get_display_name()
        self.queue_draw()
        self.updating = self.saved_updating
        return

    def create_context_menu(self, window, event, data=None):
        item_factory = gtk.ItemFactory(gtk.Menu, "<main>", None)
        self.item_factory = item_factory
        return item_factory.get_widget("<main>")

    def context_cb(self, treeview, event, data=None):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            pthinfo = self.get_path_at_pos(x,y)
            if pthinfo is not None:
                path,col,cellx,celly = pthinfo
                self.grab_focus()
                self.set_cursor(path,col,0)
                popup_menu = self.create_context_menu(self, self.window, None)

                for cb in self.menu_cbs:
                    items = cb(data)
                    for item in items:
                        menuItem = gtk.MenuItem(item[0])
                        menuItem.connect("button_press_event", item[1], self)
                        popup_menu.append(menuItem)
                        menuItem.show()

                popup_menu.popup(None, None, None, event.button, event.time)
        return

    def register_menu_cb(self, func):
        self.menu_cbs.append(func)
        return

    def __init__(self, store):
        gtk.TreeView.__init__(self)
      
        self.menu_cbs = []
 
        # Create the model
        model = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.set_model(model)

        # Create a text renderer
        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)

        editablerenderer = gtk.CellRendererText()
        editablerenderer.set_property("xalign", 0.0)
        editablerenderer.set_property("editable", True)
        editablerenderer.connect('edited', self.edited_cb, model)
        editablerenderer.connect('editing-started', self.editing_started, model)
        editablerenderer.connect('editing-canceled', self.editing_cancelled)
        
        # Create the two columns 
        column = gtk.TreeViewColumn("Name", editablerenderer, text=NAME_COLUMN, foreground=COLOUR_COLUMN) 
        column.add_attribute(editablerenderer, "text", NAME_COLUMN)
        self.append_column(column)

        column = gtk.TreeViewColumn("Value", renderer, text=VALUE_COLUMN, foreground=COLOUR_COLUMN) 
        self.append_column(column)
        
        self.set_rules_hint(True)
        
        self.connect('realize', lambda tv: tv.expand_all())
        
        self.datastore = []
        self.updating = True
                
        self.store = store
        self.store.register_for_updates(self.new_node)
       
        self.connect('button_press_event', self.context_cb, self)
 
        for source in store:
            self.new_node(store[source])
