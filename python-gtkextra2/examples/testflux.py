#!/usr/bin/env python

import gtk, gtkextra

class Application(gtk.Window):
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkPlotFlux Demo")
        self.set_size_request(550, 340)

        colormap = self.get_colormap()
        red = colormap.alloc_color("red")
        
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrollwin)

        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        canvas.connect("select_item", self.select_item)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot()
        plot.resize(width=0.5, height=0.25)
        plot.set_range(-1.0, 1.0, -1.0, 1.4)
        plot.legends_move(0.51, 0.05)
        plot.set_legends_border(0, 0)
        plot.axis_hide_title(gtkextra.PLOT_AXIS_TOP)
        plot.axis_show_ticks(gtkextra.PLOT_AXIS_BOTTOM, 15, 3)
        plot.axis_set_ticks(gtkextra.PLOT_AXIS_X, 1.0, 1)
        plot.axis_set_ticks(gtkextra.PLOT_AXIS_Y, 1.0, 1)
        plot.axis_set_visible(gtkextra.PLOT_AXIS_TOP, gtk.TRUE)
        plot.axis_set_visible(gtkextra.PLOT_AXIS_RIGHT, gtk.TRUE)
        plot.x0_set_visible(gtk.TRUE)
        plot.y0_set_visible(gtk.TRUE)
        canvas.add_plot(plot, 0.15, 0.06)

        px1 = [0., 0.2, 0.4, 0.6, 0.8, 1.0]
        py1 = [.2, .4, .5, .35, .30, .40]
        px2 = [.12, .22, .27, .12, .052, .42]
        py2 = [.0, .05, .12, .22, .16, .1]

        data = gtkextra.PlotFlux()
        data.set_points(x=px1, y=py1, dx=px2, dy=py2)
        data.set_symbol(gtkextra.PLOT_SYMBOL_CIRCLE, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, red, red)
        data.set_line_attributes(gtkextra.PLOT_LINE_NONE, 0, 0, 1, red)
        data.set_legend("Flux")
        plot.add_data(data)

        self.show_all()

    def select_item(self, canvas, event, item, *args):
        if item.type == gtkextra.PLOT_CANVAS_DATA:
            tuple = canvas.get_active_point()
            if tuple:
                print "Active point:", tuple[0], "->", tuple[1], tuple[2]
        return gtk.TRUE

if __name__ == '__main__':
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
