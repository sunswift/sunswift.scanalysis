#!/usr/bin/env python

import gtk
import gtkextra

PREVIEW_TEXT = "ABCDEFGHI abcdefghi 0123456789"
    
class Application(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkFontCombo Demo")

        vbox = gtk.VBox()
        self.add(vbox)

        font_combo = gtkextra.FontCombo()
        vbox.pack_start(font_combo, gtk.FALSE, gtk.FALSE)

        preview_entry = gtk.Entry()
        preview_entry.set_text(PREVIEW_TEXT)
        vbox.pack_start(preview_entry)

        self.new_font(font_combo, preview_entry)
        font_combo.connect("changed", self.new_font, preview_entry)

        self.show_all()

    def new_font(self, font_combo, preview_entry, *args):
        if 0:
            # The C example is as follows:
            # But pygtk2 style does not allow setting font_desc.
            style = preview_entry.get_style().copy()
            style.font_desc = font_combo.get_font_description()
            preview_entry.set_style(style)
        else:
            #This works though.
            preview_entry.modify_font(font_combo.get_font_description())
        if not preview_entry.get_text():
            preview_entry.set_text(PREVIEW_TEXT)
        preview_entry.set_position(0)
        
if __name__ == '__main__':		
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()
