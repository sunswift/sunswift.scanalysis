import gobject
import gtk

from Can import *

class SimpleLogger:
    def __init__(self, sa):
        self.sa = sa
        if "SimpleLogger" not in self.sa.cfg.cfg:
            self.sa.cfg.cfg["SimpleLogger"] = {}
            self.sa.cfg.cfg["SimpleLogger"]["filename"] = "default.log"
            
        filename = self.sa.cfg.cfg["SimpleLogger"]["filename"]
        self.file = open(filename, "a+")

    def deliver_packet(self, pkt):
        self.file.write("%08x\t" % pkt.id)
        self.file.write("%16x\t" % pkt.data)
        self.file.write("%1x\t" % pkt.len)
        self.file.write(str(pkt.recvd))
        self.file.write("\n"); 

    def flush_file(self):
        self.file.flush()
