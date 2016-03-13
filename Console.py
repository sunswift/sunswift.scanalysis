# --------------------------------------------------------------------------                                 
#  Scanalysis Console
#  File name: Console.py
#  Author: David Snowdon
#  Description: Console support
#
#  Copyright (C) David Snowdon, 2009. 
#   
#  Date: 01-10-2009
# -------------------------------------------------------------------------- 
#
#  This file is part of Scanalysis.
#  
#  Scanalysis is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Scanalysis is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Scanalysis.  If not, see <http://www.gnu.org/licenses/>.

import gobject
import gtk
import time
import thread

class Console (gtk.ScrolledWindow):
    def __init__(self, sa):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        self.tv = tv = gtk.TextView(buffer=None)
        tv.set_editable(False)

        self.add(tv)

        table = tv.get_buffer().get_tag_table()
        date_tag = gtk.TextTag(name="date")
        date_tag.set_property("weight", 700)

        text_tag = gtk.TextTag(name="text")
        text_tag.set_property("weight", 400)

        table.add(date_tag)
        table.add(text_tag)

        self.console_lock = thread.allocate_lock()

        self.write("Console started")

    def write(self, string, timenow=None, mod=None, label=None):
        """Write to the console

string is the string to write. 

timenow is the time in unix format. If it is none, then the current time is used instead. 

mod is the module which is making this call. """

        print "Console: " + string + " " + str(timenow)
        return

        self.console_lock.acquire()
        max = self.get_vadjustment().get_property("upper")

        buf = self.tv.get_buffer()
        iter = buf.get_start_iter()
    

        # Insert the time
        if timenow is None:
            loctime = time.localtime()
        else:
            loctime = time.localtime(timenow)
        timestr = time.strftime("%d/%m/%Y %H:%M:%S", loctime)
        buf.insert_with_tags_by_name(iter, timestr, "date")

        if mod is not None:
            buf.insert_with_tags_by_name(iter, "\t" + mod.get_display_name())

        if label is not None:
            buf.insert_with_tags_by_name(iter, "\t" + label)

        buf.insert_with_tags_by_name(iter, ":\t")

        buf.insert_with_tags_by_name(iter, string + "\n", "text")

        self.console_lock.release()

    
    def deliver(self, labelstr, pkt):
        '''A function to be used as a delivery function'''         
        print "Got delivery -- %s, %s" % (labelstr, str(pkt))
        self.write(str(pkt), timenow=pkt.get_time(), label=labelstr)


