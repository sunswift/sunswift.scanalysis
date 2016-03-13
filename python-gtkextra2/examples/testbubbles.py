#!/usr/bin/env python

import gtk
import gtkextra

class Application(gtk.Window):
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Bubbles Demo")
        self.set_size_request(550, 650)
        self.connect("destroy", lambda win : gtk.main_quit())

        colormap = self.get_colormap()
        blue = colormap.alloc_color("blue")
        
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrollwin)

        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot(width=0.5, height=0.25)
        plot.legends_move(0.05, 0.05)
        plot.set_legends_border(0, 0)
        plot.axis_hide_title(gtkextra.PLOT_AXIS_TOP)
        plot.axis_show_ticks(gtkextra.PLOT_AXIS_BOTTOM, 15, 3)
        plot.axis_set_visible(gtkextra.PLOT_AXIS_TOP, gtk.TRUE)
        plot.axis_set_visible(gtkextra.PLOT_AXIS_RIGHT, gtk.TRUE)
        plot.grids_set_visible(gtk.TRUE, gtk.TRUE, gtk.TRUE, gtk.TRUE)
        canvas.add_plot(plot, 0.15, 0.06)

        px1 = [0., 0.1, 0.2, 0.3, 0.4, 0.5, .6, .7, .8, .9]
        py1 = [.2, .4, .5, .35, .30, .40, .45, .56, .76, .87]
        pa1 = [.12, .22, .27, .12, .052, .12, .045, .214, .123, .088]
        pda1 = [.132, .23, .432, .34, .46, .56, .785, .76, .86, .89]

        data = gtkextra.PlotData()
        data.set_points(x=px1, y=py1, a=pa1, da=pda1)
        data.set_symbol(gtkextra.PLOT_SYMBOL_CIRCLE, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, blue, blue)
        data.set_line_attributes(gtkextra.PLOT_LINE_NONE, 0, 0, 1, blue)
        data.set_legend("Bubbles")
        data.gradient_set_visible(gtk.TRUE)
        plot.add_data(data)

        self.show_all()

if __name__ == '__main__':		
    app = Application()
    gtk.main()
