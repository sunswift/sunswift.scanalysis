# --------------------------------------------------------------------------                                 
#  Scanalysis Scandal Abstraction
#  File name: Scandal.py
#  Author: David Snowdon
#  Description: The abstraction between scanalysis and Scandal
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
import sys

import Can
import Driver

import time
import math

def scandal_decode_packet(pkt):
    pkt_type = (pkt.id >> Packet.TYPE_OFFSET) & Packet.TYPE_MASK
    
    if pkt_type == Packet.CHANNEL_TYPE:
        return ChannelPacket(pkt=pkt)
    elif pkt_type == Packet.CONFIG_TYPE:
        return ConfigPacket(pkt=pkt)
    elif pkt_type == Packet.HEARTBEAT_TYPE:
        return HeartbeatPacket(pkt=pkt)
    elif pkt_type == Packet.SCANDAL_ERROR_TYPE:
        return ErrorPacket(pkt=pkt)
    elif pkt_type == Packet.USER_ERROR_TYPE:
        return UserErrorPacket(pkt=pkt)
    elif pkt_type == Packet.RESET_TYPE:
        return ResetPacket(pkt=pkt)
    elif pkt_type == Packet.USER_CONFIG_TYPE:
        return UserConfigPacket(pkt=pkt)
    elif pkt_type == Packet.COMMAND_TYPE:
        return CommandPacket(pkt=pkt)
    elif pkt_type == Packet.TIMESYNC_TYPE:
        return TimesyncPacket(pkt=pkt)
    else:
        print "Packet: tried to decode non-Scandal packet"
	print "ID: 0x%08x" % pkt.get_id()
	print "Data: " + str(pkt.get_data())

        return None

def bytes_to_int(bytes):
    value = 0
    for i in range(len(bytes)):
        value <<= 8
        value += bytes[i]
    return value

def int_to_bytes(myint, numbytes):
    bytes = []
    for i in range(numbytes):
        bytes = [myint & 0xFF] + bytes
        myint >>= 8
    return bytes

class Packet(Can.Packet):
    # Packet type numbers
    ( CHANNEL_TYPE, 
      CONFIG_TYPE, 
      HEARTBEAT_TYPE, 
      SCANDAL_ERROR_TYPE,
      USER_ERROR_TYPE,
      RESET_TYPE,
      USER_CONFIG_TYPE,
      COMMAND_TYPE,
      TIMESYNC_TYPE,
      NUM_TYPES ) = range(10)

    # Packet defs
    PRIO_OFFSET = 26
    PRIO_MASK = 0x07
    TYPE_OFFSET = 18
    TYPE_MASK = 0xFF

    def get_prio(self):
        return (self.id >> Packet.PRIO_OFFSET) & Packet.PRIO_MASK

    def get_type(self):
        return (self.id >> Packet.TYPE_OFFSET) & Packet.TYPE_MASK
        
    (CONFIG_ADDR, 
     CONFIG_IN_CHAN_SOURCE, 
     CONFIG_OUT_CHAN_M, 
     CONFIG_OUT_CHAN_B) = range(4)

    def __init__(self, id, data):
        Can.Packet.__init__(self, id, data)
        self.creationtime = time.time()

class ChannelPacket(Packet, Driver.Deliverable):
    ADDR_OFFSET=10
    ADDR_MASK = 0xFF

    CHANNEL_OFFSET=0
    CHANNEL_MASK=0x3FF

    def __init__(self, pkt=None, addr=0, channel=0, value=0, rawvalue=None, rawtime=None):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.CHANNEL_TYPE << Packet.TYPE_OFFSET |\
            (addr & ChannelPacket.ADDR_MASK) << \
                                 ChannelPacket.ADDR_OFFSET |\
            (channel & ChannelPacket.CHANNEL_MASK) << \
                                 ChannelPacket.CHANNEL_OFFSET

        raw_time = int(int((time.time() * 1000.0)) & 0xFFFFFFFF)

        data = int_to_bytes(value, 4) + \
            int_to_bytes(raw_time, 4)

        Packet.__init__(self, id, data)


    def get_addr(self):
        return (self.id >> self.ADDR_OFFSET) & self.ADDR_MASK

    def get_channel(self):
        return (self.id >> self.CHANNEL_OFFSET) & self.CHANNEL_MASK

    def get_raw_value(self):
        value = bytes_to_int(self.data[0:4])
        # Sign conversion
        #if self.data[0] & 0x80:
                
        if value > (1<<31):
            value = -int(value ^ 0xFFFFFFFF)
            
        return value

    def get_raw_time(self):
#        return bytes_to_int(self.data[4:8])
        normalraw = int(self.creationtime * 1000.0);
        
#        candidatetime1 = normalraw & 0xFFFFFFFF00000000 + (bytes_to_int(self.data[4:8]))
#        candidatetime2 = (normalraw + 0x0000000100000000) & 0xFFFFFFFF00000000 + (bytes_to_int(self.data[4:8]))
#        candidatetime3 = (normalraw - 0x0000000100000000) & 0xFFFFFFFF00000000 + (bytes_to_int(self.data[4:8]))
        
#        print 
#        print comptime
#        print candidatetime1 
#        print candidatetime2
        
#        print "raw"
#        print bytes_to_int(self.data[4:8])
#        print "comp"
#        print normalraw
#        print 1
#        print normalraw - candidatetime1
#        print 2
#        print normalraw - candidatetime2
#        print

#        if abs(normalraw - candidatetime3) < abs(normalraw - candidatetime2):
#            if abs(normalraw - candidatetime1) < abs(normalraw - candidatetime3):
#                return candidatetime1
#            else:
#                return candidatetime3
#        else:
#            if abs(normalraw - candidatetime1) < abs(normalraw - candidatetime2):
#                return candidatetime1
#            else:
#                return candidatetime2
        return normalraw; 
               
       
    # For Deliverable
    def get_value(self):
        return self.get_raw_value() / 1000.0

    def get_time(self):
        return self.get_raw_time() / 1000.0

    def __str__(self):
        return ("%.03f" % self.get_value())    


class HeartbeatPacket(Packet, Driver.Deliverable):
    ADDR_OFFSET = 10
    ADDR_MASK = 0xFF

    NODE_TYPE_OFFSET = 0
    NODE_TYPE_MASK = 0x3FF

    LAST_SCANDAL_ERROR_BYTE = 0
    LAST_USER_ERROR_BYTE = 1
    SC_VERSION_BYTE = 2
    NUM_ERRORS_BYTE = 3

    def __init__(self, pkt=None, addr=0, nodetype=0, last_scandal_err=0, \
                     last_user_err=0, scandal_vers=0, num_errs=0, raw_time=None):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.HEARTBEAT_TYPE << Packet.TYPE_OFFSET |\
            (addr & HeartbeatPacket.ADDR_MASK) << \
                                 HeartbeatPacket.ADDR_OFFSET |\
            (nodetype & HeartbeatPacket.NODE_TYPE_MASK) << \
                                 HeartbeatPacket.NODE_TYPE_OFFSET

        data = [last_scandal_err, last_user_err, scandal_vers, num_errs] + \
            int_to_bytes(raw_time, 4)

        Packet.__init__(self, id, data)


    def get_addr(self):
        return (self.id >> HeartbeatPacket.ADDR_OFFSET) &\
            HeartbeatPacket.ADDR_MASK

    def get_node_type(self):
        return (self.id >> HeartbeatPacket.NODE_TYPE_OFFSET) &\
            HeartbeatPacket.NODE_TYPE_MASK
                
    def get_last_scandal_error(self):
        return self.data[HeartbeatPacket.LAST_SCANDAL_ERROR_BYTE]

    def get_last_user_error(self):
        return self.data[HeartbeatPacket.LAST_USER_ERROR_BYTE]

    def get_scandal_version(self):
        return self.data[HeartbeatPacket.LAST_SC_VERSION_BYTE]

    def get_num_errors(self):
        return self.data[HeartbeatPacket.LAST_NUM_ERRORS_BYTE]

    def get_raw_time(self):
        return bytes_to_int(self.data[4:8])
    
    # To satisfy the deliverable
    def get_value(self):
        return self.get_time()
    def get_time(self):
        return self.get_raw_time() / 1000.0
    def __str__(self):
        return "%d" % self.get_node_type()


class ResetPacket(Packet, Driver.Deliverable):
    ADDR_OFFSET=10
    ADDR_MASK = 0xFF

    def __init__(self, pkt=None, addr=0, rawtime=None):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.RESET_TYPE << Packet.TYPE_OFFSET |\
            (addr & ResetPacket.ADDR_MASK) << \
                                 ChannelPacket.ADDR_OFFSET
 
        if rawtime is None:
            raw_time = int(int((time.time() * 1000.0)) & 0xFFFFFFFF)

        data = int_to_bytes(0, 4) + \
            int_to_bytes(raw_time, 4)

        Packet.__init__(self, id, data)

    def get_addr(self):
        return (self.id >> self.ADDR_OFFSET) & self.ADDR_MASK

    def get_raw_time(self):
        return bytes_to_int(self.data[4:8])
    
    # For Deliverable
    def get_value(self):
        return self.get_addr()

    def get_time(self):
        return self.get_raw_time() / 1000.0

class CommandPacket(Packet):
    DEST_OFFSET = 10
    DEST_MASK = 0xFF

    COMMAND_OFFSET = 0
    COMMAND_MASK = 0x3FF

    def __init__(self, pkt=None, destaddr=0, commandnum=0, value=None, value2=None):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.COMMAND_TYPE << Packet.TYPE_OFFSET |\
            (destaddr & CommandPacket.DEST_MASK) << \
                                 CommandPacket.DEST_OFFSET |\
            (commandnum & CommandPacket.COMMAND_MASK) << \
                                 CommandPacket.COMMAND_OFFSET

        if value is not None:
            data = int_to_bytes(value, 4)
        else:
            data = [0,0,0,0]

        if value2 is not None:
            data += int_to_bytes(value2, 4)
        else:
            data += [0,0,0,0]

        Packet.__init__(self, id, data)

    def get_dest(self):
        return (self.id >> CommandPacket.DEST_OFFSET) &\
            CommandPacket.DEST_MASK

    def get_command(self):
        return (self.id >> CommandPacket.COMMAND_OFFSET) &\
            CommandPacket.COMMAND_MASK

class ConfigPacket(Packet):
    DEST_OFFSET = 10
    DEST_MASK = 0xFF

    CONFIG_NUM_OFFSET = 0
    CONFIG_NUM_MASK = 0x3FF

    (   CONFIG_ADDR,
        CONFIG_IN_CHAN_SOURCE,
        CONFIG_OUT_CHAN_M,
        CONFIG_OUT_CHAN_B,
        NUM_TYPES ) = range(5)

    def __init__(self, pkt=None, destaddr=0, confignum=0, value=0, value2=None):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.CONFIG_TYPE << Packet.TYPE_OFFSET |\
            (destaddr & ConfigPacket.DEST_MASK) << \
                                        ConfigPacket.DEST_OFFSET |\
            (confignum & ConfigPacket.CONFIG_NUM_MASK) << \
                                        ConfigPacket.CONFIG_NUM_OFFSET;

        data = int_to_bytes(value, 4)
        if value2 is not None:
            data += int_to_bytes(value2, 4)
        else:
            data += [0,0,0,0]

        print "Warning: config packets are not yet implemented in a generic way"
        
        Packet.__init__(self, id, data)

    def get_dest(self):
        return (self >> self.DEST_OFFSET) & self.DEST_MASK

    def get_config_num(self):
        return (self >> self.CONFIG_NUM_OFFSET) & self.CONFIG_NUM_MASK

    def get_param1(self):
        return Packet.bytes_to_int(self.data[0:4])

    def get_param2(self):
        return Packet.bytes_to_int(self.data[4:8])

class AddrConfigPacket(ConfigPacket):
    def __init__(self, destaddr=0, newaddr=0):
        ConfigPacket.__init__(self, destaddr=destaddr, 
                                confignum=ConfigPacket.CONFIG_ADDR, 
                                value=(newaddr << 24))

class InChanSourceConfigPacket(ConfigPacket):
    def __init__(self, destaddr=0, inchan=0, node=0, num=0):
        value1 =    ((inchan >> 8) & 0xFF) << 24 |\
                    ((inchan >> 0) & 0xFF) << 16 |\
                    (node & 0xFF) << 8 | \
                    ((num & 0xFF) >> 8) << 0;\
                    
        value2 =    ((num & 0xFF) << 24);
        
        ConfigPacket.__init__(self, destaddr=destaddr,  confignum=ConfigPacket.CONFIG_IN_CHAN_SOURCE, value=value1, value2=value2)

class OutChanMConfigPacket(ConfigPacket):
    def __init__(self, destaddr=0, chan=0, m=0):
        value1 =    ((chan >> 8) & 0xFF) << 24 | \
                    ((chan >> 0) & 0xFF) << 16 | \
                    ((m >> 24) & 0xFF) << 8 | \
                    ((m >> 16) & 0xFF) << 0
        value2 =    ((m >> 8) & 0xFF) << 24 | \
                    ((m >> 0) & 0xFF) << 16
                    
        ConfigPacket.__init__(self, destaddr=destaddr,  confignum=ConfigPacket.CONFIG_OUT_CHAN_M, value=value1, value2=value2)
                                
class OutChanBConfigPacket(ConfigPacket):
    def __init__(self, destaddr=0, chan=0, b=0):
        value1 =    ((chan >> 8) & 0xFF) << 24 | \
                    ((chan >> 0) & 0xFF) << 16 | \
                    ((b >> 24) & 0xFF) << 8 | \
                    ((b >> 16) & 0xFF) << 0
        value2 =    ((b >> 8) & 0xFF) << 24 | \
                    ((b >> 0) & 0xFF) << 16
                    
        ConfigPacket.__init__(self, destaddr=destaddr, confignum=ConfigPacket.CONFIG_OUT_CHAN_B, value=value1, value2=value2)




class UserConfigPacket(Packet):
    DEST_OFFSET = 10
    DEST_MASK = 0xFF

    CONFIG_NUM_OFFSET = 0
    CONFIG_NUM_MASK = 0x3FF

    def __init__(self, pkt=None, destaddr=0, confignum=0, value=0, value2=None):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.USER_CONFIG_TYPE << Packet.TYPE_OFFSET |\
            (destaddr & UserConfigPacket.DEST_MASK) << \
                                        UserConfigPacket.DEST_OFFSET |\
            (confignum & UserConfigPacket.CONFIG_NUM_MASK) << \
                                        UserConfigPacket.CONFIG_NUM_OFFSET;

        data = int_to_bytes(value, 4)
        if value2 is not None:
            data += int_to_bytes(value2, 4)
        else:
            data += [0,0,0,0]
        
        Packet.__init__(self, id, data)

    def get_dest(self):
        return (self >> self.DEST_OFFSET) & self.DEST_MASK

    def get_config_num(self):
        return (self >> self.CONFIG_NUM_OFFSET) & self.CONFIG_NUM_MASK

    def get_param1(self):
        return bytes_to_int(self.data[0:4])

    def get_param2(self):
        return bytes_to_int(self.data[4:8])

class UserErrorPacket(Packet):
    ADDR_OFFSET = 10
    ADDR_MASK = 0xFF

    NODE_TYPE_OFFSET = 0
    NODE_TYPE_MASK = 0x3FF

    def __init__(self, pkt=None, addr=0, nodetype=0, errornum=0, time=0):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.USER_ERROR_TYPE << Packet.TYPE_OFFSET |\
            (addr & UserErrorPacket.ADDR_MASK) << \
                                        UserErrorPacket.ADDR_OFFSET |\
            (nodetype & UserErrorPacket.NODE_TYPE_MASK) << \
                                        UserErrorPacket.NODE_TYPE_OFFSET;

        data = int_to_bytes(errornum, 1)
        data += [0,0,0]
        data += int_to_bytes(time, 4)
        
        Packet.__init__(self, id, data)

    def get_addr(self):
        return (self.id >> UserErrorPacket.ADDR_OFFSET) & \
            UserErrorPacket.ADDR_MASK

    def get_node_type(self):
        return (self.id >> UserErrorPacket.NODE_TYPE_OFFSET) & \
            UserErrorPacket.NODE_TYPE_MASK
    
    def get_errornum(self):
        return self.data[0]

    def get_raw_time(self):
        return bytes_to_int(self.data[4:8])

class ErrorPacket(Packet):
    ADDR_OFFSET = 10
    ADDR_MASK = 0xFF

    NODE_TYPE_OFFSET = 0
    NODE_TYPE_MASK = 0x3FF

    def __init__(self, pkt=None, addr=0, nodetype=0, errornum=0, time=0):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.SCANDAL_ERROR_TYPE << Packet.TYPE_OFFSET |\
            (addr & ErrorPacket.ADDR_MASK) << \
                                        ErrorPacket.ADDR_OFFSET |\
            (nodetype & ErrorPacket.NODE_TYPE_MASK) << \
                                        ErrorPacket.NODE_TYPE_OFFSET;

        data = int_to_bytes(errornum, 1)
        data += [0,0,0]
        data += int_to_bytes(time, 4)
        
        Packet.__init__(self, id, data)

    def get_addr(self):
        return (self.id >> ErrorPacket.ADDR_OFFSET) & \
            ErrorPacket.ADDR_MASK

    def get_node_type(self):
        return (self.id >> ErrorPacket.NODE_TYPE_OFFSET) & \
            ErrorPacket.NODE_TYPE_MASK
    
    def get_errornum(self):
        return bytes_to_int(self.data[0:0])

    def get_raw_time(self):
        return bytes_to_int(self.data[4:8])

class TimesyncPacket(Packet):
    def __init__(self, pkt=None, newtime=0):
        if pkt is not None:
            Packet.__init__(self, pkt.id, pkt.data)
            return

        id = Packet.TIMESYNC_TYPE << Packet.TYPE_OFFSET

        data = int_to_bytes(int(newtime * 1000.0), 8)
        
        Packet.__init__(self, id, data)

    def get_new_time(self):
        return bytes_to_int(self.data[0:8]) / 1000.0

    def get_time(self):
        return bytes_to_int(self.data[0:8]) / 1000.0
