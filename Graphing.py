# --------------------------------------------------------------------------                                 
#  Scanalysis Graphing Library
#  File name: Graphing.py
#  Author: David Snowdon
#  Description: The abstraction between scanalysis and various 
#               graphing libraries
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

import Driver
import gobject
import gtk
import bisect
import time
import numpy

class Graph:
    def __init__(self, sa, xlabel=None, ylabel=None, title="", maxupdate=1):
        self.sa = sa
        self.xlabels = {}
        self.ylabels = {}
        if xlabel is not None:
            self.xlabels[(1,1)] = xlabel
        if ylabel is not None:
            self.ylabels[(1,1)] = ylabel
        self.title = title

        self.timeout_val=maxupdate
        self.update_flag = False
        
        self.series_list = []

    def get_widget(self):
        return gtk.VBox()

    def add_axis(self, axis=(1,1), ylabel=None, xlabel=None):
        if ylabel is not None:
            self.set_ylabel(ylabel, axis=axis)
        if xlabel is not None:
            self.set_xlabel(xlabel, axis=axis)
        return

    def add_series(self, series, axis=(1,1) ):
        self.series_list.append(series)
        series.add_graph(self)

    def remove_series(self, series):
        self.series_list.remove(series)
        series.remove_graph(self)

    def set_xlabel(self, label, axis=(1,1)):
        self.xlabels[axis] = label

    def set_ylabel(self, label, axis=(1,1)):
        self.ylabels[axis] = label

    def get_xlabel(self, axis=(1,1)):
        if axis in self.xlabels:
            return self.xlabels[axis]
        else:
            return ""

    def get_ylabel(self, axis=(1,1)):
        if axis in self.ylabels:
            return self.ylabels[axis]
        else:
            return ""

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def flag_update(self):
        if self.update_flag == False:
            self.update_flag = True
            gobject.timeout_add(self.timeout_val, self.paint_refresh)

    def destroy_cb(self, widg):
        self.update_flag = False

    def paint_refresh(self):
        if self.update_flag == True:
            self.update_flag = False
        return False


class Series(Driver.Namable):
    def __init__(self, sa, label="_nolegend_", format={}, \
                     type="Scatter", maxpoints=None):
        if label == None:
            Driver.Namable.__init__(self)
        else:
            Driver.Namable.__init__(self, defaultname=label)

        self.sa = sa
        self.label = label; 
        self.type = type

        self.graph_list = []
        
        self.xpoints = []
        self.ypoints = []

        self.maxpoints = maxpoints

        self.format = format
        self.enabled = True

    def enable(self):
        self.enabled = True
    def disable(self):
        self.enabled = False

    def get_format(self):
        return self.format
    
    def get_label(self):
        return self.label

    def get_xpoints(self):
        return self.xpoints

    def get_ypoints(self):
        return self.ypoints

    def set_xpoints(self, new_xpoints):
        self.xpoints = new_xpoints
        
    def set_ypoints(self, new_ypoints):
        self.ypoints = new_ypoints

    def add_point(self, x, y):
        self.xpoints.append(x)
        self.ypoints.append(y)

        if self.maxpoints is not None:
            if len(self.xpoints) > self.maxpoints:
                self.xpoints = self.xpoints[-self.maxpoints:]
                self.ypoints = self.ypoints[-self.maxpoints:]

    def add_graph(self, graph):
        self.graph_list.append(graph)
        
    def clear(self):
        self.xpoints = []
        self.ypoints = []

class SeriesStatic(Series):
    def __init__(self, sa, xpoints, ypoints, **kwargs):
        Series.__init__(self, sa, **kwargs)
        
        self.xpoints = numpy.array(xpoints)
        self.ypoints = numpy.array(ypoints)
        

class SeriesTime(Series):
    def __init__(self, sa, nodename, channelname, maxtimediff=None, **kwargs):
        Series.__init__(self, sa, **kwargs)

        self.sa.store.register_for_channel(nodename, channelname, self.deliver)

        self.maxtimediff = maxtimediff

    def deliver(self, pkt):
        if self.enabled is False:
            return
    
        xpoints = self.get_xpoints()
        ypoints = self.get_ypoints()

        pkttime = pkt.get_time()
        pktval = pkt.get_value()

        # Optimise for the common case, where we are adding to the end 
        # of the array
        if len(xpoints) == 0:
            self.add_point( pkt.get_time(), pkt.get_value())
        elif xpoints[-1] < pkttime:
            self.add_point( pkt.get_time(), pkt.get_value())
        else:
            # Otherwise, do an ordered insertion by time. 
            i = bisect.bisect(xpoints, pkttime)
            xpoints.insert(i, pkttime)
            ypoints.insert(i, pktval)

        if self.maxtimediff is not None:
            xmin = xpoints[-1] - self.maxtimediff
            if xpoints[0] < xmin:
                i = bisect.bisect(xpoints, xmin)
                xpoints = xpoints[i:]
                ypoints = ypoints[i:]
                self.set_xpoints(xpoints)
                self.set_ypoints(ypoints)


        for graph in self.graph_list:
            graph.flag_update()


class SeriesXY(Series):
    def __init__(self, sa, xnodename, xchanname, \
                     ynodename, ychanname, \
                     maxupdate=200,\
                     **kwargs):
        Series.__init__(self, sa, **kwargs)

        self.sa.store.register_for_channel(xnodename, xchanname, self.xdeliver)
        self.sa.store.register_for_channel(ynodename, ychanname, self.ydeliver)

        self.x_data = []
        self.y_data = []

        self.updating_points = False
        self.maxupdate = maxupdate

#    def stop(self):
#        self.store.unregister_for_all_deliveries(self.xdeliver)
#        self.store.unregister_for_all_deliveries(self.ydeliver)

    def xdeliver(self, pkt):
        pktval = pkt.get_value()
        pkttime = pkt.get_time()

        n = len(self.x_data)
        if n == 0:
            self.x_data.append( (pktval, pkttime) )
        else:
            i = n
            while i > 0:
                (val, t) = self.x_data[i-1]
                if t == pktval:
                    break
                if t < pkttime:
                    self.x_data.insert(i, (pktval, pkttime) )
                    break
                i = i - 1

        self.flag_update_points()

    def ydeliver(self, pkt):
        pktval = pkt.get_value()
        pkttime = pkt.get_time()

        n = len(self.y_data)
        if n == 0:
            self.y_data.append( (pktval, pkttime) )
        else:
            i = n
            while i > 0:
                (val, t) = self.y_data[i-1]
                if t == pkttime:
                    break
                if t < pkttime:
                    self.y_data.insert(i, (pktval, pkttime) )
                    break
                i = i - 1

        self.flag_update_points()

    def flag_update_points(self):
        if self.updating_points == False:
            self.updating_points = True
            gobject.timeout_add(self.maxupdate, self.update_points)


    def update_points(self):
        self.updating_points = False
        start = time.time()

        px = []
        py = []
        pt = []

        x_i = 0
        y_i = 0

        x_n = len(self.x_data)
        y_n = len(self.y_data)

        xmax = xmin = ymax = ymin = None

        while (x_i < x_n) and (y_i < y_n):
            (x1_v, x1_t) = self.x_data[x_i]
            (y1_v, y1_t) = self.y_data[y_i]

            if xmax is None:
                xmax = x1_v
                xmin = x1_v
                ymax = y1_v
                ymin = y1_v
            else:
                xmax = max(xmax, x1_v)
                ymax = max(ymax, y1_v)
                xmin = min(xmin, x1_v)
                ymin = min(ymin, y1_v)


            def linear_interp(y1, x1, y2, x2, xt):
                if x1 == x2:
                    return (y1 + y2) / 2.0
                frac = (xt - x1) / (x2 - x1)
                return frac * (y2 - y1) + y1

            if x1_t == y1_t:
                px.append(x1_v)
                py.append(y1_v)
                pt.append(x1_t)
                
                next_x = None
                next_y = None

                if x_i+1 < x_n:
                    next_x = self.x_data[x_i+1]
                    
                if y_i+1 < y_n:
                    next_y = self.y_data[y_i+1]

                # If we don't have any more values left, 
                # get out of the loop
                if (next_x == None) and (next_y == None):
                    break
                
                # If we've got one value left, use it
                if next_x == None:
                    y_i = y_i + 1
                    continue

                if next_y == None:
                    x_i = x_i + 1
                    continue

                # If we've got both, increment the one
                # which has the nearest time
                (_, x2_t) = next_x
                (_, y2_t) = next_y
                if x2_t < y2_t:
                    x_i = x_i + 1
                else:
                    y_i = y_i + 1
                continue

            # If there is another x value left...
            if x_i+1 < x_n:
                (x2_v, x2_t) = self.x_data[x_i + 1]
                if (x1_t < y1_t) and (x2_t > y1_t):
                    val = linear_interp(x1_v, x1_t, x2_v, x2_t, y1_t)

                    px.append(val)
                    py.append(y1_v)
                    pt.append(y1_t)
            
                    x_i = x_i + 1
                    continue

            # If there is another y value left...
            if y_i+1 < len(self.y_data):
                (y2_v, y2_t) = self.y_data[y_i + 1]
                if (y1_t < x1_t) and (y2_t > y1_t):
                    val = linear_interp(y1_v, y1_t, y2_v, y2_t, x1_t)
                    px.append(x1_v)
                    py.append(val)
                    pt.append(x1_t)

                    y_i = y_i + 1
                    continue

            # No overlap... Move on to the next value
            if y1_t < x1_t:
                y_i = y_i + 1
            else:
                x_i = x_i + 1
            continue

        if self.maxpoints is not None:
            # If we're over-length, cull some data
            if len(pt) > self.maxpoints:
                cutoff = pt[-self.maxpoints]
                for i in range(1, len(self.x_data)):
                    (v,t) = self.x_data[i]
                    if t < cutoff:
                        continue
                    self.x_data = self.x_data[i:]
                    break

                for i in range(1, len(self.y_data)):
                    (v,t) = self.y_data[i]
                    if t < cutoff:
                        continue
                    self.y_data = self.y_data[i:]
                    break


        self.pt = pt
        self.set_xpoints(px)
        self.set_ypoints(py)

        self.xmax = xmax
        self.ymax = ymax
        self.xmin = xmin
        self.ymin = ymin

        finish = time.time()

#        print "XYGraph: Number of items (x,y): (%d,%d)" % (len(px), len(py))
#        print "XYGraph: Time for update: %f" % (finish - start)

        for graph in self.graph_list:
            graph.flag_update()

    def clear_data(self):
        self.x_data = []
        self.y_data = []
        self.update_points()
