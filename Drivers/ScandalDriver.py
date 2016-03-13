import Driver
import Misc
import Scandal
import gtk
import gobject
import pprint
import Can
import Configurator
import time

def scandal_decode_packet(pkt):
    pkt_type = (pkt.id >> Scandal.Packet.TYPE_OFFSET) & Scandal.Packet.TYPE_MASK
    
    if pkt_type == Scandal.Packet.CHANNEL_TYPE:
        return Scandal.ChannelPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.CONFIG_TYPE:
        return Scandal.ConfigPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.HEARTBEAT_TYPE:
        return Scandal.HeartbeatPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.SCANDAL_ERROR_TYPE:
        return Scandal.ErrorPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.USER_ERROR_TYPE:
        return Scandal.UserErrorPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.RESET_TYPE:
        return Scandal.ResetPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.USER_CONFIG_TYPE:
        return Scandal.UserConfigPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.COMMAND_TYPE:
        return Scandal.CommandPacket(pkt=pkt)
    elif pkt_type == Scandal.Packet.TIMESYNC_TYPE:
        return Scandal.TimesyncPacket(pkt=pkt)
    else:
        print "Scandal.Packet: tried to decode non-Scandal packet"
	print "ID: 0x%08x" % pkt.get_id()
	print "Data: " + str(pkt.get_data())

        return None


class ScandalNode(Driver.Source):
    def __init__(self, store, scandal, addr, mytype):
        self.addr = addr
        self.channels = {}
        self.mytype = mytype
        self.scandal = scandal
        name = self.scandal.get_node_name(mytype, addr)
        Driver.Source.__init__(self, store, name)

    def get_display_name(self):
        return "%s (%d)" % (self.get_name(), self.addr)

    def set_name(self, name):
        Driver.Source.set_name(self, name)
        self.scandal.set_node_name(self.get_node_type(), \
                                       self.get_addr(), name)

    def set_channel(self, chan_num, channel):
        self.channels[chan_num] = channel

    def get_channels(self):
        return self.channels

    def get_addr(self):
        return self.addr

    def get_node_type(self):
        return self.mytype

    def get_scandal(self):
        return self.scandal

    def __cmp__(self, other):
        if isinstance(other, ScandalNode):
            return cmp(self.get_addr(), other.get_addr())
        else:
            return Driver.Source.__cmp__(self,other)

class ScandalChannel(Driver.Channel, Misc.Calibrateable):
    def __init__(self, node, scandal, chan_num): 
        self.chan_num = chan_num
        self.scandal = scandal
        name = self.scandal.get_chan_name(node.get_node_type(), \
                                              node.get_addr(), \
                                              chan_num)

        # Add the channel to the numbered index in the node
        node.set_channel(chan_num, self)

        # Do the normal driver init stuff
        Driver.Channel.__init__(self, node, name)
        

    def get_display_name(self):
        return "%s (%d)" % (self.get_name(), self.chan_num)

    def set_name(self, name):
        Driver.Channel.set_name(self, name)
        self.scandal.set_chan_name(self.get_source().get_node_type(), \
                                       self.get_source().get_addr(), \
                                       self.get_chan_num(), name)

    def get_chan_num(self):
        return self.chan_num

    def __cmp__(self, other):
        if isinstance(other, ScandalChannel):
            return cmp(self.get_chan_num(), other.get_chan_num())
        else:
            return Driver.Channel.__cmp__(self,other)
            
    def set_mb(self, (m,b), mode64=False):
        Misc.Calibrateable.set_mb(self, (m,b))
        
        if mode64: # If we are doing 64 bit scaling
            scandalm = int(m*1024*1024.0)
            scandalb = int(b*1024.0*1000.0)
        else:
            scandalm = int(m*1024.0)
            scandalb = int(b*1.0*1024.0*1000.0)
            
        msg = Scandal.OutChanMConfigPacket(destaddr=self.get_source().get_addr(), 
                                            chan=self.get_chan_num(), 
                                            m=scandalm)
        self.scandal.send(msg)
        print "SEnding M: %d" % scandalm
        time.sleep(10.0)

        msg = Scandal.OutChanBConfigPacket(destaddr=self.get_source().get_addr(), 
                                            chan=self.get_chan_num(), 
                                            b=scandalb)
        self.scandal.send(msg)

        print "SEnding B: %d" % scandalb

class CanTypeSelector(Configurator.ListConfig):
    def __init__(self, mydriver, configitem, config, options, label="Can Type Selector"):
        self.mydriver = mydriver
        Configurator.ListConfig.__init__(self, configitem, config, options, label=label)

    def update_config(self, widg):
        Configurator.ListConfig.update_config(self, widg)
        self.mydriver.config["can"]["config"] = {}
        self.mydriver.restart_can()

class ScandalDriver(Driver.Driver):
    devices = None    
    SD_FILE = "scandal_devices_file_name"

    def __init__(self, sa, config, name="ScandalDriver"):
        Driver.Driver.__init__(self, sa, config, name=name)

        # Temporary measure while we don't have a config
        # or a method of starting drivers automagically
        # We really need a start_driver function or something
        
        self.can = None
        self.can_log = None
        if "can" not in self.config:
            self.config["can"] = can_conf = {}
            can_conf["config"] = {}

        if "nodes" not in self.config:
            self.config["nodes"] = {}

        if "timesyncs" not in self.config:
            self.config["timesyncs"] = False

        if ScandalDriver.SD_FILE not in self.config:
            self.config[ScandalDriver.SD_FILE] = "scandal_devices.cfg"

        self.nodelist = {}

        self.read_sd_config()

        self.dev_config_window = None
        self.can_config_window = None

        self.restart_can()

        if self.config["timesyncs"]:
            gobject.timeout_add(1000, self.do_send_timesync_cb)


    def stop(self):
        self.sa.store.unregister_for_all_deliveries(self.recv_can_pkt)
        if self.can is not None:
            self.can.stop()
            del self.can
        if self.dev_config_window is not None:
            self.dev_config_window.destroy()
        if self.can_config_window is not None:
            self.can_config_window.destroy()
        if self.can_log != None:
            self.can_log.close()

    def send(self, pkt):
        self.can.send(pkt)

    def recv_can_pkt(self, pkt):
        scandalpkt = scandal_decode_packet(pkt)
        
        # Handle channel packets
        if isinstance(scandalpkt, Scandal.ChannelPacket):
            addr = scandalpkt.get_addr()
            if addr in self.nodelist:
                chan = scandalpkt.get_channel()
                node = self.nodelist[addr]
                chanlist = node.get_channels()

                if chan not in chanlist:
                    # Get the inital channel name
                    nodetype = node.get_node_type()
                    nodeaddr = node.get_addr()
                    channame = self.get_chan_name(nodetype, nodeaddr, chan)
                    
                    # Create the new channel
                    chanlist[chan] = ch = ScandalChannel(node, self, chan)

                    # Add it to the source/node -- renames in the process
                    node[channame] = chanlist[chan]

                # Deliver the packet
                chanlist[chan].deliver(scandalpkt)

        # If this is a heartbeat packet, 
        elif isinstance(scandalpkt, Scandal.HeartbeatPacket):
            addr = scandalpkt.get_addr()
            nodetype = scandalpkt.get_node_type()
            if addr not in self.nodelist:
                nodename = self.get_node_name(nodetype, addr)
                
                # Create the new node
                self.nodelist[addr] = ScandalNode(self.sa.store, self, \
                                                      addr, nodetype)

                # Add it to the source/node -- renames in the process
                self.sa.store[nodename] = self.nodelist[addr]

            # Deliver the packet
            self.nodelist[addr].deliver(scandalpkt)

        elif isinstance(scandalpkt, Scandal.UserErrorPacket):
            errornum = scandalpkt.get_errornum()

            addr = scandalpkt.get_addr()
            if addr not in self.nodelist.keys():
                return
                
            node = self.nodelist[addr]
            mytype = node.get_node_type();
            
            errorname = self.get_type_error_name_from_number(mytype, errornum)
            if errorname is None:
                errorname = "Unknown Error"

            self.sa.console.write("Got error: \"" + errorname + "\" (" + str(errornum) + ") from " + node.get_display_name(), mod=self)

        elif isinstance(scandalpkt, Scandal.TimesyncPacket):
            self.sa.console.write("Got a TimesyncPacket: New time is: %lf" % (scandalpkt.get_new_time()), mod=self)
            self.sa.console.write("Old time was: %lf" % time.time(), mod=self)
            self.sa.console.write("Difference is: %lf" % 
                                  (time.time() - scandalpkt.get_time()), 
                                  mod=self)


        # If this is some other type of packet
        else:
            self.sa.store.deliver(scandalpkt)

    def can_log_delivery(self, pkt):
        self.can_log.write("%08x " % pkt.get_id())
        data = pkt.get_data()
        for byte in data:
            self.can_log.write("%02x" % byte)
        self.can_log.write(" %f\n" % pkt.get_recvd())

    def restart_can(self):
        if self.can is not None:
            self.can.stop()
            del self.can

        can_conf = self.config["can"]

        if "type" in can_conf:
            self.can = Driver.modfac.create_module(can_conf["type"], \
                                                       self.sa, \
                                                       can_conf["config"], \
                                                       self.get_name() + " CAN")

            # CAN log
            if self.can_log != None:
                self.can_log.close()
            self.can_log = file(self.get_name() + ".log", "a+")

            if self.can is not None:
                self.can.register_for_delivery(self.recv_can_pkt)
                self.can.register_for_delivery(self.can_log_delivery)

        else:
            self.can = None

            
    # Called periodically to send time synchronisation messages
    def do_send_timesync_cb(self):
        pkt = Scandal.TimesyncPacket(newtime=time.time())
        self.send(pkt)

        self.sa.console.write("Sending new timestamp: " + str(pkt.get_time()), mod=self)
        
        # Return true if timesyncs is set
        return self.config["timesyncs"]


    # Called when we click a button to bring up the device config window
    def do_device_config_cb(self, widg):
        if self.dev_config_window is not None:
            return

        window = self.dev_config_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("destroy", self.device_config_destroy_cb)
        window.set_default_size(600,400)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title("Configure Scandal Devices")

        vbox = gtk.VBox()
        window.add(vbox)

        devpage = ScandalDevicesPage(self.__class__.devices)
        vbox.pack_start(devpage)        

        but = gtk.Button(label="Save Dev Config")
        but.connect("clicked", self.save_sd_config_cb)
        vbox.pack_end(but, expand=False, fill=False)

        window.show()
        window.show_all()

    def device_config_destroy_cb(self, widget, data=None):
        self.dev_config_window = None

    def save_sd_config_cb(self, widg):
        self.save_sd_config()

    def can_config_destroy_cb(self, widget, data=None):
        self.can_config_window = None

    def do_config_interface_cb(self, widg):
        if self.can is None:
            self.sa.console.write("Tried to configure non-existent CAN interface")
            return
        
        window = self.can_config_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("destroy", self.can_config_destroy_cb)
        window.set_default_size(600,400)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title("Configure CAN Interface")
        self.can_config_window = window

        vbox = gtk.VBox()
        window.add(vbox)

        conf = self.can.configure()
        vbox.pack_start(conf, expand=True)

        window.show()
        window.show_all()

    # Overrides the Module version
    def configure(self):
        widg = Driver.Driver.configure(self)

        vbox = gtk.VBox()
        widg.pack_start(vbox)

        but = gtk.Button(label="Config Devices")
        but.connect("clicked", self.do_device_config_cb)
        vbox.pack_start(but, expand=False, fill=False)

        hbox = gtk.HBox()
        vbox.pack_start(hbox, expand=False)

        ifaces = []
        for module in Driver.modfac:
            if issubclass(Driver.modfac[module], Can.Interface):
                ifaces.append(module)
        ifaces.sort()
        typelist = CanTypeSelector(self, "type", self.config["can"], ifaces, label="Can Interface Module")
        hbox.pack_start(typelist, expand=True)

        but = gtk.Button(label="Config Interface")
        but.connect("clicked", self.do_config_interface_cb)
        hbox.pack_start(but, expand=False)

        timesync = Configurator.BoolConfig("timesyncs", self.config, label="Send Timesync Messages")
        vbox.pack_start(timesync, expand=False, fill=False)

        return widg

    # Functions for reading and writing the sd config file
    def read_sd_config(self):
        try:
            f = file(self.config[ScandalDriver.SD_FILE])
            # Note: this is very insecure!
            self.__class__.devices = eval(f.read())
            f.close()
        except IOError:
            self.__class__.devices = {}
            
    def save_sd_config(self):
        pp = pprint.PrettyPrinter(indent=4)
        f = file(self.config[ScandalDriver.SD_FILE], mode="w+")
        pprint.pprint(self.__class__.devices, stream=f)
        f.close()

    def get_node_config(self, nodetype, addr):
        if addr not in self.config["nodes"]:
            self.config["nodes"][addr] = {"type": nodetype}
        
        nodeconf = self.config["nodes"][addr]

        # If the type aint right, delete the old config. 
        # Harsh, but fair. 
        if nodeconf["type"] != nodetype:
            print "WARNING: Re-setting config for node %d/%d" % (nodetype, addr)
            self.config["nodes"][addr] = {"type": nodetype}

        # FIXME: Might want to ask for the config to be written 
        # at this point
        return nodeconf
        
    def get_channel_config(self, nodetype, addr, chan_num):
        nodeconf = self.get_node_config(nodetype, addr)
        
        if "channels" not in nodeconf:
            nodeconf["channels"] = {}

        if chan_num not in nodeconf["channels"]:
            nodeconf["channels"][chan_num] = {}

        return nodeconf["channels"][chan_num]

    # Functions for naming, etc. 
    def get_node_name(self, nodetype, addr):
        nodeconf = self.get_node_config(nodetype, addr)
        if "name" in nodeconf:
            return nodeconf["name"]            
        else:
            name = self.get_type_node_name(nodetype)
            if name is not None:
                return name + " " + str(addr)
            else:
                return "Node %d/%d" % (nodetype, addr)

    def set_node_name(self, nodetype, addr, name):
        nodeconf = self.get_node_config(nodetype, addr)
        nodeconf["name"] = name

    def get_chan_name(self, nodetype, addr, chan_num):
        chanconf = self.get_channel_config(nodetype, addr, chan_num)
        if "name" in chanconf:
            return chanconf["name"]
        else:
            name = self.get_type_chan_name(nodetype, chan_num)
            if name is not None:
                return name
            else:
                return "Chan %d:%d" % (addr, chan_num)

    def set_chan_name(self, nodetype, addr, chan_num, name):
        chanconf = self.get_channel_config(nodetype, addr, chan_num)
        chanconf["name"] = name

    # Devices configs
    def get_type_node_config(self, nodetype):
        devs = self.__class__.devices
        if nodetype not in devs:
            devs[nodetype] = {}
        
        return devs[nodetype]

    def get_type_chan_config(self, nodetype, chan_num):
        nodetypeconf = self.get_type_node_config(nodetype)
        if "channels" not in nodetypeconf:
            nodetypeconf["channels"] = {}
        
        if chan_num not in nodetypeconf["channels"]:
            nodetypeconf["channels"][chan_num] = {}

        return nodetypeconf["channels"][chan_num]

    def get_type_node_name(self, nodetype):
        nodetypeconf = self.get_type_node_config(nodetype)
        if "name" not in nodetypeconf:
            return None
        else:
            return nodetypeconf["name"]

    def get_type_chan_name(self, nodetype, chan_num):
        chantypeconf = self.get_type_chan_config(nodetype, chan_num)
        if "name" not in chantypeconf:
            return None
        else:
            return chantypeconf["name"]

    def get_type_userconfig_number_from_name(self, nodetype, config_name):
        nodeconfig = self.get_type_node_config(nodetype)
        if "configs" in nodeconfig:
            for config in nodeconfig["configs"]:
                if nodeconfig["configs"][config]["name"] == config_name:
                    return config
        return None

    def get_type_command_number_from_name(self, nodetype, command_name):
        nodeconfig = self.get_type_node_config(nodetype)
        if "commands" in nodeconfig:
            for command in nodeconfig["commands"]:
                if nodeconfig["commands"][command]["name"] == command_name:
                    return command
        return None

    def get_type_error_name_from_number(self, nodetype, error_number):
        nodeconfig = self.get_type_node_config(nodetype)
        if "errors" in nodeconfig:
            if error_number not in nodeconfig["errors"]:
                return None
            else:
                return nodeconfig["errors"][error_number]["name"]

    # Look up the type ID for a type of device, given its name
    # e.g. MPPTNG is type 22
    def lookup_type_id(self, nodetype):
        devs = self.__class__.devices
        for dev in devs:
            if "name" in devs[dev]:
                if devs[dev]["name"] == nodetype:
                    return dev
        return None

    # Look up the type name for a given device type ID
    def lookup_type_name(self, nodetypeid):
        devs = self.__class__.devices
        if nodetypeid in devs:
            if "name" in devs[nodetypeid]:
                return devs[nodetypeid]["name"]
        return None
        

# Configuration -- editor for the scandal devices config file
#   Device list column numbering
(
    DEVICELIST_NAME_COLUMN, 
    DEVICELIST_TYPE_COLUMN, 
    DEVICELIST_NUM_COLUMNS
) = range(3)

( 
    DEVICEPAGE_LIST_TYPE_COLUMN, 
    DEVICEPAGE_LIST_NAME_COLUMN,
    DEVICEPAGE_LIST_NUM_COLUMNS
) = range(3)

class ScandalDevicesPageEditor(gtk.VBox):
    def new_entry_cb(self, widget):
        for id in range(1024):
            if id not in self.cfg.keys():
                break
        self.cfg[id] = {"name": "New"}
        self.update_model()

    def delete_entry_cb(self, widget):
       (path, column) = self.list.get_cursor()
       iter = self.model.get_iter(path)
       (id,) = self.model.get(iter, DEVICEPAGE_LIST_TYPE_COLUMN)
       del self.cfg[id]
       self.update_model()
       


    def edited_cb(self, cell, path, new_text, column):
        iter = self.model.get_iter(path)
        (id,oldname) = self.model.get(iter, DEVICEPAGE_LIST_TYPE_COLUMN, DEVICEPAGE_LIST_NAME_COLUMN)

        if column is DEVICEPAGE_LIST_NAME_COLUMN:
            self.cfg[id]["name"] = new_text
    
        if column is DEVICEPAGE_LIST_TYPE_COLUMN:
            new_id = int(new_text)
            self.cfg[new_id]["name"] = self.cfg[id]["name"]
            del self.cfg[id]
            
        self.update_model()

    def update_model(self):
        self.model.clear() # Remove everything
        
        if self.cfg is not None:
            # Populate the store
            mykeys = self.cfg.keys()
            mykeys.sort()
            for id in mykeys:
                if "name" in self.cfg[id]:
                    name = self.cfg[id]["name"]
                else:
                    name = "Default " + str(id)
                node = self.model.append( row=[id, name] )

    def update_store(self, new_cfg):
        self.cfg = new_cfg
        self.update_model()

    def __init__(self, name, cfg_item):
        gtk.VBox.__init__(self)
        self.cfg = cfg_item
        self.pack_start(gtk.Label(str=name), expand=False)
        
        hbox = gtk.HBox()
        self.pack_end(hbox, expand=False)

        but = gtk.Button(label="New")
        but.connect('clicked', self.new_entry_cb)
        hbox.pack_end(but, expand=False)

        but = gtk.Button(label="Delete")
        but.connect('clicked', self.delete_entry_cb)
        hbox.pack_end(but, expand=False)


        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.pack_start(sw)
        
        self.list = list = gtk.TreeView()
        sw.add(list)
        self.model = model = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
        list.set_model(model)
        
        # Create the two columns 
        editablerenderer = gtk.CellRendererText()
        editablerenderer.set_property("xalign", 0.0)
        editablerenderer.set_property("editable", True)
        editablerenderer.connect('edited', self.edited_cb, DEVICEPAGE_LIST_TYPE_COLUMN)
        column = gtk.TreeViewColumn("Type ID", editablerenderer, text=DEVICEPAGE_LIST_TYPE_COLUMN) 
        list.append_column(column)

        # Create the two columns 
        editablerenderer = gtk.CellRendererText()
        editablerenderer.set_property("xalign", 0.0)
        editablerenderer.set_property("editable", True)
        editablerenderer.connect('edited', self.edited_cb, DEVICEPAGE_LIST_NAME_COLUMN)
        column = gtk.TreeViewColumn("Name", editablerenderer, text=DEVICEPAGE_LIST_NAME_COLUMN) 
        list.append_column(column)
        
        list.set_rules_hint(True)
        
        self.update_model()

class ScandalDevicesPage(gtk.HBox):
    def devicelist_edited(self, cell, path, new_text, (my_model, my_config, column)):
        iter = self.model.get_iter(path)
        (id,) = self.model.get(iter, DEVICELIST_TYPE_COLUMN)
        store = self.devicenames[int(id)]
        
        if column is DEVICELIST_TYPE_COLUMN:
            newid = int(new_text)
            self.devicenames[newid] = store
            del self.devicenames[id]

        if column is DEVICELIST_NAME_COLUMN:
            store["name"] = new_text

        self.update_store()

    def cursor_changed_cb(self, user):
        (path, column) = self.devicelist.get_cursor()
        iter = self.model.get_iter(path)
        (id,) = self.model.get(iter, DEVICELIST_TYPE_COLUMN)
        new_store = self.devicenames[int(id)]

        if "channels" not in new_store:
            new_store["channels"] = {}
        if "inchannels" not in new_store:
            new_store["inchannels"] = {}
        if "configs" not in new_store:
            new_store["configs"] = {}
        if "errors" not in new_store:
            new_store["errors"] = {}
        if "commands" not in new_store:
            new_store["commands"] = {}

        self.channels_editor.update_store(new_store["channels"])
        self.inchannels_editor.update_store(new_store["inchannels"])
        self.configs_editor.update_store(new_store["configs"])
        self.errors_editor.update_store(new_store["errors"])
        self.commands_editor.update_store(new_store["commands"])


    def new_device_cb(self, widget):
        # Look for a free ID in the first 1024
        for id in range(1024):
            if id not in self.devicenames.keys():
                break; 

        # Populate the new device
        self.devicenames[id] = {}
        self.devicenames[id]["name"] = "New Device Type"
        self.devicenames[id]["channels"] = {}
        self.devicenames[id]["inchannels"] = {}
        self.devicenames[id]["configs"] = {}
        self.devicenames[id]["errors"] = {}
        self.devicenames[id]["commands"] = {}

        self.update_store()

    def update_store(self):
        self.model.clear()
        devs = self.devicenames.keys()
        devs.sort()
        for devicetype in devs:
            if "name" not in self.devicenames[devicetype]:
                name = "Node Type %d" % devicetype
            else:
                name = self.devicenames[devicetype]["name"]

            node = self.model.append( row=[name, devicetype] )

    def __init__(self, devicenames):
        gtk.HBox.__init__(self)

        self.devicenames = devicenames
        
        ################################################
        # Simple list on the right for the device types
        ################################################
        vbox = gtk.VBox()
        self.pack_end(vbox, expand=False)
        vbox.pack_start(gtk.Label(str="Devices"), expand=False)
        
        but = gtk.Button(label="New Device")
        but.connect('clicked', self.new_device_cb)

        vbox.pack_end(but, expand=False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)
        
        self.devicelist = devicelist = gtk.TreeView()
        sw.add(devicelist)
        self.model = model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        print "Initial type: " + str(type(model))
        devicelist.set_model(model)
        
        # Create the two columns 
        editablerenderer = gtk.CellRendererText()
        editablerenderer.set_property("xalign", 0.0)
        editablerenderer.set_property("editable", True)
        editablerenderer.connect('edited', self.devicelist_edited, (model, self, DEVICELIST_NAME_COLUMN))
        column = gtk.TreeViewColumn("Name", editablerenderer, text=DEVICELIST_NAME_COLUMN) 
        devicelist.append_column(column)

        # Create the two columns 
        editablerenderer = gtk.CellRendererText()
        editablerenderer.set_property("xalign", 0.0)
        editablerenderer.set_property("editable", True)
        editablerenderer.connect('edited', self.devicelist_edited, (model, self, DEVICELIST_TYPE_COLUMN))
        column = gtk.TreeViewColumn("Type ID", editablerenderer, text=DEVICELIST_TYPE_COLUMN) 
        devicelist.append_column(column)
        
        devicelist.set_rules_hint(True)

        self.devicelist.connect('cursor-changed', self.cursor_changed_cb)
        

        # Update the store
        self.update_store()

        ################################################
        # Pane on the left for editing values
        ################################################
        vbox = gtk.VBox()
        self.pack_start(vbox)

        self.channels_editor = ScandalDevicesPageEditor("Out Channels", None)
        vbox.pack_start(self.channels_editor) 

        self.inchannels_editor = ScandalDevicesPageEditor("In Channels", None)
        vbox.pack_start(self.inchannels_editor) 

        self.configs_editor = ScandalDevicesPageEditor("Config", None)
        vbox.pack_start(self.configs_editor) 

        self.errors_editor = ScandalDevicesPageEditor("Errors", None)
        vbox.pack_start(self.errors_editor) 

        self.commands_editor = ScandalDevicesPageEditor("Commands", None)
        vbox.pack_start(self.commands_editor) 

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Scandal", ScandalDriver)
