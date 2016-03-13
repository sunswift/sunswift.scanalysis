#!/usr/bin/env python
import gtk
import gtkextra
from math import exp, pow, sin

class Application(gtk.Window):
    scale = 1.0
    custom_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def __init__(self):
        self.nlayers = 0
        self.buttons = []
        self.plots = []
        
        page_width = int(gtkextra.PLOT_LETTER_W * self.scale)
        page_height = int(gtkextra.PLOT_LETTER_H * self.scale)
    
        gtk.Window.__init__(self)
        self.set_title("GtkPlot Demo")
        self.set_size_request(550, 650)
        self.set_border_width(0)

        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        self.add(scrollwin)

        colormap = self.get_colormap()
        light_yellow = colormap.alloc_color("light yellow")
        light_blue = colormap.alloc_color("light blue")

        self.canvas = canvas = gtkextra.PlotCanvas(page_width, page_height)
        #canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        canvas.set_property("flags", canvas.get_property("flags") | gtkextra.PLOT_CANVAS_DND_FLAGS)
        
        scrollwin.add_with_viewport(canvas)
        canvas.set_size(page_width, page_height)

        plot = self.new_layer(canvas)
        plot.set_range(-1.0, 1.0, -1.0, 1.4)
        plot.legends_move(0.500, 0.05)
        plot.set_legends_border(gtkextra.PLOT_BORDER_NONE, gtkextra.PLOT_BORDER_NONE)

        axis_left = plot.get_axis(gtkextra.PLOT_AXIS_LEFT)
        axis_right = plot.get_axis(gtkextra.PLOT_AXIS_RIGHT)
        axis_top = plot.get_axis(gtkextra.PLOT_AXIS_TOP)
        axis_bottom = plot.get_axis(gtkextra.PLOT_AXIS_BOTTOM)
        axis_x = plot.get_axis(gtkextra.PLOT_AXIS_X)
        axis_y = plot.get_axis(gtkextra.PLOT_AXIS_Y)

        axis_top.hide_title()
        axis_bottom.show_ticks(15, 3)
        axis_x.set_ticks(1.0, 1)
        axis_y.set_ticks(1.0, 1)
        axis_top.set_visible(True)
        axis_right.set_visible(True)
        axis_x.set_visible(True)
        axis_y.set_visible(True)
        plot.x0_set_visible(True)
        plot.y0_set_visible(True)
        axis_left.set_labels_suffix("%")

        child = gtkextra.PlotCanvasPlot(plot)
        canvas.put_child(child, .15, .06, .65, .31);
        plot.show()
        #child.set_property("flags",
        #                   child.get_property("flags") |
        #                   gtkextra.PLOT_CANVAS_PLOT_SELECT_POINT |
        #                   gtkextra.PLOT_CANVAS_PLOT_DND_POINT)
        self.build_example1(plot)

        plot = self.new_layer(canvas)
        plot.set_background(light_yellow)
        plot.legends_set_attributes(None, 0, None, light_blue)
        plot.set_range(0.0, 1.0, 0.0, 0.85)

        axis_right = plot.get_axis(gtkextra.PLOT_AXIS_RIGHT)
        axis_top = plot.get_axis(gtkextra.PLOT_AXIS_TOP)
        axis_top.set_visible(True)
        axis_right.set_visible(True)
        axis_top.hide_title()
        axis_right.hide_title()
        plot.grids_set_visible(True, True, True, True)
        plot.set_legends_border(gtkextra.PLOT_BORDER_SHADOW, 3)
        plot.legends_move(0.58, 0.05)
        plot.show()

        child = gtkextra.PlotCanvasPlot(plot)
        canvas.put_child(child, .15, .4, .65, .65)
        plot.show()
        self.build_example2(plot)

        #canvas.connect("move_item", self.move_item)
        canvas.connect("select_item", self.select_item)


        child = gtkextra.PlotCanvasText("Times-BoldItalic", 16, 0, None, None, True, gtk.JUSTIFY_CENTER,
                                        "DnD titles, legends and plots")
        canvas.put_child(child, .40, .020, .0, .0)
        child = gtkextra.PlotCanvasText("Times-Roman", 16, 0, None, None, True, gtk.JUSTIFY_CENTER,
                                         "You can use \\ssubscripts\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\N\\Ssuperscripts");
        canvas.put_child(child, .40, .720, .0, .0)
        child = gtkextra.PlotCanvasText("Times-Roman", 12, 0, None, None, True, gtk.JUSTIFY_CENTER, 
                                         "Format text mixing \\Bbold \\N\\i, italics, \\ggreek \\4\\N and \\+different fonts");
        canvas.put_child(child, .40, .765, .0, .0)
        child.text.set_border(gtkextra.PLOT_BORDER_SHADOW, 2, 0, 2) #FIXME: does not work

        self.show_all()
        canvas.export_ps_with_size("plotdemo.ps", epsflag=True)
        print "Wrote plotdemo.ps"

    def move_item(self, canvas, item, new_x, new_y, *args):
        print "move_item"
        if item.type == gtkextra.PLOT_CANVAS_DATA:
            print "MOVING DATA"
            (i, old_x, old_y) = canvas.get_active_point()
            print "Active point: %d -> %f %f" % (i, new_x, new_y)
            data = canvas.get_active_data()
            x, y, dx, dy = data.x, data.y, data.dx, data.dy
            x[i] = new_x
            y[i] = new_y
            data.set_points(x=x, y=y, dx=dx, dy=dy)
        return True

    def select_item(self, canvas, event, item):
        if isinstance(item, gtkextra.PlotCanvasText):
            print "Item selected: TEXT"
        elif isinstance(item, gtkextra.PlotCanvasPixmap):
            print "Item selected: PIXMAP"
        elif isinstance(item, gtkextra.PlotCanvasRectangle):
            print "Item selected: RECTANGLE"
        elif isinstance(item, gtkextra.PlotCanvasEllipse):
            print "Item selected: ELLIPSE"
        elif isinstance(item, gtkextra.PlotCanvasLine):
            print "Item selected: LINE"
        elif isinstance(item, gtkextra.PlotCanvasPlot):
            #print "Item selected: PLOT", item.pos
            if item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_TITLE:
                print "Item selected: TITLE"
            elif item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_LEGENDS:
                print "Item selected: LEGENDS"
            elif item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_PLOT:
                print "Item selected: PLOT"
            elif item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_AXIS:
                print "Item selected: AXIS"
            elif item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_MARKER:
                print "Item selected: MARKER"
            elif item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_GRADIENT:
                print "Item selected: GRADIENT"
            elif item.pos == gtkextra.PLOT_CANVAS_PLOT_IN_DATA:
                print "Item selected: DATA"
                #FIXME
                #x = gtk_plot_data_get_x(GTK_PLOT_CANVAS_PLOT(child)->data, &n); 
                #y = gtk_plot_data_get_y(GTK_PLOT_CANVAS_PLOT(child)->data, &n); 
                #n = GTK_PLOT_CANVAS_PLOT(child)->datapoint;
                #printf("Item selected: DATA\n");
                #printf("Active point: %d -> %f %f\n", 
                #GTK_PLOT_CANVAS_PLOT(child)->datapoint, x[n], y[n]);
        return True

    def activate_plot(self, button, canvas, *args):
        if button.get_active():
            for n in xrange(self.nlayers):
                if button == self.buttons[n]:
                    canvas.set_active_plot(self.plots[n])
                else:
                    self.buttons[n].set_active(False) 
        return True

    def activate_button(self, canvas, *args):
        plot = canvas.get_active_plot()
        for n in xrange(self.nlayers):
            if plot == self.plots[n]:
                self.buttons[n].set_active(True)
            else:
                self.buttons[n].set_active(False)
        return True
        
    def new_layer(self, canvas):
        self.nlayers = self.nlayers + 1
        button = gtk.ToggleButton(str(self.nlayers))
        button.set_size_request(20, 20)
        canvas.put(button, (self.nlayers - 1) * 20, 0)
        #button.connect("toggled", self.activate_plot, canvas) #FIXME
        plot = gtkextra.Plot()
        plot.resize(0.5, 0.25)
        self.buttons.append(button)
        self.plots.append(plot)
        button.set_active(True)
        return plot

    def build_example1(self, plot):
        px1 = [0., .2, .4, .6, .8, 1.]
        py1 = [.2, .4, .5, .35, .30, .40]
        dx1 = [.2, .2, .2, .2, .2, .2]
        dy1 = [.1, .1, .1, .1, .1, .1]

        px2 = [0., -.2, -.4, -.6, -.8, -1.]
        py2 = [.2, .4, .5, .35, .30, .40]
        dx2 = [.2, .2, .2, .2, .2, .2]
        dy2 = [.1, .1, .1, .1, .1, .1]

        colormap = self.get_colormap()
        red = colormap.alloc_color("red")
        black = colormap.alloc_color("black")
        blue = colormap.alloc_color("blue")

        data = gtkextra.PlotData()
        data.show()
        plot.add_data(data)
        data.set_points(x=px1, y=py1, dx=dx1, dy=dy1)
        data.set_symbol(gtkextra.PLOT_SYMBOL_DIAMOND, gtkextra.PLOT_SYMBOL_EMPTY, 10, 2, red, red)
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, red)
        data.set_connector(gtkextra.PLOT_CONNECT_SPLINE)
        data.show_yerrbars()
        data.set_legend("Spline + EY")
        data.show_labels(True)
        data.set_labels(['0', '1', '2', '3', '4', '5'])

        data = gtkextra.PlotData()
        data.show()
        plot.add_data(data)
        data.set_points(x=px2, y=py2, dx=dx2, dy=dy2)
        data.set_symbol(gtkextra.PLOT_SYMBOL_SQUARE, gtkextra.PLOT_SYMBOL_OPAQUE, 8, 2, black, black)
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 4, red)
        data.set_connector(gtkextra.PLOT_CONNECT_STRAIGHT)
        data.set_x_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 0, black)
        data.set_y_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 0, black)
        data.set_legend("Line + Symbol")
        
        data = plot.add_function(self.function)
        data.show()
        data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 0, blue)
        data.set_legend("Function Plot")

    def build_example2(self, plot):
        px2 = [.1, .2, .3, .4, .5, .6, .7, .8]
        py2 = [.012, .067, .24, .5, .65, .5, .24, .067]
        dx2 = [.1, .1, .1, .1, .1, .1, .1, .1]

        colormap = self.get_colormap()
        dark_green = colormap.alloc_color("dark green")
        blue = colormap.alloc_color("blue")
        
        data = plot.add_function(self.gaussian)
        data.show()
        data.set_line_attributes(gtkextra.PLOT_LINE_DASHED, 0, 0, 2, dark_green)
        data.set_legend("Gaussian")

        data = gtkextra.PlotBar(gtk.ORIENTATION_VERTICAL)
        data.show()
        plot.add_data(data)
        data.set_points(x=px2, y=py2, dx=dx2)
        data.set_symbol(gtkextra.PLOT_SYMBOL_NONE, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, blue, blue)
        data.set_line_attributes(gtkextra.PLOT_LINE_NONE, 0, 0, 1, blue)
        data.set_connector(gtkextra.PLOT_CONNECT_NONE)
        data.set_legend("V Bars")

    def function(self, x, *extra):
        try:
            return -0.5 + 0.3 * sin(3.0 * x) * sin(50.0 * x)
        except:
            return None

    def gaussian(self, x, *extra):
        try:
            return 0.65 * exp(-0.5 * pow(x - 0.5, 2) / 0.02)
        except:
            return None

if __name__ == '__main__':
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()

