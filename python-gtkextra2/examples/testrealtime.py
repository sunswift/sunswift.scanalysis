#!/usr/bin/env python

import gobject
import gtk, gtkextra
from random import randint

class Application(gtk.Window):

    def __init__(self):
        #gtk.Window.__init__(self)
        self.__gobject_init__()
        self.set_title("GtkPlot Real Time Demo")
        self.set_size_request(550, 600)
        self.connect("destroy", self.quit)

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
        canvas.connect("button_press_event", self.button_press_handler)
        scrollwin.add_with_viewport(canvas)

        plot = gtkextra.Plot()
        plot.resize(width=0.65, height=0.45)
        plot.set_background(light_yellow)
        plot.legends_set_attributes(None, 0, None, white)
        plot.set_legends_border(gtkextra.PLOT_BORDER_SHADOW, 3)
        plot.legends_move(0.60, 0.10)

        plot.set_range(0.0, 20.0, 0.0, 1.0)
        plot.set_ticks(gtkextra.PLOT_AXIS_X, 2, 1)
        plot.set_ticks(gtkextra.PLOT_AXIS_Y, .1, 1)

        axis_left = plot.get_axis(gtkextra.PLOT_AXIS_LEFT)
        axis_right = plot.get_axis(gtkextra.PLOT_AXIS_RIGHT)
        axis_top = plot.get_axis(gtkextra.PLOT_AXIS_TOP)
        axis_bottom = plot.get_axis(gtkextra.PLOT_AXIS_BOTTOM)
        axis_x = plot.get_axis(gtkextra.PLOT_AXIS_X)
        axis_y = plot.get_axis(gtkextra.PLOT_AXIS_Y)

        axis_top.set_labels_style(gtkextra.PLOT_LABEL_FLOAT, 0)
        axis_bottom.set_labels_style(gtkextra.PLOT_LABEL_FLOAT, 0)
        
        axis_top.set_visible(True)
        axis_right.set_visible(True)
        plot.grids_set_visible(True, True, True, True)
        
        axis_top.hide_title()
        axis_right.hide_title()
        axis_left.set_title("Intensity")
        axis_bottom.set_title("Time (s)")

        child = gtkextra.PlotCanvasPlot(plot)
        canvas.put_child(child, .15, .15, .80, .65);
        plot.show()

        child = gtkextra.PlotCanvasText("Times-BoldItalic", 20, 0, None, None, True, gtk.JUSTIFY_CENTER, "Real Time Demo")
        canvas.put_child(child, .45, .05, 0., 0.)

        data = gtkextra.PlotData()
        plot.add_data(data)
        data.show()
        data.set_legend("Random pulse")
        data.set_symbol(gtkextra.PLOT_SYMBOL_DIAMOND, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, red, red)
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, red)
        
        plot.clip_data(True)

        canvas.paint()
        canvas.refresh()

        self.show_all()

        gobject.timeout_add(100, self.update, canvas, plot, data)

    def update(self, canvas, plot, data, *args):
        y = randint(0, 9) / 10.0

        px = data.x
        py = data.y
        if px is None : px = []
        if py is None : py = []
        
        n = data.get_numpoints()
        if n == 0:
            x = 1.0
        else:
            x = px[n - 1] + 1.0

        px.append(x)
        py.append(y)

        data.set_points(x=px, y=py)

        (xmin, xmax) = plot.get_xrange()
        if x > xmax:
            plot.set_xrange(xmin + 5.0, xmax + 5.0)

        canvas.paint()
        canvas.refresh()

        return True
        
    def button_press_handler(self, canvas, event, *extra):
        (x, y) = canvas.get_pointer()
        position = canvas.get_position(x, y)
        print "Canvas position:", position[0], position[1] 

    def quit(self, *args):
        gtk.main_quit()

if __name__ == '__main__':
    app = Application()
    gtk.main()
