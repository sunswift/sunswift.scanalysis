#!/usr/bin/env python

import gtk
import gtkextra

class Application(gtkextra.CharSelection):

    def __init__(self):
        gtkextra.CharSelection.__init__(self)
        self.connect("destroy", self.quit)
        self.cancel_button.connect("clicked", self.quit)
        self.ok_button.connect("clicked", self.ok_clicked)
        self.show()

    def ok_clicked(self, *args):
        psfont = self.font_combo.get_psfont()
        psname_f = psfont.get_psfontname()
        psname_a = psfont.psname
        code = self.selection
        print "psname_f=%s psname_a=%s code=%d " % (psname_f, psname_a, code)
        
    def quit(self, *args):
        gtk.main_quit()


if __name__ == '__main__':		
    app = Application()
    gtk.main()
