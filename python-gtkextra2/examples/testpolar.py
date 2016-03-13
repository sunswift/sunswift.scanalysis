#!/usr/bin/env python

import gtk, gtkextra

class Application(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkPlotPolar Demo")
        self.set_size_request(500, 320)

        colormap = self.get_colormap()
        red = colormap.alloc_color("red")
        
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrollwin)

        canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.PlotPolar()
        plot.resize(width=0.5, height=0.25)
        canvas.add_plot(plot, 0.15, 0.06)

        r = [0.2, 0.34, 0.45, 0.6, 0.75, 0.81]
        angle = [15.0, 20.0, 43.0, 67.0, 84.0, 106.0]
    
        data = gtkextra.PlotData()
        data.set_points(x=r, y=angle)
        data.set_symbol(gtkextra.PLOT_SYMBOL_DIAMOND, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, red, red)
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, red)
        data.set_legend("Example")
        plot.add_data(data)

        self.show_all()

if __name__ == '__main__':
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
