#!/usr/bin/env python
# --------------------------------------------------------------------------                                 
#  Scanalysis Main
#  File name: scanalysis.py
#  Author: David Snowdon, Etienne Le Sueur, Mark Yuan, Sam May
#  Description: The main scanalysis program
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

# These you shouldn't need to install
from optparse import OptionParser
import pprint, sys, copy, math

# You need to install these modules. They don't come with Python. 
import pygtk
pygtk.require('2.0')
import gtk
import gobject
gtk.gdk.threads_init()

# These are modules that we can't do without, so we import them directly
import NodeList
import Console
import Configurator

# Import the driver module
# Then import all the drivers in the Drivers directory
import Driver
from Drivers import *
import Can

# For the convenience functions -- should these be defined elsewhere?

class Scanalysis:
    def delete_event(self, widget, event, data=None):
        # sam: dave, you copied this out of the PyGTK tutorial.
        # I know cos I'm reading it now :)
        
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        
        # sam. cleanly shutdown modules
        # FlukeDriver at least uses the Module.stop() method to clean up, close
        # connections e.t.c
        try:
            for mod in self.modules.values():
                if mod is not None:                    
                    mod.stop()
        finally:
            gtk.main_quit()
            
    def toggle_fullscreen(self, widget, data=None):
        if self.is_full_screen is True:
            self.window.unfullscreen()
            self.is_full_screen = False
        else:
            self.window.fullscreen()
            self.is_full_screen = True
        
    def do_config(self, widget, data=None):
        self.cfg.config_window()

    def write_config(self, widget, data=None):
        self.cfg.save_config()

    def create_menubar(self):
        # File menu
        items = gtk.Menu()
                
        item = gtk.MenuItem("Config")
        item.connect("activate", self.do_config)
        items.append(item)

        item = gtk.MenuItem("Write Config")
        item.connect("activate", self.write_config)
        items.append(item)

        item = gtk.MenuItem("Quit")
        item.connect("activate", self.destroy)
        items.append(item)

        file_menu = gtk.MenuItem("File")    
        file_menu.set_submenu(items)    


        # View menu
        items = gtk.Menu()
                
        item = gtk.MenuItem("Fullscreen")
        item.connect("activate", self.toggle_fullscreen)
        items.append(item)

        view_menu = gtk.MenuItem("View")    
        view_menu.set_submenu(items)    

        # Create a menubar
        menubar = gtk.MenuBar()        
        menubar.append(file_menu)
        menubar.append(view_menu)
        
        return menubar
        
    def add_notebook_page(self, name, pagewidg):
        self.notebook.append_page(pagewidg, gtk.Label(str=name))
        self.notebook.show_all()

    def remove_notebook_page(self, pagewidg):
        n = self.notebook.get_n_pages()
        for i in range(n):
            widg = self.notebook.get_nth_page(i)
            if widg is pagewidg:
                self.notebook.remove_page(i)
#                pagewidg.destroy()

    def send_to_all_can(self, pkt):
        if isinstance(pkt, Can.Packet):
            for mod in self.modules:
                if isinstance(mod, Can.Interface):
                    mod.send(pkt)
            else:
                self.console.write("Tried to send non-CAN packet via CAN")

    def get_scandal_node_addr(self, name, nodetype=None, mod=None):
        if name in self.store:
            source = self.store[name]
            
            print "Looking at " + name
            if isinstance(source, ScandalDriver.ScandalNode):
                scandal = source.get_scandal()
                if nodetype is not None:
                    nodetypeid = scandal.lookup_type_id(nodetype)
                    if nodetypeid != source.get_node_type():
                        self.console.write("Node %s had an incorrect type (%d)" % (name, \
                                               source.get_node_type()),\
                                               mod=mod)
                        return None
                return source.get_addr()
            else:
                self.console.write("Node %s was not a Scandal node and should have been" % name, \
                                       mod=mod)
                return None
            
    # Logging feature
    def request_log(self, *args, **kwargs):
        if len(loggers) == 0:
            self.log_requests.append( (args, kwargs) )
        else:
            for logger in self.loggers:
                logger.request_log(*args, **kwargs)

    def register_logger(self, new_logger):
        self.console.write("New logger registered: " + new_logger.get_name())
        self.loggers.append(new_logger)
        for (args, kwargs) in self.log_requests:
            new_logger.request_log(*args, **kwargs)

            
    # Init function
    def __init__(self, config_name):
        # Do configuration stuff
        print "Starting with configuration: " + config_name
        self.cfg = Configurator.Configurator(self, name=config_name)

        # Create the datastore
        self.store = Driver.Datastore()
        
        # Set up the logging database
        self.log_requests=[]
        self.loggers=[]

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.is_full_screen = False
        self.window.set_default_size(1280,700)
        self.window.set_position(gtk.WIN_POS_CENTER)

        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)
    
        # Sets the border width of the window.
        self.window.set_border_width(0)
        
        # Create a vbox
        vbox = gtk.VBox()
        self.window.add(vbox)    
    
        self.menubar = self.create_menubar()
        vbox.pack_start(self.menubar, expand=False)
    
        # Create an hbox underneath the menubar
        paned = gtk.HPaned()
        vbox.add(paned)

        # Create a notebook
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        paned.pack1(self.notebook, resize=True, shrink=False)
        
        # Create the node list
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        paned.pack2(sw, resize=True, shrink=True)

        self.nodelist = NodeList.NodeList(self.store)
        sw.add(self.nodelist)
        gobject.timeout_add(1000, self.nodelist.update_colours)

        # Add the console pane
        self.console = Console.Console(self)
        self.add_notebook_page("console", self.console)

        # Set up the module DB
        # This instantiates the drivers from the config file
        if "modules" not in self.cfg.cfg:
            self.cfg.cfg["modules"] = {}
        self.modules = Driver.ModuleDB(self, self.cfg.cfg["modules"])

        # Show everything
        self.window.show_all()
        # and the window
        self.window.show()
        
        #while(1):
            #print("--------------")         
            #self.test_pkt = Can.Packet(1,[0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xF])
            #self.modules["Scandal"].can.send(self.test_pkt)
            #print("--------------")

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# Parse command line options
parser = OptionParser()
parser.add_option("-c", "--config", dest="config_name",
                  help="read and write configuration to/from FILE", metavar="FILE")

(options,args) = parser.parse_args()

# Set a default configuration name
if options.config_name is None:
    options.config_name = "scanalysis.cfg"

# If the program is run directly or passed as an argument to the python
# interpreter then create a Scanalysis instance and show it
if __name__ == "__main__":
    scanalysis = Scanalysis(options.config_name)
    scanalysis.main()
