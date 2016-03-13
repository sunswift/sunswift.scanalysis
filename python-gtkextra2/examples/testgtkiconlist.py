#!/usr/bin/env python

import gtk, gtkextra
import icons

class Application(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkIconList Demo")
        self.set_size_request(400, 400)
        self.connect("destroy", self.quit)

        hbox1 = gtk.HBox()
        self.add(hbox1)

        table = gtk.Table(4, 2)
        hbox1.pack_start(table, gtk.FALSE, gtk.FALSE)

        notebook = gtk.Notebook()
        hbox1.pack_start(notebook)

        scrollw1 = gtk.ScrolledWindow()
        scrollw1.set_border_width(0)
        scrollw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        label1 = gtk.Label("Worksheets")
        notebook.append_page(scrollw1, label1)

        scrollw2 = gtk.ScrolledWindow()
        scrollw2.set_border_width(0)
        scrollw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        label2 = gtk.Label("Plots")
        notebook.append_page(scrollw2, label2)

        iconlist1 = gtkextra.IconList(48, gtkextra.ICON_LIST_TEXT_BELOW)
        iconlist1.set_selection_mode(gtk.SELECTION_SINGLE)
        iconlist1.connect("select_icon", self.select_icon)
        scrollw1.add_with_viewport(iconlist1)
        for i in xrange(20):
            print "FIXME: IconList.add_from_data"
            #iconlist1.add_from_data(icons.sheet_icon2, "Data %02d" % i)

        iconlist2 = gtkextra.IconList(48, gtkextra.ICON_LIST_TEXT_RIGHT)
        iconlist2.set_selection_mode(gtk.SELECTION_MULTIPLE)
        scrollw2.add_with_viewport(iconlist2)
        for i in xrange(20):
            print "FIXME: IconList.add_from_data"
            #iconlist2.add_from_data(icons.plot_icon2, "Plot %02d" % i)

        self.show_all()

    def select_icon(self, widget, item, event, *args):
        print "SELECTION:", item.label
        return gtk.TRUE
    
    def quit(self, *args):
        gtk.main_quit()

if __name__ == '__main__':
    app = Application()
    gtk.main()
