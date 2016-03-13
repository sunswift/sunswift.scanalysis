#!/usr/bin/env python
import sys

import gtk
import gtkextra
from random import randint

class Application(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkPlot Real Time Demo")
        self.set_size_request(550, 600)
        
        colormap = self.get_colormap()
        red = colormap.alloc_color("red")
        light_blue = colormap.alloc_color("light blue")
        light_yellow = colormap.alloc_color("light yellow")
        white = colormap.alloc_color("white")

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrollwin)

        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.set_background(light_blue)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot(width=0.65, height=0.45)
        plot.set_background(light_yellow)
        plot.legends_set_attributes(None, 0, None, white)
        plot.set_range(0.0, 20.0, 0.0, 1.0)
        plot.axis_set_ticks(gtkextra.PLOT_AXIS_X, 2.0, 1)
        plot.axis_set_ticks(gtkextra.PLOT_AXIS_Y, 0.1, 1)
        plot.axis_set_labels_style(gtkextra.PLOT_AXIS_TOP, gtkextra.PLOT_LABEL_FLOAT, 0)
        plot.axis_set_labels_style(gtkextra.PLOT_AXIS_BOTTOM, gtkextra.PLOT_LABEL_FLOAT, 0)
        plot.axis_set_visible(gtkextra.PLOT_AXIS_TOP, gtk.TRUE)
        plot.axis_set_visible(gtkextra.PLOT_AXIS_RIGHT, gtk.TRUE)
        plot.grids_set_visible(gtk.TRUE, gtk.TRUE, gtk.TRUE, gtk.TRUE)
        plot.axis_hide_title(gtkextra.PLOT_AXIS_TOP)
        plot.axis_hide_title(gtkextra.PLOT_AXIS_RIGHT)
        plot.axis_set_title(gtkextra.PLOT_AXIS_LEFT, "Intensity")
        plot.axis_set_title(gtkextra.PLOT_AXIS_BOTTOM, "Point")
        plot.set_legends_border(gtkextra.PLOT_BORDER_SHADOW, 3)
        plot.legends_move(0.60, 0.10)
        canvas.add_plot(plot, 0.15, 0.15)

        canvas.put_text(0.45, 0.05, "Times-BoldItalic", 20, 0, None, None,
                        gtk.TRUE, gtk.JUSTIFY_CENTER, "Iterator Demo")

        mask = gtkextra.PLOT_DATA_X | gtkextra.PLOT_DATA_Y | gtkextra.PLOT_DATA_LABELS
        data = gtkextra.PlotData(self.iterator, 20, mask)
        data.show_labels(gtk.TRUE)
        plot.add_data(data)
        data.set_legend("Iterator")
        data.set_symbol(gtkextra.PLOT_SYMBOL_DIAMOND, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, red, red)
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, red)
        
        self.show_all()

    def iterator(self, plot, data, iter):
        x = iter
        y = randint(0, 9) / 10.0
        label = str(x)
        return (x, y, label)

    def mainloop(self):
        mainloop()

def excepthook(type, value, traceback):
    print type, value, traceback
    sys.exit()

if __name__ == '__main__':
    sys.excepthook = excepthook
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
