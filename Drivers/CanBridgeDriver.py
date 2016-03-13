import canbridge
import gobject

import Can
import Driver

def decode_canbridge_pkt(canbridge_pkt):
    (id,data,len) = canbridge_pkt
    bytes = []
    for i in range(len):
        bytes.append(data & 0xFF)
        data = data >> 8
    return (id, bytes)
            
def encode_canbridge_pkt(id, data):
    value = 0
    for i in range(len(data)):
        value += data[i] << (i*8)
    return (id,value,len(data))

class CanBridgeDriver(Driver.Driver, Can.Interface):
    def __init__(self, sa, config, name="CanBridge"):
        Can.Interface.__init__(self)
        Driver.Driver.__init__(self, sa, config, name=name)
        gobject.timeout_add(5, self.poll)

    def poll(self):
        canbridge.outputSend()
        canbridge.inputRecv()
        pkt = canbridge.inputDequeue()
        while pkt is not None:
            (id, data) = decode_canbridge_pkt(pkt)
            self.deliver(Can.Packet(id, data))
            pkt = canbridge.inputDequeue()
        
        return 1

    def send(self, pkt):
        Can.Interface.send(self, pkt)
        cbpkt = encode_canbridge_pkt(pkt.get_id(), pkt.get_data())
        (a,b,c) = cbpkt
        print "Queueing: %d %d %d" % cbpkt
        canbridge.outputQueue( cbpkt )

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Can Bridge", CanBridgeDriver)
