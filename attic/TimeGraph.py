import gobject
import gtk,gtkextra
import math
import bisect

from Misc import *

class TimeGraph (gtk.VBox):
    def __init__(self, ylabel="", width=300, height=300, \
                     duration=300, xtick=60.0, ytick=1.0):
        gtk.VBox.__init__(self)
        self.ylabel = ylabel
        self.duration = duration
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
        axis_bottom.set_title("Time (s)")

        child = gtkextra.PlotCanvasPlot(plot)
        canvas.put_child(child, .15, .15, .9, 0.8);

#        child = gtkextra.PlotCanvasText("Times-BoldItalic", 20, 0, None, None, True, gtk.JUSTIFY_CENTER, "Real Time Demo")
#        canvas.put_child(child, .45, .05, 0., 0.)

        self.update_flag = False
#        gobject.idle_add(self.paint_refresh)

        self.data_list = []
        self.connect("destroy", self.destroy_cb)

    def destroy_cb(self, widg):
        self.update_flag = False
        for data in self.data_list:
            data.stop()

    def add(self, data):
        self.plot.add_data(data)
        data.show()
        # So that we can delete these later
        self.data_list.append(data)

    def flag_update(self):
        # Refresh the graph in our idle time
        if self.update_flag == False:
            self.update_flag = True
            gobject.timeout_add(100, self.paint_refresh)

    def paint_refresh(self):
        if self.update_flag == True:
            self.canvas.paint()
            self.canvas.refresh()
            self.update_flag = False
        return False


class TimeData(gtkextra.PlotData):
    def __init__(self, graph, store, nodename, channame, colour, label="", \
                 symbol=gtkextra.PLOT_SYMBOL_NONE, del_nonvis=True, \
                     maxpoints=50000):
        gtkextra.PlotData.__init__(self)

        self.store = store

        self.graph = graph
        graph.add(self)
        
        graph.plot.show()
        self.show()
        self.set_legend(label)
        self.set_symbol(symbol, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, colour, colour)
        self.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, colour)
        
        self.del_nonvis=del_nonvis
        self.maxpoints = maxpoints

        graph.plot.clip_data(True)

        graph.canvas.paint()
        graph.canvas.refresh()

        self.store.register_for_channel(nodename, channame, self.deliver)
        
        self.updating = False

    def stop(self):
        self.store.unregister_for_all_deliveries(self.deliver)

    def deliver(self, pkt):

        def nearest_int_multiple(value, divider):
            division = value / divider
            return divider * round(division)

        pktval = pkt.get_value()
        pkttime = pkt.get_time()

        px = self.x
        py = self.y
        if px is None: 
            px = [pktval]
            py = [pkttime]
            self.graph.plot.set_yrange(nearest_int_multiple(pktval - self.graph.ytick, self.graph.ytick),\
                                 nearest_int_multiple(pktval + self.graph.ytick, self.graph.ytick))
            self.graph.plot.set_xrange(nearest_int_multiple(pkttime - self.graph.duration, self.graph.xtick),\
                                 nearest_int_multiple(pkttime + self.graph.xtick, self.graph.xtick))
            
        n = self.get_numpoints()

        i = bisect.bisect(px, pkttime)
        px.insert(i, pkttime)
        py.insert(i, pktval)

        (xmin, xmax) = self.graph.plot.get_xrange()
        if pkttime > xmax:
            xmin = nearest_int_multiple(pkttime + self.graph.xtick - self.graph.duration, self.graph.xtick)
            xmax = nearest_int_multiple(pkttime + self.graph.xtick, self.graph.xtick)
            if xmin < 0.0:
                xmin = 0.0
#            print "Setting xrange for %s to (%f, %f)" % (self.label, xmin, xmax)
            self.graph.plot.set_xrange(xmin, xmax)
            
            # Time graph -- remove all points which are outside our scope on Y axis

        (ymin, ymax) = self.graph.plot.get_yrange()
        if pktval > ymax:
            ymax = nearest_int_multiple(pktval + self.graph.ytick, self.graph.ytick)
            self.graph.plot.set_yrange(ymin, ymax)
#            print "Setting yrange for %s to (%f, %f)" % (self.label, ymin, ymax)
        if pktval < ymin:
            ymin = nearest_int_multiple(pktval - self.graph.ytick, self.graph.ytick)
            self.graph.plot.set_yrange(ymin, ymax)
#            print "Setting yrange for %s to (%f, %f)" % (self.label, ymin, ymax)

        if self.del_nonvis:
            if len(px) > 0:
                if px[0] < xmin:
                    i = bisect.bisect(px, xmin)
                    px = px[i:]
                    py = py[i:]

            if len(px) > 0:
                if px[-1] > xmax:
                    i = bisect.bisect(px, xmax)
                    px = px[:i]
                    px = py[:i]

        if len(px) > self.maxpoints:
            px = px[-self.maxpoints:]
            py = py[-self.maxpoints:]

        self.set_points(x=px, y=py)
#        print "CountB x=%d y=%d" % (len(self.x), len(self.y))

        self.graph.flag_update()


    def set_units(self, units_string):
        self.units_string = units_string
