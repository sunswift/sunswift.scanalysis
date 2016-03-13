#!/usr/bin/env python

import sys
import math
import os
import os.path
import types
import math

from optparse import OptionParser

# If two samples are this many seconds apart, they are considered to have happened at the same time
AS_GOOD_AS = 0.001

# How many seconds to average over for the averages file.
average_length = 5.0

# Parse some options
parser = OptionParser()
parser.add_option("-i", "--input", dest="inname",
                  help="Read data from FILE", metavar="FILE")

(options,args) = parser.parse_args()

# We can also pass an input file via "process.py filename"
if len(args) is 1:
    options.inname = args[0]

if options.inname is None:
    infile = sys.stdin
else:
    infile = open(options.inname, "r")

indata = {}
num=0
for line in infile:
    num=num+1

    line = line.strip("\n")

    # The first line is the labels
    if num == 1:
        fieldnames = line.split()
        print fieldnames
    else:
        words = line.split("\t")
    
        if len(words) != len(fieldnames):
            print "Malformed line %d - fieldnames: %s words:%s" % (num, len(fieldnames), len(words))
            sys.exit()
        
        data = dict(zip(fieldnames, words))

        key = (data["Node"], data["Channel"])

        if key not in indata.keys():
            indata[key] = []

        del data["Node"]
        del data["Channel"]
            
        indata[key].append(dict(zip(data.keys(), map(float,data.values())))); 

infile.close()    

def compare_by (fieldname):
   def compare_two_dicts (a, b):
        return cmp(a[fieldname], b[fieldname])
   return compare_two_dicts


print "Adding data offsets"
#Re-align: node number, time offset 
#realign = [(30,612000.0)]
realign = []

#Scaling: node name, channel, scaling factor
#scaling = [("Motor Controller","Speed",1.015)]
scaling = []

#Ignore: list of nodes to drop
ignore = ["MPPTNG1"]
#ignore = []

for (node, channel, fac) in scaling:
    newdata = []
    for data in indata[(node,channel)]:
        data["Value"] = data["Value"] * fac
        newdata.append(data)
    indata[(node,channel)] = newdata

for (node,channel) in indata.keys():
    if node in ignore:
        del indata[(node,channel)]
    for (align_node,offset) in realign:
        if align_node == node:
            newdata = []
            for data in indata[(node,channel)]:
                data["Time"] = data["Time"] + offset
                newdata.append(data)
            del indata[(node,channel)]
            indata[(node,channel)] = newdata


print "Sorting"
for channel in indata.keys():
    temp = indata[channel]
    temp.sort(compare_by("Time"))
    indata[channel].sort(compare_by("Time"))

# Try re-sampling it and generating a single CSV file. 
resample_table = {}
resample_data = {}
not_done = 1

last_stamp = -1
last_stamp_node = 0
last_stamp_channel = 0

for (node,channel) in indata.keys():
    resample_data[(node,channel)] = []
    if last_stamp < indata[(node,channel)][0]["Time"]:
        last_stamp = indata[(node,channel)][0]["Time"]
        last_stamp_node = node
        last_stamp_channel = channel
        
print "First channel to be sampled was (%s,%s)" % (last_stamp_node, last_stamp_channel)

for (node,channel) in indata.keys():
    data = indata[(node,channel)]
    while data[0]["Time"] <= last_stamp:
        resample_table[(node,channel)] = (data[0]["Value"], data[0]["Time"])
        del data[0]
    indata[(node,channel)] = data
 
while not_done:
    # Find the next point
    next_stamp = indata[indata.keys()[0]][0]["Time"]
    for key in indata.keys():
        if next_stamp > indata[key][0]["Time"]:
            next_stamp = indata[key][0]["Time"]
            next_key = key
    
    # Add interpolated data for each channel
    for key in indata.keys():
        (y1,x1) = resample_table[key]
        y2 = indata[key][0]["Value"]
        x2 = indata[key][0]["Time"]
        xs = next_stamp
        
        # If the time stamps are less than "AS_GOOD_AS" seconds apart, then 
        # consider them equal
        if abs(x2 - x1) >= AS_GOOD_AS:
            ys = (y2 - y1) * ( (xs - x1) / (x2 - x1) ) + y1
        else:
            ys = y2
                        
        resample_data[key].append((ys,xs))
        
        if abs(x2 - next_stamp) < AS_GOOD_AS:
            resample_table[key] = (y2,x2)
            del indata[key][0]
            
        # If we've run out of data here, we finish up
        if indata[key] == []:
            not_done = 0
            
#print "Writing big CSV"
#out = open("interpolated.csv", "w+")
#channels = resample_data.keys()
#out.write("Time")
#for (node,channel) in channels:
#    out.write(",%d_%d" % (node, channel))
#out.write("\n")
#
#for i in range(0,len(resample_data[channels[0]])):
#    (_,time) = resample_data[channels[0]][i]
#    out.write(str(time))
#    
#    for channel in channels:
#        (value,_) = resample_data[channel][i]
#        out.write(",%f" % value)
#    out.write("\n")
#
#out.close()



print("Writing averages")

channels = resample_data.keys()
channels.sort()

out = open("averages_%fs.csv" % average_length, "w+")
out.write("Time")
for (node,channel) in channels:
    out.write(",%s_%s" % (node, channel))
out.write("\n")

(_,start_period) = resample_data[channels[0]][0]
start_index = 0

for i in range(0,len(resample_data[channels[0]])):
    (_,time) = resample_data[channels[0]][i]
    
    if time >= start_period + average_length:
        mysum = 0.0
        for j in range(start_index, i):
            (_,time) = resample_data[channels[0]][j]
            mysum = mysum + time
        avg = mysum / float(i - start_index)
        out.write("%f" % avg)
            
        for channel in channels:
            mysum = 0.0
            for j in range(start_index, i):
                (value,_) = resample_data[channel][j]
                mysum = mysum + value
            out.write(",%f" % (mysum/ float(i - start_index)))

        out.write("\n")
            
        start_index = i
        (_,start_period) = resample_data[channels[0]][start_index]
out.close()
