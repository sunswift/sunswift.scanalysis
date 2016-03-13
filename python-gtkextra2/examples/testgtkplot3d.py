#!/usr/bin/env python

import gtk
import gtkextra
from math import cos

class Application(gtk.Window):
    def __del__(self):
        print 'Application.__del__'

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title=("GtkPlot3D Demo")
        self.set_size_request(550, 650)

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        self.add(scrollwin)

        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot3D(width=0.7, height=0.7)
        plot.axis_set_minor_ticks(gtkextra.PLOT_AXIS_X, 1)
        plot.axis_set_minor_ticks(gtkextra.PLOT_AXIS_Y, 1)
        plot.axis_show_ticks(gtkextra.PLOT_SIDE_XY, gtkextra.PLOT_TICKS_OUT, gtkextra.PLOT_TICKS_OUT)
        plot.axis_show_ticks(gtkextra.PLOT_SIDE_XZ, gtkextra.PLOT_TICKS_OUT, gtkextra.PLOT_TICKS_OUT)
        plot.axis_show_ticks(gtkextra.PLOT_SIDE_YX, gtkextra.PLOT_TICKS_OUT, gtkextra.PLOT_TICKS_OUT)
        plot.axis_show_ticks(gtkextra.PLOT_SIDE_YZ, gtkextra.PLOT_TICKS_OUT, gtkextra.PLOT_TICKS_OUT)
        plot.axis_show_ticks(gtkextra.PLOT_SIDE_ZX, gtkextra.PLOT_TICKS_OUT, gtkextra.PLOT_TICKS_OUT)
        plot.axis_show_ticks(gtkextra.PLOT_SIDE_ZY, gtkextra.PLOT_TICKS_OUT, gtkextra.PLOT_TICKS_OUT)
        canvas.add_plot(plot, 0.10, 0.06)

        surface = gtkextra.PlotSurface(self.function)
        surface.set_xstep(0.025)
        surface.set_ystep(0.025)
        surface.set_legend("cos ((r-r\\s0\\N)\\S2\\N)")
        plot.add_data(surface)

        button = gtk.Button("Rotate X")
        button.connect("clicked", self.rotate_x, canvas, plot)
        canvas.put(button, 150, 0)
        
        button = gtk.Button("Rotate Y")
        button.connect("clicked", self.rotate_y, canvas, plot)
        canvas.put(button, 230, 0)
        
        button = gtk.Button("Rotate Z")
        button.connect("clicked", self.rotate_z, canvas, plot)
        canvas.put(button, 310, 0)
        
        self.show_all()

        try:
            canvas.export_ps_with_size("demo3d.ps")
            print "Wrote demo3d.ps"
        except:
            pass

    def function(self, x, y, *extra):
        return cos(((x - 0.5) * (x - 0.5) + (y - 0.5) * (y - 0.5)) * 24.0) \
               / 4.0 + 0.5

    def rotate_x(self, button, canvas, plot, *extra):
        plot.rotate_x(10.0)
        canvas.paint()
        canvas.refresh()
        
    def rotate_y(self, button, canvas, plot, *extra):
        plot.rotate_y(10.0)
        canvas.paint()
        canvas.refresh()
        
    def rotate_z(self, button, canvas, plot, *extra):
        plot.rotate_z(10.0)
        canvas.paint()
        canvas.refresh()
        
if __name__ == '__main__':
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
