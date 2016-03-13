#!/usr/bin/env python

import gtk
import gtkextra
from math import cos

class Application(gtk.Window):

    def __init__(self, use_function =  1):
        gtk.Window.__init__(self)
        self.set_title("Contour Demo")
        self.set_size_request(550, 600)

        scale = 1.0
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrollwin)

        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W * scale, gtkextra.PLOT_LETTER_H * scale)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot3D(width=0.5, height=0.5)
        plot.axis_set_minor_ticks(gtkextra.PLOT_AXIS_X, 3)
        plot.axis_set_minor_ticks(gtkextra.PLOT_AXIS_Y, 3)
        plot.minor_grids_set_visible(gtk.FALSE, gtk.FALSE, gtk.FALSE)
        canvas.add_plot(plot, 0.16, 0.02)

        nx = 40
        ny = 40
        if use_function:
            surface = gtkextra.PlotCSurface(self.function)
            surface.set_xstep(1.0/nx)
            surface.set_ystep(1.0/ny)
        else:
            x=[]; y=[]; z=[]
            for ix in range(nx):
                for iy in range(ny):
                    x.append(ix/float(nx))
                    y.append(iy/float(ny))
                    z.append(self.function(x[-1], y[-1]))
            surface = gtkextra.PlotCSurface()
            surface.set_points(nx, ny, x=x, y=y, z=z)

        surface.set_legend("cos ((r-r\\s0\\N)\\S2\\N)")
        surface.set_gradient(0.2, 0.8, 6, 1)
        surface.set_lines_visible(gtk.FALSE)
        surface.set_transparent(gtk.FALSE)
        plot.add_data(surface)

        plot = gtkextra.Plot(width=0.4, height=0.4)
        plot.axis_set_minor_ticks(gtkextra.PLOT_AXIS_X, 1)
        plot.axis_set_minor_ticks(gtkextra.PLOT_AXIS_Y, 1)
        canvas.add_plot(plot, 0.26, 0.56)

        nx = 20
        ny = 20
        if use_function:
            surface = gtkextra.PlotCSurface(self.function)
            surface.set_xstep(1.0/nx)
            surface.set_ystep(1.0/ny)
        else:
            x=[]; y=[]; z=[]
            for ix in range(nx):
                for iy in range(ny):
                    x.append(ix/float(nx))
                    y.append(iy/float(ny))
                    z.append(self.function(x[-1], y[-1]))
            surface = gtkextra.PlotCSurface()
            surface.set_points(nx, ny, x=x, y=y, z=z)

        surface.set_legend("cos ((r-r\\s0\\N)\\S2\\N)")
        surface.set_gradient(0.2, 0.8, 6, 1)
        surface.set_grid_visible(gtk.FALSE)
        surface.set_transparent(gtk.FALSE)
        surface.set_projection(gtkextra.PLOT_PROJECT_FULL)
        plot.add_data(surface)

        canvas.export_ps("democsurface.ps", 0, 0, gtkextra.PLOT_LETTER)
        self.show_all()

    def function(self, x, y):
        return cos(((x - 0.5) * (x - 0.5) + (y - 0.5) * (y - 0.5)) * 24.0) \
               / 3.0 + 0.5

if __name__ == '__main__':		
    app = Application(0)
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
