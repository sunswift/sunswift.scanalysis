#!/usr/bin/env python

import gtk, gtkextra

class Application(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkPlotBox Demo")
        self.set_size_request(550, 360)

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrollwin)

        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot()
        plot.resize(width=0.5, height=0.25)
        plot.set_range(-1.0, 1.0, -1.0, 1.4)
        plot.legends_move(0.51, 0.05)
        plot.set_legends_border(gtkextra.PLOT_BORDER_NONE, gtkextra.PLOT_BORDER_NONE)
        plot.axis_hide_title(gtkextra.PLOT_AXIS_TOP)
        plot.axis_show_ticks(gtkextra.PLOT_AXIS_BOTTOM, 15, 3)
        plot.axis_set_ticks(gtkextra.PLOT_AXIS_X, 1.0, 1)
        plot.axis_set_ticks(gtkextra.PLOT_AXIS_Y, 1.0, 1)
        plot.x0_set_visible(gtk.TRUE);
        plot.y0_set_visible(gtk.TRUE);
        canvas.add_plot(plot, 0.15, 0.06)

        self.build_example1(plot)
        
        self.show_all()

    def build_example1(self, plot):
        px1 = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        py1 = [0.56, 0.12, 0.123, 0.5, 0.2, 0.21]
        pz1 = [0.12, 0.22, 0.27, 0.12, 0.052, 0.42]
        dz1 = [0.0243, 0.045, 0.075, 0.0213, 0.05, 0.0324]

        colormap = self.get_colormap()
        red = colormap.alloc_color("red")
        yellow = colormap.alloc_color("yellow")
        
        data = gtkextra.PlotBox(gtk.ORIENTATION_VERTICAL)
        plot.add_data(data)
        data.set_points(x=px1, y=py1, z=pz1, dz=dz1)
        data.show_zerrbars()
        data.set_symbol(gtkextra.PLOT_SYMBOL_CIRCLE, gtkextra.PLOT_SYMBOL_FILLED, 10, 2,
                        yellow, red)
        data.set_line_attributes(gtkextra.PLOT_LINE_NONE, 0, 0, 1, red)
        data.set_legend("Boxes")

if __name__ == '__main__':
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()

