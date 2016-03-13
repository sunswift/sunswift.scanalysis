import struct
import serial
import time

class TDK:
    data_types = {2 : {"length": 2, "name":"ping", "has_val":False}, 
                  4 : {"length": 4, "name":"voltage", "has_val":True},
                  5 : {"length": 4, "name":"current", "has_val":True} }                   

    def __init__(self, port, sa):
        # An 0.1s timeout
	
	self.sa = sa

	self.sa.console.write("TDK starting, port: %s\n" % port)

        self.ser = serial.Serial(port, 9600)

	if not self.ser.isOpen:
		self.sa.console.write("serial port not open")
	else:
		self.sa.console.write("serial port open")

	try:
		self.ser.open()
		self.sa.console.write("port opened successfully")
	except SerialException:
		self.sa.console.write("caught serialexception when trying to open")

	self.ser.write("ADR 6\r")
	ok = self.ser.read(3)
	if ok == "OK\r":
		self.sa.console.write("adr success")

	self.ser.write("PV 05\r")

	ok = self.ser.read(3)
	if ok == "OK\r":
		self.sa.console.write("voltage changed successfully")
	


    def get_voltage(self):
	self.ser.write("MV?\r")
	data = self.ser.read(7)
	float_data = float(data)
        return float_data
   
    def set_voltage(self,voltage):
	self.ser.write("PV %f\r" %voltage)
	ok = self.ser.read(3)
	if ok == "OK\r":
		self.sa.console.write("voltage changed successfully!")
	return

    def get_current(self):
	self.ser.write("MC?\r")
	data = self.ser.read(7)
	float_data = float(data)
        return float_data

