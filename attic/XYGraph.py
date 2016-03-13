import gobject
import gtk,gtkextra
import math

from Misc import *

class Graph (gtk.VBox):
    def __init__(self, xlabel="", ylabel="", width=300, height=300, \
                     xtick=60.0, ytick=1.0, maxupdate=100):
        gtk.VBox.__init__(self)
        self.ylabel = ylabel
        self.xlabel = xlabel
        self.xtick=xtick
        self.ytick=ytick
        
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

        plot.set_range(0.0, 100.0, 0.0, 10.0)
        plot.set_ticks(gtkextra.PLOT_AXIS_X, self.xtick, 3)
        plot.set_ticks(gtkextra.PLOT_AXIS_Y, self.ytick, 3)


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
        axis_left.set_visible(True)

        axis_bottom.move_title(0, 0.5, 1.3)

        plot.grids_set_visible(False, False, True, False)
        
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

    def add(self, data):
        self.plot.add_data(data)
        data.show()
        # So we can stop them later
        self.data_list.append(data)

    def destroy_cb(self, widg):
        self.update_flag = False
        for data in self.data_list:
            data.stop()

    def flag_update(self):
        # Refresh the graph in our idle time
        if self.update_flag == False:
            self.update_flag = True
            gobject.timeout_add(self.timeout_val, self.paint_refresh)

    def paint_refresh(self):
        if self.update_flag == True:
            self.canvas.paint()
            self.canvas.refresh()
            self.update_flag = False
        return False



class XYData(gtkextra.PlotData):
    def __init__(self, graph, store, \
                     xnodename, xchanname,\
                     ynodename, ychanname,\
                     colour, label="", \
                     symbol=gtkextra.PLOT_SYMBOL_NONE,\
                     maxupdate=100):
        gtkextra.PlotData.__init__(self)

        self.store = store

        self.x_data = []
        self.y_data = []

        self.graph = graph
        graph.add(self)
        
        graph.plot.show()
        self.show()
        self.set_legend(label)
        self.set_symbol(symbol, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, colour, colour)
        self.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, colour)
        
        graph.plot.clip_data(True)

        self.store.register_for_channel(xnodename, xchanname, self.xdeliver)
        self.store.register_for_channel(ynodename, ychanname, self.ydeliver)

        graph.flag_update()
        
        self.maxupdate=maxupdate
        self.updating=False

    def stop(self):
        self.store.unregister_for_all_deliveries(self.xdeliver)
        self.store.unregister_for_all_deliveries(self.ydeliver)


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
        if self.updating == False:
            self.updating = True
            gobject.timeout_add(self.maxupdate, self.update_points)

    def update_points(self):
        self.updating = False
        start = time.time()

        px = []
        py = []
        pt = []

        x_i = 0
        y_i = 0

        x_n = len(self.x_data)
        y_n = len(self.y_data)

        def nearest_int_multiple(value, divider):
            division = value / divider
            return divider * round(division)

        if x_n > 0:
            (x1_v, _) = self.x_data[0]
            xmin = nearest_int_multiple(x1_v, self.graph.xtick)
            xmax = xmin + self.graph.xtick
        else:
            xmax = self.graph.xtick
            xmin = 0.0

        if y_n > 0:
            (y1_v, _) = self.y_data[0]
            ymin = nearest_int_multiple(y1_v, self.graph.ytick)
            ymax = ymin + self.graph.ytick
        else:
            ymax = self.graph.ytick
            ymin = 0.0

        while (x_i < x_n) and (y_i < y_n):
            (x1_v, x1_t) = self.x_data[x_i]
            (y1_v, y1_t) = self.y_data[y_i]

            xmax = max(xmax, nearest_int_multiple(x1_v + self.graph.xtick, self.graph.xtick))
            ymax = max(ymax, nearest_int_multiple(y1_v + self.graph.ytick, self.graph.ytick))
            xmin = min(xmin, nearest_int_multiple(x1_v - self.graph.xtick, self.graph.xtick))
            ymin = min(ymin, nearest_int_multiple(y1_v - self.graph.ytick, self.graph.ytick))

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

        self.pt = pt
        self.set_points(x=px, y=py)
        self.px = px
        self.py = py

        self.graph.plot.set_xrange(xmin, xmax)
        self.graph.plot.set_yrange(ymin, ymax)

        finish = time.time()

        print "XYGraph: Number of items (x,y): (%d,%d)" % (len(px), len(py))
        print "XYGraph: Time for update: %f" % (finish - start)

        self.graph.flag_update()
        
    def get_points(self):
        return (self.px,self.py)

    def set_units(self, units_string):
        self.units_string = units_string

    def clear_data(self):
        self.x_data = []
        self.y_data = []
        self.update_points()
