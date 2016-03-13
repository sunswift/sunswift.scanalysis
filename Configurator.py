# --------------------------------------------------------------------------                                 
#  Scanalysis Configurator
#  File name: Configurator.py
#  Author: David Snowdon
#  Description: Configuration support
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
import pprint
import copy
import Driver

class TextConfig(gtk.Frame):
    def update_config(self, widg):
        self.config[self.configitem] = widg.get_text()

    def __init__(self, configitem, config, label="Text Config"):
        self.config = config
        self.configitem = configitem

        gtk.Frame.__init__(self, label=label)

        e = gtk.Entry()
        e.connect("changed", self.update_config)
        if self.configitem in self.config:
            e.set_text(str(self.config[self.configitem]))
        
        self.add(e)

class FloatConfig(TextConfig):
    def update_config(self, widg):
        self.config[self.configitem] = float(widg.get_text())

class IntConfig(TextConfig):
    def update_config(self, widg):
        self.config[self.configitem] = int(widg.get_text())

class BoolConfig(gtk.Frame):
    def update_config(self, widg):
        self.config[self.configitem] = self.checkbox.get_active()

    def __init__(self, configitem, config, label="List Config"):
        self.config = config
        self.configitem = configitem

        gtk.Frame.__init__(self, label=label)

        e = self.checkbox = gtk.CheckButton(label=label)
        e.connect("toggled", self.update_config)

        if configitem in config:
            e.set_active(config[configitem])

        self.add(e)


class ListConfig(gtk.Frame):
    def update_config(self, widg):
        self.config[self.configitem] = self.combobox.get_active_text()

    def __init__(self, configitem, config, options, label="List Config"):
        self.config = config
        self.configitem = configitem

        print self
        print configitem
        print config
        print options
        print label

        gtk.Frame.__init__(self, label=label)
        
        e = self.combobox = gtk.combo_box_new_text()
        for option in options:
            self.combobox.append_text(option)

        e.connect("changed", self.update_config)

        if configitem in config:
            if config[configitem] in options:
                e.set_active(options.index(config[configitem]))

        self.add(e)



class SimpleLoggerEditor(gtk.HBox):
    def edited_cb(self, editable):
        self.cfg["filename"] = self.entry.get_text()

    def __init__(self, cfg_item):
        gtk.HBox.__init__(self)
        self.cfg = cfg_item
        
        self.entry = entry = gtk.Entry(max=0)
        if "filename" not in cfg_item.keys():
            cfg_item["filename"] = "default.log"
        entry.set_text(cfg_item["filename"])
        entry.set_editable(True)
        entry.connect('changed', self.edited_cb)

        self.pack_start(gtk.Label(str="Simple Logger Filename"), expand=False)
        self.pack_end(entry, expand=True)

        
(
    MODLIST_NAME_COLUMN, 
    MODLIST_TYPE_COLUMN, 
    MODLIST_NUM_COLUMNS
) = range(3)

class Configurator:
    def destroy(self, widget, data=None):
        return

    def do_ok(self, widget, data=None):
        self.save_config()
        self.window.destroy()
        
    def do_new_module(self, widget):
        typename = self.combobox.get_active_text()

        i = 1
        while "%s %d"%(typename,i) in self.sa.modules:
            i += 1
        self.sa.modules.new_module(typename, "%s %d" % (typename,i))
        self.update_modlist_model()

    def do_remove_module(self, widget):
        (model,iter) = self.modlist.get_selection().get_selected()
        if iter is not None:
            (name,) = model.get(iter, MODLIST_NAME_COLUMN)
            self.sa.modules.remove_module(name)
            self.update_modlist_model()

    def modlist_edited_cb(self, cell, path, new_text, my_model):
        iter = self.modlist_model.get_iter(path)
        (oldname,) = self.modlist_model.get(iter, MODLIST_NAME_COLUMN)

        self.sa.modules.rename_module(oldname, new_text)
        self.update_modlist_model()

    def cursor_changed_cb(self, user):
        (path, column) = self.modlist.get_cursor()
        print path
        iter = self.modlist_model.get_iter(path)
        (name,) = self.modlist_model.get(iter, MODLIST_NAME_COLUMN)

        oldwidgs = self.configframe.get_children()
        for oldwidg in oldwidgs:
            self.configframe.remove(oldwidg)
        widg = self.sa.modules[name].configure()
        self.configframe.add(widg)
        self.configframe.set_label(self.sa.modules[name].get_display_name())
        self.configframe.show_all()

    def update_modlist_model(self):
        model = self.modlist_model

        # Get rid of everything that's there
        model.clear()

        # Transfer the relevant info from the module
        # DB to the model
        mods = self.sa.modules.keys()
        mods.sort()
        for mod in mods:
            model.append( row=[mod] )
        

    def create_module_list(self):
        # Scrolled window for view
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.modlist = modlist = gtk.TreeView()
        sw.add(modlist)
        self.modlist_model = model = gtk.ListStore(gobject.TYPE_STRING)
        modlist.set_model(model)
        
        # Create the single column 
        editablerenderer = gtk.CellRendererText()
        editablerenderer.set_property("xalign", 0.0)
        editablerenderer.set_property("editable", True)
        editablerenderer.connect('edited', self.modlist_edited_cb, model)
        column = gtk.TreeViewColumn("Name", editablerenderer, text=MODLIST_NAME_COLUMN) 
        modlist.append_column(column)

        modlist.set_rules_hint(True)
        modlist.connect('cursor-changed', self.cursor_changed_cb)
        

        # Update the store
        self.update_modlist_model()

        return sw

    def config_window(self):
        # Create a window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_default_size(600,400)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title("Configuration")

        # Top level HBox
        hbox = gtk.HBox()
        self.window.add(hbox)
        
        # Frame on the left
        self.configframe = gtk.Frame(label="None")
        hbox.pack_start(self.configframe, expand=True, fill=True)

        # Listview on the right
        vbox = gtk.VBox()
        hbox.pack_end(vbox, fill=False, expand=False)

        list = self.create_module_list()
        vbox.pack_start(list)

        # Add the buttons below the list 

        # Create the new/remove widgets
        newremove = gtk.Frame()
        my_box = gtk.HBox()
        newremove.add(my_box)

        types = Driver.modfac.keys()
        self.combobox = gtk.combo_box_new_text()
        for modtype in types:
            self.combobox.append_text(modtype)

        my_box.pack_start(self.combobox)

        but = gtk.Button(label="New")
        but.connect("clicked", self.do_new_module)
        my_box.pack_end(but, expand=False)

        vbox.pack_start(newremove, expand=False)

        newremove = gtk.Button(label="Remove")
        newremove.connect("clicked", self.do_remove_module)
        vbox.pack_start(newremove, expand=False)

        button = gtk.Button(label="Save")
        button.connect("clicked", self.do_ok)
        vbox.pack_end(button, expand=False, fill=False)

        # Show everything
        self.window.show_all()
        
        
    def set_default_config(self):
        # Set up a default configuration
        self.cfg = {}
        self.cfg["drivers"] = {}
        self.save_config()

    def __init__(self, sa, name="scanalysis.cfg"):
        self.sa = sa
        self.cfg_name = name
        self.read_config()
        
    def read_config(self):
        try:
            f = file(self.cfg_name)
            # Note: this is very insecure!
            self.cfg = eval(f.read())
            f.close()
        except IOError:
            self.set_default_config()
            
    def save_config(self):
        pp = pprint.PrettyPrinter(indent=4)
        f = file(self.cfg_name, mode="w+")
        pprint.pprint(self.cfg, stream=f)
        f.close()
