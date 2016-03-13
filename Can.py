# --------------------------------------------------------------------------                                 
#  Scanalysis CAN Library
#  File name: Can.py
#  Author: David Snowdon
#  Description: CAN support
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

import time
import sys
import Driver

class Packet(Driver.Deliverable):
    def __init__(self, id, data, timestamp=None):
        self.id = id
        self.data = data
        if timestamp is None:
            self.recvd = time.time()
        else:
            self.recvd = timestamp
    
    def get_data(self):
        return self.data

    def get_id(self):
        return self.id

    def get_length(self):
        return len(self.data)

    def get_recvd(self):
        return self.recvd

    def get_value(self):
        return self.id

    def get_time(self):
        return self.recvd

class Interface(Driver.Deliverer):
    def __init__(self):
        Driver.Deliverer.__init__(self)
        self.sent = 0
        self.rcvd = 0

    def get_count(self):
        return self.sent + self.rcvd
    
    def get_num_sent(self):
        return self.sent

    def get_num_rcvd(self):
        return self.rcvd

    def send(self, pkt):
        self.sent += 1

    def is_active(self):
        return True
    
