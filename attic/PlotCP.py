import pygtk
pygtk.require('2.0')
import gtk
import gtkextra
import math

class PlotGraph(gtk.VBox):
    def __init__(self, legend_label = " ", xlabel = "X Axis", ylabel = "Y Axis", \
xtick = 1.0, ytick = 1.0, width = 640, height = 480, symbol = gtkextra.PLOT_SYMBOL_NONE, variable1 = "Road.csv", variable2 = "Stops.csv", variable3 = 1):
	gtk.VBox.__init__(self)
    	self.ylabel = ylabel
	self.xlabel = xlabel
        self.xtick = xtick
        self.ytick = ytick
	self.variable1 = variable1
	self.variable2 = variable2
	self.variable3 = int(variable3)

	colormap = self.get_colormap()
        self.red = colormap.alloc_color("red")
        self.blue = colormap.alloc_color("blue")
        self.green = colormap.alloc_color("green")
        self.light_blue = colormap.alloc_color("light blue")
        self.light_yellow = colormap.alloc_color("light yellow")
        self.white = colormap.alloc_color("white")

	colour = self.red

	self.canvas = canvas = gtkextra.PlotCanvas(width, height)
        canvas.set_background(self.white)
        self.pack_start(canvas)

	self.plot = plot = gtkextra.Plot()

        plot.resize(width=0.65, height=1.0)
        plot.set_background(self.light_yellow)
        plot.legends_set_attributes(None, 0, None, self.white)
        plot.set_legends_border(gtkextra.PLOT_BORDER_SHADOW, 3)
        plot.legends_move(0.05, 1.23)
        plot.hide_legends()

	plot.set_range(0.0000, 3100.0000, 0.0000, 3100.0000)
        plot.set_ticks(gtkextra.PLOT_AXIS_X, self.xtick, 1)
        plot.set_ticks(gtkextra.PLOT_AXIS_Y, self.ytick, 1)

	axis_left = plot.get_axis(gtkextra.PLOT_AXIS_LEFT)
        axis_right = plot.get_axis(gtkextra.PLOT_AXIS_RIGHT)
        axis_top = plot.get_axis(gtkextra.PLOT_AXIS_TOP)
        axis_bottom = plot.get_axis(gtkextra.PLOT_AXIS_BOTTOM)
        axis_x = plot.get_axis(gtkextra.PLOT_AXIS_X)
        axis_y = plot.get_axis(gtkextra.PLOT_AXIS_Y)

        axis_top.set_labels_style(gtkextra.PLOT_LABEL_FLOAT, 0)
        axis_bottom.set_labels_style(gtkextra.PLOT_LABEL_FLOAT, 0)
        
        axis_top.set_visible(True)
        axis_right.set_visible(False)
        axis_bottom.set_visible(True)
        axis_left.set_visible(True)

        axis_bottom.move_title(0, 0.5, 1.17)
	axis_top.move_title(0, 0.5, 0.03)

        plot.grids_set_visible(False, False, True, False)
        
        axis_top.set_title(legend_label)
        axis_left.set_title(self.ylabel)
        axis_bottom.set_title(self.xlabel)

	child = gtkextra.PlotCanvasPlot(plot)
        canvas.put_child(child, .15, .15, .9, 0.8);

	self.data = data = gtkextra.PlotData()

	self.plot.add_data(data)
	self.plot.show()

	self.data.show()
	self.data.set_legend(legend_label)

       	self.data.set_symbol(symbol, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, colour, colour)
       	self.data.set_line_attributes(gtkextra.PLOT_LINE_SOLID, 0, 0, 1, colour)
	
        
	if (legend_label == "Latitude vs Longitude") and (variable2 != ""):
	    self.data2 = data2 = gtkextra.PlotData()
	    self.plot.add_data(data2)
	    self.data2.show()
	    stops_name = self.get_stops_name()
	    #lbl = gtk.Label("abc")
	    #self.data2.set_labels(lbl)
	    self.data2.set_symbol(gtkextra.PLOT_SYMBOL_DIAMOND, gtkextra.PLOT_SYMBOL_OPAQUE, 10, 2, colour, colour)
	    self.data2.set_line_attributes(gtkextra.PLOT_LINE_NONE, 0, 0, 1, self.blue)


       	self.plot.clip_data(True)

       	self.canvas.paint()
       	self.canvas.refresh()
	self.show_all()

	if legend_label == "Latitude vs Longitude":
	    px = self.get_latitude()
	    py = self.get_longitude()
	else:
	    px = self.get_chainage()
	    py = self.get_altitude()

	self.data.set_points(x=px, y=py)

	if (legend_label == "Latitude vs Longitude") and (variable2 != ""):
	    sx = self.get_stops_lat()
	    sy = self.get_stops_lon()
	    self.data2.set_points(x=sx, y=sy)

	xmin = min(px)
	xmax = max(px)
	ymin = min(py)
	ymax = max(py)

	self.plot.set_xrange(xmin, xmax)
	self.plot.set_yrange(ymin, ymax)

	canvas.paint()
	canvas.refresh()

    def get_longitude(self):
	longitude = []
	road = open(self.variable1,"r")

	for line in road:
		temp = line.split(",")
		b = float(temp[1])	
		a = round(b, 4)
		longitude.append(a)

	road.close()
	return longitude[::self.variable3]

    def get_latitude(self):
	latitude = []
	road = open(self.variable1,"r")

	for line in road:
		temp = line.split(",")
		b = float(temp[2])	
		a = round(b, 4)
		latitude.append(a)

	road.close()
	return latitude[::self.variable3]

    def get_altitude(self):
	altitude = []
	road = open(self.variable1,"r")

	for line in road:
		temp = line.split(",")
		b = float(temp[3])	
		a = round(b, 4)
		altitude.append(a)

	road.close()
	return altitude[::self.variable3]

    def get_chainage(self):
	chainage = []
	road = open(self.variable1,"r")

	for line in road:
		temp = line.split(",")
		b = float(temp[4])	
		a = round(b, 4)
		chainage.append(a)

	road.close()
	return chainage[::self.variable3]

    def get_course_index(self):
	course_index = []
	road = open(self.variable,"r")

	for line in road:
		temp = line.split(",")
		a = int(temp[0])
		course_index.append(a)

	road.close()
	return course_index[::]

    def get_stops_index(self):
	stops_index = []
	stops = open(self.variable2,"r")

	for line in stops:
		temp = line.split(",")
		a = int(temp[0])
		stops_index.append(a)

	stops.close()
	return stops_index[::]

    def get_stops_lon(self):
	stops_lon = []
	stops = open(self.variable2,"r")

	for line in stops:
		temp = line.split(",")
		b = float(temp[1])
		a = round(b, 4)
		stops_lon.append(a)

	stops.close()
	return stops_lon[::]

    def get_stops_lat(self):
	stops_lat = []
	stops = open(self.variable2,"r")

	for line in stops:
		temp = line.split(",")
		b = float(temp[2])
		a = round(b, 4)
		stops_lat.append(a)

	stops.close()
	return stops_lat[::]


    def get_stops_name(self):
	stops_name = []
	stops = open(self.variable2,"r")

	for line in stops:
		temp = line.split(",")
		a = temp[4]
		stops_name.append(a)

	stops.close()
	return stops_name[::]

















