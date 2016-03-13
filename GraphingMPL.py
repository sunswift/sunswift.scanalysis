# --------------------------------------------------------------------------                                 
#  Scanalysis Matplotlib Graphing Abstraction
#  File name: GraphingMPL.py
#  Author: David Snowdon
#  Description: The abstraction between scanalysis and matplotlib
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
import matplotlib

matplotlib.use('GTKCairo')  # or 'GTK' or 'GTKAgg'
from matplotlib.figure import Figure
import matplotlib.pyplot

from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.figure import Figure

import Graphing

class Graph(Graphing.Graph):
    def __init__(self, sa, legend=True, **kwargs):
        Graphing.Graph.__init__(self, sa, **kwargs)

        self.fig = Figure() #figsize=(5,4), dpi=100)
        self.canvas = FigureCanvas(self.fig)

        self.axes = {}
        self.serieslist = {}
        self.serieslines = {}
        self.annotations = {}
        self.axistags = []

        self.add_axis( axis=(1,1) )

        self.legend = legend

    def get_widget(self):
        return self.canvas
        
    def add_axis(self, **kwargs):
        Graphing.Graph.add_axis(self, **kwargs)

        axis = kwargs["axis"]

        self.axistags.append(axis)

        # Add the matplotlib axis
        rect = [0.1, 0.1, 0.8, 0.8]
        self.axes[axis] = self.fig.add_axes(rect, label=str(axis))
        if len(self.axes.keys()) > 1:
            self.axes[axis].set_frame_on(False)

        # Add the series list. 
        self.serieslist[axis] = []
        self.serieslines[axis] = []
        self.annotations[axis] = []

    def add_series(self, series, axis=(1,1), **kwargs):
        Graphing.Graph.add_series(self, series, **kwargs)

        self.serieslist[axis].append(series)

        for axisnum in range(len(self.axistags)):
            ax = self.axistags[axisnum]

            # Clear the axis of all previous plots
            self.axes[ax].cla()

            # Set the graph title on the first axis
            if axisnum == 1:
                if self.get_title() is not None:
                    self.axes[ax].set_title(self.get_title())

            # Set the first axis to have ticks only on the left
            if axisnum == 0:
                self.axes[ax].yaxis.tick_left()
                
            if axisnum == 1: 
                self.axes[ax].yaxis.tick_right()
                #self.axes[ax].yaxis.set_label_position('right')

            # These should only be for the first axis I think
            self.axes[ax].set_xlabel(self.get_xlabel(axis=ax))
            self.axes[ax].set_ylabel(self.get_ylabel(axis=ax))

            args = []
            for series in self.serieslist[ax]:
                x = series.get_xpoints()
                y = series.get_ypoints()
                formatstr = ""
        
                args.append(x)
                args.append(y)
                args.append(formatstr)

            self.serieslines[ax] = self.axes[ax].plot(*args)
#            series.manager = get_current_fig_manager()

            for i in range(len(self.serieslist[ax])):
                series = self.serieslist[ax][i]
                line = self.serieslines[ax][i]

                kwargs = series.get_format()
                kwargs["label"] = series.get_label()
                matplotlib.pyplot.setp(line, **kwargs)

            if self.legend:
                if axisnum == 0:
                    self.axes[ax].legend(loc="lower left")
                if axisnum == 1:
                    self.axes[ax].legend(loc="upper left")

            for (xy, label, offset, format) in self.annotations[axis]:
                self.axes[ax].annotate(label, xy, textcoords="offset points", xytext=offset, **format)

    def paint_refresh(self):
        if self.update_flag == True:
            Graphing.Graph.paint_refresh(self)
            self.update_flag = False

            newxmin = None
            newxmax = None

            for ax in self.axes.keys():
                newymin = None
                newymax = None

                for i in range(len(self.serieslist[ax])):
                    series = self.serieslist[ax][i]
                    line = self.serieslines[ax][i]

                    x = series.get_xpoints()
                    y = series.get_ypoints()
                
                    if len(x) > 0:
                        if newxmin is None:
                            newxmin = min(x)
                        if newxmax is None:
                            newxmax = max(x)
                        newxmax = max(max(x), newxmax)
                        newxmin = min(min(x), newxmin)

                    if len(y) > 0:
                        if newymin is None:
                            newymin = min(y)
                        if newymax is None:
                            newymax = max(y)
                        
                        newymin = min(min(y), newymin)
                        newymax = max(max(y), newymax)

                    line.set_data(x,y)
                    line.set_ydata(y)
                    
                if newymin is not None:
                    margin = (newymax - newymin) * 0.02
                    self.axes[ax].set_ylim(newymin - margin, newymax + margin)
                
            for ax in self.axes.keys():
                if newxmin is not None:
                    margin = (newxmax - newxmin) * 0.02
                    self.axes[ax].set_xlim(newxmin - margin, newxmax + margin)
                
        
            self.canvas.draw()

        return False

    def add_annotation(self, xpoints, ypoints, labels, xoffset=0, yoffset=0, format={}, axis=(1,1)):
        for i in range(len(xpoints)):
            self.annotations[axis].append( ((xpoints[i], ypoints[i]), labels[i], (xoffset,yoffset), format) )

