# --------------------------------------------------------------------------                                 
#  Scanalysis GTKExtra Graphing Abstraction
#  File name: GraphingGTKExtra.py
#  Author: David Snowdon
#  Description: The abstraction between scanalysis and gtkextra
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

import Graphing
import gobject
import gtk,gtkextra

class Graph(Graphing.Graph, gtk.VBox):
    def __init__(self, sa, xlabel=None, ylabel=None, title=None, maxupdate=1, width=300, height=300):
        Graphing.Graph.__init__(self, sa, xlabel=xlabel, ylabel=ylabel, title=title, maxupdate=maxupdate)
        gtk.VBox.__init__(self)

        colormap = self.get_colormap()
        self.red = colormap.alloc_color("red")
        self.blue = colormap.alloc_color("blue")
        self.green = colormap.alloc_color("green")
        self.light_blue = colormap.alloc_color("light blue")
        self.light_yellow = colormap.alloc_color("light yellow")
        self.white = colormap.alloc_color("white")

        self.canvas = canvas = \
            gtkextra.PlotCanvas(width, height)
        canvas.set_background(self.white)
        self.pack_start(canvas)

        self.plot = plot = gtkextra.Plot()

        plot.resize(width=0.65, height=1.0)
        plot.set_background(self.light_yellow)
        plot.legends_set_attributes(None, 0, None, self.white)
        plot.set_legends_border(gtkextra.PLOT_BORDER_SHADOW, 3)
        plot.legends_move(0.05, 1.23)
        plot.hide_legends()

        plot.set_range(0.0, 3100.0, 0.0, 3100.0)
        plot.set_ticks(gtkextra.PLOT_AXIS_X, 300.0, 1)
        plot.set_ticks(gtkextra.PLOT_AXIS_Y, 200.0, 1)

        axis_left = plot.get_axis(gtkextra.PLOT_AXIS_LEFT)
        axis_right = plot.get_axis(gtkextra.PLOT_AXIS_RIGHT)
        axis_top = plot.get_axis(gtkextra.PLOT_AXIS_TOP)
        axis_bottom = plot.get_axis(gtkextra.PLOT_AXIS_BOTTOM)
        axis_x = plot.get_axis(gtkextra.PLOT_AXIS_X)
        axis_y = plot.get_axis(gtkextra.PLOT_AXIS_Y)

        axis_top.set_labels_style(gtkextra.PLOT_LABEL_FLOAT, 0)
        axis_bottom.set_labels_style(gtkextra.PLOT_LABEL_FLOAT, 0)
        
        axis_top.set_visible(False)
        axis_right.set_visible(False)
        axis_bottom.set_visible(True)
        axis_left.set_visible(False)

        axis_bottom.move_title(0, 0.5, 1.3)

        plot.grids_set_visible(False, False, False, False)
        
        axis_top.hide_title()
        axis_left.set_title(ylabel)
        axis_bottom.set_title(xlabel)

        child = gtkextra.PlotCanvasPlot(plot)
        canvas.put_child(child, .15, .15, .9, 0.8);

#        child = gtkextra.PlotCanvasText("Times-BoldItalic", 20, 0, None, None, True, gtk.JUSTIFY_CENTER, "Real Time Demo")
#        canvas.put_child(child, .45, .05, 0., 0.)

        self.connect("destroy", self.destroy_cb)
        self.data_list = []
        self.update_flag = False
        self.timeout_val = maxupdate

    def add_series(self, series):
        Graphing.Graph.add_series(self, series)

        data = self.new_data(series)

        self.data_list.append( (series, data) )
        data.set_points(series.get_xpoints(), series.get_ypoints())

        self.flag_update()

    def remove_series(self, series):
        Graphing.Graph.remove_series(self, series)
        del data_list[series]

    def set_xlabel(self, xlabel):
        Graphing.Graph.set_xlabel(self, xlabel)
        axis_bottom = self.plot.get_axis(gtkextra.PLOT_AXIS_BOTTOM)
        axis_bottom.set_title(self.xlabel)
        
    def set_ylabel(self, ylabel):
        Graphing.Graph.set_ylabel(self, ylabel)
        axis_left = self.plot.get_axis(gtkextra.PLOT_AXIS_BOTTOM)
        axis_left.set_title(self.ylabel)

    # Titles not implemented


### Below here is GTK Extra specific helper functions
        
    def new_data(self, series):
        data = gtkextra.PlotData()

        self.plot.add_data(data)

        self.plot.show()
        data.show()

        data.set_legend(series.get_display_name())
        
        # This should be based on the info in the series structure
        symbol = symbol=gtkextra.PLOT_SYMBOL_NONE
        colour = self.red
        data.set_symbol(symbol, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, \
                            colour, colour)
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, colour)

        self.plot.clip_data(True)        

        return data
        
    def paint_refresh(self):
        if self.update_flag == True:
            Graphing.Graph.paint_refresh(self)
            print "Updating canvas!"
            self.canvas.paint()
            self.canvas.refresh()
            self.canvas.show_all()
            self.update_flag = False
        return False



