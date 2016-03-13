#!/usr/bin/env python

import string
import gtk
import gtkextra
import pixmaps

DEFAULT_PRECISION = 3
DEFAULT_SPACE = 8

class Example1(gtkextra.Sheet):

    xfont1 = "-bitstream-charter-bold-r-normal--28-280-72-72-p-0-iso8859-1"
    xfont2 = "-bitstream-charter-bold-r-normal--36-360-72-72-p-0-iso8859-1"

    text = [ "GtkSheet is a matrix where you can allocate cells of text.",
        "Cell contents can be edited interactively with an specially designed entry",
        "You can change colors, borders, and many other attributes",
        "Drag & drop or resize the selection clicking the corner or border",
        "Store the selection on the clipboard pressing Ctrl-C",
        "(The selection handler has not been implemented yet)",
        "You can add buttons, charts, pixmaps, and other widgets" ]
    
    def __init__(self):
        gtkextra.Sheet.__init__(self, 1000, 26, "Example 1")
        
        colormap = self.get_colormap()

        self.set_background(colormap.alloc_color("light yellow"))
        self.set_grid(colormap.alloc_color("light blue"))
        
        for column in xrange(self.get_columns_count()):
            name = chr(ord("A") + column)
            self.column_button_add_label(column, name)
            self.set_column_title(column, name)

        self.row_button_add_label(0, "This is\na multiline\nlabel")
        self.row_button_justify(0, gtk.JUSTIFY_RIGHT)

        range = gtkextra.SheetRange(1, 1, 2, 3)
        self.clip_range(range)

        # As long as a GdkFont object is used a reference to it must be kept.
        self.font1 = gtk.load_font(self.xfont1)
        if not self.font1:
            print "Couldn't load", self.xfont1
        else:
            self.range_set_font(range, self.font1)

        self.range_set_foreground(range, colormap.alloc_color("red"))

        self.set_cell(1, 2, gtk.JUSTIFY_CENTER, "Welcome to")

        range.row0 = 2

        self.font2 = load_font(self.xfont2)
        if not self.font2:
            print "Couldn't load", self.xfont2
        else:
            self.range_set_font(range, self.font2)

        self.range_set_foreground(range, colormap.alloc_color("blue"))

        self.set_cell(2, 2, gtk.JUSTIFY_CENTER, "GtkSheet")

        range = GtkSheetRange(3, 0, 3, 4)
        self.range_set_background(range, colormap.alloc_color("dark gray"))
        self.range_set_foreground(range, colormap.alloc_color("green"))

        self.set_cell(3, 2, gtk.JUSTIFY_CENTER, "a Matrix widget for Gtk+")

        (pixmap, mask) = create_pixmap_from_xpm_d(colormap, None,
                                                  pixmaps.bullet_xpm)

        row = 4
        for line in self.text:
            if line[0] != "(":
                bullet = GtkPixmap(pixmap, mask)
                self.attach(bullet, row, 0, .5, .5)
            self.set_cell(row, 1, gtk.JUSTIFY_LEFT, line)
            row = row + 1

        (pixmap, mask) = create_pixmap_from_xpm_d(colormap, None,
                                                  pixmaps.smile_xpm)
        smile = GtkPixmap(pixmap, mask)
        self.button_attach(smile, -1, 5, .5, .5)

        self.connect("key_press_event", self.clipboard_handler)
        self.connect("resize_range", self.resize_handler)
        self.connect("move_range", self.move_handler)
        self.connect("traverse", self.alarm_traverse)
        
        self.curve = GtkCurve()
        self.curve.set_range(0, 200, 0, 200)

        show_button = GtkButton("Show me a plot")
        show_button.set_size_request(100, 60)
        self.attach(show_button, 12, 2, .5, .5)
        show_button.connect("clicked", self.show_child)

    def clipboard_handler(self, widget, key):
        if key.state & GDK.CONTROL_MASK:
            keyval = string.upper(chr(key.keyval))
            if keyval == "C" and self.get_state() != STATE_NORMAL:
                self.unclip_range()
                self.clip_range(self.get_range())
            elif keyval == "X":
                self.unclip_range()

    def resize_handler(self, widget, old_range, new_range, *args):
        print "OLD SELECTION: %d %d %d %d" % tuple(old_range)
        print "NEW SELECTION: %d %d %d %d" % tuple(new_range)

    def move_handler(self, widget, old_range, new_range, *args):
        print "OLD SELECTION: %d %d %d %d" % tuple(old_range)
        print "NEW SELECTION: %d %d %d %d" % tuple(new_range)

    def alarm_traverse(self, widget, row, column, new_row, new_column, *args):
        print "TRAVERSE: %d %d %d %d" % (row, column, new_row, new_column)
        # You can return gtk.FALSE, gtk.TRUE or a 2-tuple.
        return (new_row, new_column)

    def show_child(self, *args):
        if not self.curve.flags(MAPPED):
            self.attach(self.curve, 2, 7, 0., 0.)


class Example2(gtkextra.Sheet):

    text = [ ("Click the right mouse button to display a popup", "blue"),
             ("You can connect a parser to the 'set cell' signal", "red"),
             ("(Try typing numbers)", "black") ]

    def __init__(self):
        gtkextra.Sheet.__init__(self, 1000, 26, "Example 2")

        self.sheet_unset_flags(gtkextra.SHEET_AUTO_SCROLL)
        self.set_selection_mode(gtk.SELECTION_SINGLE)
        
        colormap = self.get_colormap()

        range = gtkextra.SheetRange(0, 0, 2, self.get_columns_count() - 1)
        self.range_set_editable(range, gtk.FALSE)
        self.range_set_background(range, colormap.alloc_color("light gray"))

        row = 0
        for (line, colorname) in self.text:
            range.row0 = row
            self.range_set_foreground(range, colormap.alloc_color(colorname))
            self.row_set_sensitivity(row, gtk.FALSE)
            self.set_cell(row, 2, gtk.JUSTIFY_CENTER, line)
            row = row + 1
        self.set_active_cell(row, 0)

        self.connect("button_press_event", self.do_popup)
        self.connect("set_cell", self.parse_numbers)

    def popup_activated(self, widget, item, *args):
        state = self.get_state()
        range = self.get_range()
        if item == "Add Column":
            self.add_column(1)
        elif item == "Add Row":
            self.add_row(1)
        elif item == "Insert Row":
            if state == SHEET_ROW_SELECTED:
                self.insert_rows(range.row0, range.rowi - range.row0 + 1)
        elif item == "Insert Column":
            if state == SHEET_COLUMN_SELECTED:
                self.insert_columns(range.col0, range.coli - range.col0 + 1)
        elif item == "Delete Row":
            if state == SHEET_ROW_SELECTED:
                self.delete_rows(range.row0, range.rowi - range.row0 + 1)
        elif item == "Delete Column":
            if state == SHEET_COLUMN_SELECTED:
                self.delete_columns(range.col0, range.coli - range.col0 + 1)
        elif item == "Clear Cells":
            self.range_clear(range)
        self.popup = None
        return gtk.TRUE

    def build_menu(self):
        items = [ "Add Column", "Add Row", "Insert Row", "Insert Column",
                  "Delete Row", "Delete Column", "Clear Cells" ]
        menu = GtkMenu()
        i = 0
        for label in items:
            item = gtk.MenuItem(label)
            item.connect("activate", self.popup_activated, label)
            item.set_flags(SENSITIVE | CAN_FOCUS)
            state = self.get_state()
            if i in (2, 4):
                if state != SHEET_ROW_SELECTED:
                    item.unset_flags(SENSITIVE | CAN_FOCUS)
            elif i in (3, 5):
                if state != SHEET_COLUMN_SELECTED:
                    item.unset_flags(SENSITIVE | CAN_FOCUS)
            item.show()
            menu.append(item)
            i = i + 1
        return menu
    
    def do_popup(self, widget, event, *args):
        mods = self.get_window().pointer_state
        if mods & GDK.BUTTON3_MASK:
            self.popup = self.build_menu()
            self.popup.popup(None, None, None, event.button, event.time)
        return gtk.TRUE

    def format_text(self, column, justification, text):
        try:
            val = float(text)
        except:
            pass
        else:
            justification = gtk.JUSTIFY_RIGHT
            cell_width = self.get_column_width(column)
            char_width = gdk_char_width(self.get_style().font, "X")
            space = float(cell_width) / float(char_width)
            intspace = int(min(space, DEFAULT_SPACE))
            
            if val < 0:
                auxval = -val
            else:
                auxval = val

            digspace = 0
            while auxval < 1 and auxval != 0.:
                auxval = auxval * 10.0
                digspace = digspace + 1

            if digspace + DEFAULT_PRECISION + 1 > intspace \
               or digspace > DEFAULT_PRECISION:
                text = "%*.*E" % (intspace, DEFAULT_PRECISION, val)
            else:
                intspace = min(intspace, len(text) - digspace - 1)
                text = "%*.*f" % (intspace, DEFAULT_PRECISION, val)
                if len(text) > space:
                    text = "%*.*E" % (intspace, DEFAULT_PRECISION, val)
        
        return (justification, text)
    
    def parse_numbers(self, widget, row, column, *args):
        sheet_entry = self.get_entry()
        justification = sheet_entry.get_justification()
        label = sheet_entry.get_text()
        (justification, label) = self.format_text(column, justification, label)
        self.set_cell(row, column, justification, label)
        

class Example3(gtkextra.Sheet):

    def __init__(self):
        gtkextra.Sheet.__init__(self, 1000, 26, "Example 3")

        self.show_grid(gtk.FALSE)

        colormap = self.get_colormap()

        range = gtkextra.SheetRange(0, 0, 10, 6)
        self.range_set_background(range, colormap.alloc_color("orange"))
        self.range_set_foreground(range, colormap.alloc_color("violet"))
        range.row0 = 1
        self.range_set_background(range, colormap.alloc_color("blue"))
        range.coli = 0
        self.range_set_background(range, colormap.alloc_color("dark green"))

        range.row0 = 0
        self.range_set_border_color(range, colormap.alloc_color("dark blue"))
        self.range_set_border(range, SHEET_RIGHT_BORDER, 4,
                              GDK.LINE_ON_OFF_DASH)
        range.col0 = 0
        range.rowi = 0
        range.coli = 0
        self.range_set_background(range, colormap.alloc_color("red"))
        self.range_set_border(range, SHEET_RIGHT_BORDER |
                              SHEET_BOTTOM_BORDER, 4, GDK.LINE_SOLID)
        range.col0 = 1
        range.rowi = 0
        range.coli = 6
        self.range_set_border_color(range, colormap.alloc_color("dark blue"))
        self.range_set_border(range, SHEET_BOTTOM_BORDER, 4,
                              GDK.LINE_ON_OFF_DASH)

        self.sheet_set_flags(SHEET_AUTO_RESIZE)

        self.changeentry(None, 0, 1, 0, 0)

        self.connect("traverse", self.changeentry)

    def changeentry(self, widget, row, column, new_row, new_column, *args):
        if new_column == 0 and column != 0:
            self.change_entry(gtk.Combo.get_type())
            entry = self.get_entry()
            combo = entry.get_ancestor(gtk.Combo.get_type())
            combo.set_popdown_strings(["", "foo", "bar", "baz"])
        if new_column == 1 and column != 1:
            self.change_entry(gtk.Entry.get_type())
        if new_column == 2 and column != 2:
            self.change_entry(gtk.SpinButton.get_type())
        if new_column >= 3 and column < 3:
            self.change_entry(gtk.ItemEntry.get_type())
        return gtk.TRUE


class PixmapButton(gtk.ToggleButton):

    def __init__(self, pixmap_data):
        gtk.ToggleButton.__init__(self)
        (pixmap, mask) = gtk.gdk.pixmap_colormap_create_from_xpm_d(None, self.get_colormap(),
                                                                   None, pixmap_data)

        self.pixmap = gtk.Pixmap(pixmap, mask)
        self.add(self.pixmap)


class ColorCombo(gtkextra.ColorCombo):
    
    def __init__(self, pixmap_data, rectangle):
        gtkextra.ColorCombo.__init__(self)
        (pixmap, mask) = create_pixmap_from_xpm_d(self.get_colormap(), None,
                                                  pixmap_data)
        self.pixmap = gtk.Pixmap(pixmap, mask)
        self.button.add(self.pixmap)
        self.rectangle = rectangle
        self.connect("changed", self.change_color)

    def change_color(self, widget, i, colorname, *args):
        color = self.get_colormap().alloc_color(colorname)
        tmp_gc = self.get_window().new_gc()
        tmp_gc.foreground = color
        (pixmap, mask) = self.pixmap.get()
        (x, y, width, height) = self.rectangle
        draw_rectangle(pixmap, tmp_gc, gtk.TRUE, x, y, width, height)
        self.pixmap.queue_draw()
        

class Application(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GtkSheet Demo")
        self.set_size_request(900, 600)
        self.connect("destroy", lambda win : gtk.main_quit())

        main_vbox = gtk.VBox(spacing=1)
        main_vbox.set_border_width(0)
        self.add(main_vbox)

        show_hide_box = gtk.HBox(spacing=1)
        hide_row_titles = gtk.Button("Hide Row Titles") 
        hide_column_titles = gtk.Button("Hide Column Titles")
        show_row_titles = gtk.Button("Show Row Titles")
        show_column_titles = gtk.Button("Show Column Titles")

        show_hide_box.pack_start(hide_row_titles)
        show_hide_box.pack_start(hide_column_titles)
        show_hide_box.pack_start(show_row_titles)
        show_hide_box.pack_start(show_column_titles)

        hide_row_titles.connect("clicked", self.do_hide_row_titles)
        hide_column_titles.connect("clicked", self.do_hide_column_titles)
        show_row_titles.connect("clicked", self.do_show_row_titles)
        show_column_titles.connect("clicked", self.do_show_column_titles)

        main_vbox.pack_start(show_hide_box, gtk.FALSE)

        toolbar = gtk.Toolbar()
        toolbar.append_space()

        font_combo = gtkextra.FontCombo()
        toolbar.append_widget(font_combo, "font", "font")
        font_combo.italic_button.set_size_request(32, 32)
        font_combo.bold_button.set_size_request(32, 32)
        font_combo.connect("changed", self.new_font)

        toolbar.append_space()

        self.left_button = PixmapButton(pixmaps.left_just)
        toolbar.append_widget(self.left_button, "justify left", "justify left")
        self.left_button.connect("released", self.justify_left)
        
        self.center_button = PixmapButton(pixmaps.center_just)
        toolbar.append_widget(self.center_button, "justify center",
                              "justify center")
        self.center_button.connect("released", self.justify_center)
        
        self.right_button = PixmapButton(pixmaps.right_just)
        toolbar.append_widget(self.right_button, "justify right",
                              "justify right")
        self.right_button.connect("released", self.justify_right)
        
        toolbar.append_space()

        bordercombo = gtkextra.BorderCombo()
        toolbar.append_widget(bordercombo, "border", "border")
        bordercombo.button.set_size_request(32, 32)
        bordercombo.connect("changed", self.change_border)
        
        toolbar.append_space()

        #fgcolorcombo = gtkextra.ColorCombo(pixmaps.font, (5, 20, 16, 4))
        #toolbar.append_widget(fgcolorcombo, "font color", "font color")
        #fgcolorcombo.connect("changed", self.change_foreground)

        toolbar.append_space()

        #bgcolorcombo = gtkextra.ColorCombo(pixmaps.paint, (4, 20, 18, 4))
        #toolbar.append_widget(bgcolorcombo, "background color",
        #                      "background color")
        #bgcolorcombo.connect("changed", self.change_background)

        toolbar.append_space()

        toggle_combo = gtkextra.ToggleCombo(5, 5)
        toolbar.append_widget(toggle_combo, "test", "test")
        toggle_combo.button.set_size_request(32, 32)
                              
        main_vbox.pack_start(toolbar, gtk.FALSE)

        status_box = gtk.HBox(spacing=1)
        status_box.set_border_width(0)
        main_vbox.pack_start(status_box, gtk.FALSE)

        self.location = gtk.Label("")
        (width, height) = self.location.size_request()
        self.location.set_size_request(160, height)
        status_box.pack_start(self.location, gtk.FALSE)

        self.entry = gtk.Entry()
        status_box.pack_start(self.entry)

        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        main_vbox.pack_start(self.notebook)

        #self.sheets = [ Example1(), Example2(), Example3() ]
        #self.sheets = [ Example1() ]
        self.sheets = [ ]
        
        scrolled_windows = []
        n = 1
        for sheet in self.sheets:
            scrolled_window = gtk.ScrolledWindow()
            scrolled_windows.append(scrolled_window)
            scrolled_window.add(sheet)

            label = gtk.Label("Folder %d" % n)
            self.notebook.append_page(scrolled_window, label)

            sheet.get_entry().connect("changed", self.show_entry)
            sheet.connect("activate", self.activate_sheet_cell)

            n = n + 1

        self.entry.connect("changed", self.show_sheet_entry)
        self.entry.connect("activate", self.activate_sheet_entry)

        self.show_all()

    def get_active_sheet(self):
        cur_page = self.notebook.get_current_page()
        return self.sheets[cur_page]
        
    def show_sheet_entry(self, entry, *args):
        if not entry.flags(gtk.HAS_FOCUS):
            return
        sheet = self.get_active_sheet()
        sheet_entry = sheet.get_entry()
        text = entry.get_text()
        sheet_entry.set_text(text)

    def activate_sheet_entry(self, entry, *args):
        sheet = self.get_active_sheet()
        sheet_entry = sheet.get_entry()
        justification = gtk.JUSTIFY_LEFT
        if isinstance(sheet_entry, gtk.ItemEntry):
            justification = sheet_entry.get_justification()
        cell = sheet.get_active_cell()
        if cell:
            (row, column) = cell
            sheet.set_cell(row, column, justification, entry.get_text())
        
    def show_entry(self, sheet_entry, *args):
        if not sheet_entry.flags(gtk.HAS_FOCUS):
            return
        text = sheet_entry.get_text()
        self.entry.set_text(text)

    def activate_sheet_cell(self, sheet, row, column, *args):
        sheet_entry = sheet.get_entry()
        title = sheet.get_column_title(column)
        if title:
            cell = "  %s:%d  " % (title, row)
        else:
            cell = " ROW: %d COLUMN: %d " % (row, column)
        self.location.set_text(cell)
        
        self.entry["max_length"] = sheet_entry["max_length"]
        
        text = sheet.cell_get_text(row, column)
        self.entry.set_text(text)

        attributes = sheet.get_attributes(row, column)

        self.entry.set_editable(attributes.is_editable)

        if attributes.justification == gtk.JUSTIFY_CENTER:
            self.justify_center()
        elif attributes.justification == gtk.JUSTIFY_RIGHT:
            self.justify_right()
        else:
            self.justify_left()

        return gtk.TRUE

    def justify_left(self, *args):
        sheet = self.get_active_sheet()
        self.left_button.set_active(gtk.STATE_ACTIVE)
        self.center_button.set_active(gtk.STATE_NORMAL)
        self.right_button.set_active(gtk.STATE_NORMAL)
        sheet.range_set_justification(sheet.get_range(), gtk.JUSTIFY_LEFT)

    def justify_center(self, *args):
        sheet = self.get_active_sheet()
        self.center_button.set_active(gtk.STATE_ACTIVE)
        self.left_button.set_active(gtk.STATE_NORMAL)
        self.right_button.set_active(gtk.STATE_NORMAL)
        sheet.range_set_justification(sheet.get_range(), gtk.JUSTIFY_CENTER)

    def justify_right(self, *args):
        sheet = self.get_active_sheet()
        self.right_button.set_active(gtk.STATE_ACTIVE)
        self.left_button.set_active(gtk.STATE_NORMAL)
        self.center_button.set_active(gtk.STATE_NORMAL)
        sheet.range_set_justification(sheet.get_range(), gtk.JUSTIFY_RIGHT)

    def change_border(self, widget, border, *args):
        sheet = self.get_active_sheet()
        range = sheet.get_range()
        border_width = 3
        sheet.range_set_border(range, 0, 0)
        if border == 1:
            border_mask = gtkextra.SHEET_TOP_BORDER
            range.rowi = range.row0
            sheet.range_set_border(range, border_mask, border_width)
        elif border == 2:
            border_mask = gtkextra.SHEET_BOTTOM_BORDER
            range.row0 = range.rowi
            sheet.range_set_border(range, border_mask, border_width)
        elif border == 3:
            border_mask = gtkextra.SHEET_RIGHT_BORDER
            range.col0 = range.coli
            sheet.range_set_border(range, border_mask, border_width)
        elif border == 4:
            border_mask = gtkextra.SHEET_LEFT_BORDER
            range.coli = range.col0
            sheet.range_set_border(range, border_mask, border_width)
        elif border == 5:
            if range.col0 == range.coli:
                border_mask = gtkextra.SHEET_LEFT_BORDER | gtkextra.SHEET_RIGHT_BORDER
                sheet.range_set_border(range, border_mask, border_width)
            else:
                border_mask = gtkextra.SHEET_LEFT_BORDER
                auxcol = range.coli
                range.coli = range.col0
                sheet.range_set_border(range, border_mask, border_width)
                border_mask = gtkextra.SHEET_RIGHT_BORDER
                range.col0 = range.coli = auxcol
                sheet.range_set_border(range, border_mask, border_width)
        elif border == 6:
            if range.row0 == range.rowi:
                border_mask = gtkextra.SHEET_TOP_BORDER | gtkextra.SHEET_BOTTOM_BORDER
                sheet.range_set_border(range, border_mask, border_width)
            else:
                border_mask = gtkextra.SHEET_TOP_BORDER
                auxrow = range.rowi
                range.rowi = range.row0
                sheet.range_set_border(range, border_mask, border_width)
                border_mask = gtkextra.SHEET_BOTTOM_BORDER
                range.row0 = range.rowi = auxrow
                sheet.range_set_border(range, border_mask, border_width)
        elif border == 7:
            border_mask = gtkextra.SHEET_RIGHT_BORDER | gtkextra.SHEET_LEFT_BORDER
            sheet.range_set_border(range, border_mask, border_width)
        elif border == 8:
            border_mask = gtkextra.SHEET_BOTTOM_BORDER | gtkextra.SHEET_TOP_BORDER
            sheet.range_set_border(range, border_mask, border_width)
        elif border == 9:
            sheet.range_set_border(range, 15, border_width)
            for i in xrange(range.row0, range.rowi + 1):
                for j in xrange(range.col0, range.coli + 1):
                    border_mask = 15
                    auxrange = gtk.SheetRange(i, j, i, j)
                    if i == range.rowi:
                        border_mask = border_mask ^ gtkextra.SHEET_BOTTOM_BORDER
                    if i == range.row0:
                        border_mask = border_mask ^ gtkextra.SHEET_TOP_BORDER
                    if j == range.coli:
                        border_mask = border_mask ^ gtkextra.SHEET_RIGHT_BORDER
                    if j == range.col0:
                        border_mask = border_mask ^ gtkextra.SHEET_LEFT_BORDER
                    if border_mask != 15:
                        sheet.range_set_border(auxrange, border_mask,
                                               border_width)
        elif border == 10:
            for i in xrange(range.row0, range.rowi + 1):
                for j in xrange(range.col0, range.coli + 1):
                    border_mask = 0
                    auxrange = gtk.SheetRange(i, j, i, j)
                    if i == range.rowi:
                        border_mask = border_mask | gtkextra.SHEET_BOTTOM_BORDER
                    if i == range.row0:
                        border_mask = border_mask | gtkextra.SHEET_TOP_BORDER
                    if j == range.coli:
                        border_mask = border_mask | gtkextra.SHEET_RIGHT_BORDER
                    if j == range.col0:
                        border_mask = border_mask | gtkextra.SHEET_LEFT_BORDER
                    if border_mask != 0:
                        sheet.range_set_border(auxrange, border_mask,
                                               border_width)
        elif border == 11:
            border_mask = 15
            sheet.range_set_border(range, border_mask, border_width)

    def change_foreground(self, widget, i, colorname, *args):
        sheet = self.get_active_sheet()
        color = sheet.get_colormap().alloc_color(colorname)
        sheet.range_set_foreground(sheet.get_range(), color)
        
    def change_background(self, widget, i, colorname, *args):
        sheet = self.get_active_sheet()
        color = sheet.get_colormap().alloc_color(colorname)
        sheet.range_set_background(sheet.get_range(), color)

    def do_hide_row_titles(self, *args):
        self.get_active_sheet().hide_row_titles()

    def do_hide_column_titles(self, *args):
        self.get_active_sheet().hide_column_titles()

    def do_show_row_titles(self, *args):
        self.get_active_sheet().show_row_titles()

    def do_show_column_titles(self, *args):
        self.get_active_sheet().show_column_titles()

    def new_font(self, font_combo, *args):
        sheet = self.get_active_sheet()
        sheet.range_set_font(sheet.get_range(), font_combo.font)

    def mainloop(self):
        mainloop()

if __name__ == '__main__':		
    print 'The Python binding for GtkSheet are not complete.'
    print 'Patches will be accepted if you fix them.'
    raw_input("Press enter to see what done so far.")
    app = Application()
    app.connect("destroy", lambda win : gtk.main_quit())
    gtk.main()

