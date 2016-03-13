#!/usr/bin/env python

import sys
sys.path.append(sys.path[0] + "/../../")

import math
import os
import os.path
import types
import math
import time

from optparse import OptionParser

import Scandal
import Can



# Parse some options
parser = OptionParser()
parser.add_option("-i", "--input", dest="inname",
                  help="Read data from FILE", metavar="FILE")
parser.add_option("-s", "--start", dest="start", type=float, action="store",
                  help="Start date from UNIXTIME", metavar="UNIXTIME")

(options,args) = parser.parse_args()

# We can also pass an input file via "process.py filename"
if len(args) is 1:
    options.inname = args[0]

if options.inname is None:
    infile = sys.stdin
else:
    infile = open(options.inname, "r")

linenum = 0
for line in infile:
    linenum = linenum + 1
    tokens = line.split()

    try:
        id = int(tokens[0], 16)
    
        data = []
        for i in range(0, len(tokens[1])/2):
            data.append( int(tokens[1][2*i:2*i+2], 16) )

        rectime = float(tokens[2])
    except:
        print "Malformed line: %d: \"%s\"" % (linenum, line)
        continue
    
    if rectime < options.start:
        continue
    
    pkttype = (id >> 18) & 0xFF
            
    pkt = Can.Packet(id, data, rectime)
    packet = Scandal.scandal_decode_packet(pkt)
                
    scandal_time = packet.get_time()
    if scandal_time is None: # This packet type doesn't have a local time
        continue
    
#    print "%d: Received at: "%linenum + time.ctime(rectime) + " -- " + str(rectime) + " -- " + str(scandal_time)
    
    if scandal_time < ( (1 << 32) / 1000.0 ):
        try:
            offset = pkt.get_recvd() - scandal_time
            #print str(type(packet)) + ": offset is " + str( pkt.get_recvd() - scandal_time )
        except:
            print "Error occured at line %d: \"%s\"" % (linenum, line)
            print "Type was: " + str(packet.get_type())
        
        before_possibility = scandal_time + math.floor(offset / ((1 << 32) / 1000.0)) * ((1<<32) / 1000.0)
        after_possibility = before_possibility + ((1<<32) / 1000.0)
        
        diff_before = abs(pkt.get_recvd() - before_possibility)
        diff_after = abs(pkt.get_recvd() - after_possibility)
    
 #       print "Original timestamp: " + str(packet.get_time())
        
        if diff_before < diff_after:
#            print "Rounding down"
            new_timestamp = before_possibility
        else: 
#            print "Rounding up"
            new_timestamp = after_possibility
        
        new_offset = pkt.get_recvd() - new_timestamp
        #print "New offset is: " + str( pkt.get_recvd() - new_timestamp )

        if abs(new_offset) > 60.0 * 60.0 * 8.0: 
            if isinstance(packet, Scandal.ChannelPacket) or isinstance(packet, Scandal.HeartbeatPacket):
                print "Offset was too large: %f Node is: "%new_offset + str(packet.get_addr())
            continue