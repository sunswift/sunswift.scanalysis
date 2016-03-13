#!/usr/bin/env python

import gtk
import gtkextra

class Application(gtk.Window):
    
    cloud_xpm = [
        "24 24 5 1",
        " 	c None",
        "x	c #FFFFFFFFFFFF",
        ".	c #6E6E6E6E6E6E",
        "X	c #000000000000",
        "o	c #CCCCCCCCCCCC",
        "                        ",
        "                        ",
        "                        ",
        "                        ",
        "                        ",
        "         .....          ",
        "        .xxxxxX         ",
        "      ...xxxxxxX        ",
        "     .xxxxxxxxxxX       ",
        "    .xxxxoxxxoxx.XXX    ",
        "    .xxxxxooxxo.xxxXX   ",
        "  ..xxxoxxxoxoxxxxxxXX  ",
        " ..xxxxoxxxxxxxoxxxoxX  ",
        " .xxxxxoxxxxxxooxoxxxX  ",
        " XxxxxxoxoXxxooXoxoxXXX ",
        " Xxooooooooooo.XoooxXoX ",
        " XXooxooXXoo..Xooo.Xo.X ",
        "  XX....XXo..XX...XX.XX ",
        "   XX..XXX.XXXX..XXXXX  ",
        "    XXXX XXX XXXXX      ",
        "                        ",
        "                        ",
        "                        ",
        "                        "]

    suncloud_xpm = [
        "24 24 7 1",
        " 	c None",
        "x	c #FFFFFFFFFFFF",
        ".	c #F7F7BABA3C3C",
        "X	c #FFFFFFFF0000",
        "o	c #AAAAAAAAAAAA",
        "O	c #000000000000",
        "+	c #CCCCCCCCCCCC",
        "@	c #6E6E6E6E6E6E",
        "                        ",
        "        .  .            ",
        "     .  .  .  .         ",
        "      .XX..XX.          ",
        "   .  X......X  .       ",
        "    .X..XXXX..X.        ",
        "    X.XXXXXXXX.X        ",
        "  ..X.XXXXXXXX.X..      ",
        "   X.XXXXoooooX.X       ",
        "   X.XXXoxxxxxO.X       ",
        " ....XoooxxxxxxO...     ",
        "   X.oxxxxxxxxxxO       ",
        "   Xooxxx+xxx+xx@OOO    ",
        "   .oxxxxx++xx+@xxxOO   ",
        "  @@xxx+xxx+x+xxxxxxOO  ",
        " @@xxxx+xxxxxxx+xxx+xO  ",
        " @xxxxx+xxxxxx++x+xxxO  ",
        " Oxxxxx+x+Oxx++O+x+xOOO ",
        " Ox+++++++++++@O+++xO+O ",
        " OO++x++OO++@@O+++@O+@O ",
        "  OO@@@@OO+@@OO@@@OO@OO ",
        "   OO@@OOO@OOOO@@OOOOO  ",
        "    OOOO OOO OOOOO      ",
        "                        "]

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title=("GtkPlot3D Demo")
        self.set_size_request(550, 650)

        colormap = self.get_colormap()
        
        self.canvas = canvas = gtkextra.PlotCanvas(gtkextra.PLOT_LETTER_W, gtkextra.PLOT_LETTER_H)
        canvas.plot_canvas_set_flags(gtkextra.PLOT_CANVAS_DND_FLAGS)
        self.add(canvas)

        plot = gtkextra.Plot(width=0.5, height=0.25)
        plot.set_range(0.0, 1.0, 0.0, 1.4)
        plot.legends_move(0.5, 0.05)
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
        px2 = [.0, .2, .4, .6, .8, 1.0]
        py2 = [.12, .22, .27, .12, .52, .62]

        (pixmap, mask) = gtk.gdk.pixmap_colormap_create_from_xpm_d(None, colormap,
                                                                   None, self.cloud_xpm)
        data = gtkextra.PlotPixmap(pixmap, mask)
        data.set_points(x=px1, y=py1)
        data.set_legend("Pixmap 1")
        plot.add_data(data)

        (pixmap, mask) = gtk.gdk.pixmap_colormap_create_from_xpm_d(None, colormap,
                                                                   None, self.suncloud_xpm)

        data = gtkextra.PlotPixmap(pixmap, mask)
        data.set_points(x=px2, y=py2)
        data.set_legend("Pixmap 2")
        plot.add_data(data)

        self.show_all()

        try:
            canvas.export_ps("demopixmap.ps")
            print "Wrote demopixmap.ps"
        except:
            pass

if __name__ == '__main__':		
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
