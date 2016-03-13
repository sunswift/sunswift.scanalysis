#!/usr/bin/env python

import gtk

# Simple PyGtk2 window
class TestWin(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("destroy", self.quit)

        b=gtk.Button("Ok")
        self.add(b)
        b.connect("clicked", self.ok_clicked)
        
        self.show_all()
    def ok_clicked(self, *args):
        print "OK"

    def main(self):
        gtk.main()
        
    def quit(self, *args):
        gtk.main_quit()
        print 'done'

if __name__ == '__main__':		
    w = TestWin()
    w.main()
