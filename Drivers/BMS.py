import struct
import serial

class BMS:
    data_types = {2 : {"length": 2, "name":"ping", "has_val":False}, 
                  4 : {"length": 4, "name":"voltage", "has_val":True},
                  5 : {"length": 4, "name":"temperature", "has_val":True} }
                     
    command_types = {"ping": {"ID": 2}, 
                     "getvoltage": {"ID": 5}, 
                     "gettemp": {"ID": 4}, 
                     "blink": {"ID": 1}}

    max_addr = 127


    def __init__(self, port):
        # An 0.1s timeout
        self.ser = serial.Serial(port, 19200, timeout=0.1)
#        self.ser = serial.Serial(port, 38400, timeout=0.1)

    def calc_checksum(self, data):
        chksum = 0
        for b in data:
            chksum += b
        chksum &= 0x7F
        return chksum

    def send_command(self, addr, cmd):
        addr &= 0x7F;
        chksum = self.calc_checksum([addr,cmd]);
        cmd |= 0x80; 
        tosend = struct.pack("BBB", cmd, addr, chksum)
        print addr
        print cmd
        print chksum
        self.ser.write(tosend)

    def recv_data(self):
        # Read 1 byte from the serial port
        # Wait until its a byte with its first bit set

#        print 'Receiving data'
        while True:
            byte = self.ser.read()
            if len(byte) != 1:
                return None
            data_type = ord(byte[0])
            if data_type & 0x80 != 0:
                data_type &= 0x7F
                break

        # Length of the packet is based on the command type
        if data_type not in BMS.data_types:
            print "Got an invalid data packet type"
            return None

        rest = self.ser.read(BMS.data_types[data_type]["length"])
        if len(rest) != BMS.data_types[data_type]["length"]:
            print "BMS received the wrong number of bytes -- timeout?"
            return None

        data = map(ord, byte + rest)
        for b in data[1:]:
            if b & 0x80 != 0:
                print "Got erroneous start bit"
                return None

#        print "Got data: " 
#        print data
        if self.calc_checksum(data[0:-1]) != data[-1]:
            return None

        return data[0:-1]

    def decode_data(self, data):
        if len(data) <= 0:
            return None

        data_type = data[0] & 0x7F
        if data_type not in BMS.data_types:
            print "BMS decode: Got an invalid data type -- shouldn't get to here"
            return None

        if len(data) != BMS.data_types[data_type]["length"]:
            print "BMS decode: Packet length was wrong -- shouldn't get to here"
            return None

        # All packets have the data type as the first byte
        # and the address as the second byte

        packet_return = {}
        packet_return["type"] = BMS.data_types[data_type]["name"]
        packet_return["addr"] = data[1] & 0x7F
        
        if BMS.data_types[data_type]["has_val"]:
            value = data[2] << 7 | data[3]
            packet_return["value"] = value

#        print "Received a %s packet from %d" % (packet_return["type"], packet_return["addr"])
#        if "value" in packet_return: 
#            print "Its value was: %d" % packet_return["value"]

        return packet_return

    def get_ping(self, addr): 
        self.send_command(addr, BMS.command_types["ping"]["ID"])
        
        data = self.recv_data()
        if data == None:
            return False
        else:
            decoded = self.decode_data(data)
            if decoded["type"] == "ping" and decoded["addr"] == addr:
                return True
            else:
                return False

    def get_voltage(self, addr):
        self.send_command(addr, BMS.command_types["getvoltage"]["ID"])

        data = self.recv_data()
        if data != None:
            decoded = self.decode_data(data)
            if decoded["type"] == "voltage":
                if decoded["addr"] == addr:
                    return decoded["value"]                
        return None
                    
    def get_temperature(self, addr):
        self.send_command(addr, BMS.command_types["gettemp"]["ID"])

        data = self.recv_data()
        if data != None:
            decoded = self.decode_data(data)
            if decoded["type"] == "temperature":
                if decoded["addr"] == addr:
                    return decoded["value"]                
        return None
        
    def send_blink(self, addr):
        self.send_command(addr, BMS.command_types["blink"]["ID"])

    def scan_bus(self):
        valid_addr = []
        for i in range(0,BMS.max_addr):
            if self.get_ping(i):
                valid_addr.append(i)
        return valid_addr
