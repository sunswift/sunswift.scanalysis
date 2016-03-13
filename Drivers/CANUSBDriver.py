import gobject
import gtk

import Can
import Driver 
import socket
import thread
import sys
import Configurator
import struct
import serial
import time
import sqlite3
from datetime import datetime

# RX Buffer Length
RX_BUF_LEN=216

# Packet Start indicating string aka delimitator
PCKT_DELIM="UNSW"
PCKT_DELIM_LEN = 4

# packet received over serial connection and structure
PCKT_LEN=18
RX_DEL_LSB_INDEX  = 0
RX_DEL_MSB_INDEX  = 3
RX_ID_LSB_INDEX   = 4
RX_ID_MSB_INDEX   = 7
RX_DATA_LSB_INDEX = 8
RX_DATA_MSB_INDEX =15
RX_LEN_INDEX      =16
RX_CHKSUM_INDEX   =17

class CANUSBDriver(Driver.Driver, Can.Interface):
    # CAN packet information
    PRI_OFFSET = 26
    TYPE_OFFSET = 18
    ADDR_OFFSET = 10
    SPECIFICS_OFFSET = 0
 
    # Commit after every 100 packets
    PCKTS_PER_REPEAT = 100
    
    conn = 0
    sqlite_db_name = ""         
    sqlite_db = ""
	
    def __init__(self, sa, config, name="CANUSB"):

        #super class constructors
        Can.Interface.__init__(self)
        Driver.Driver.__init__(self, sa, config, name=name)

        #Define default port to read serial data, if nothing in scanalysis.cfg
        if "port" not in config:
            config["port"] = "/dev/ttyUSB1"

        #Define queue for writing packets sqlite and can packet parsing
        self.pkt_queue_lock = thread.allocate_lock()
        self.pkt_queue = []

        gobject.timeout_add(100, self.poll)

        #new thread for reading can data
        self.worker_thread = thread.start_new_thread(self.worker, () )

        self.active = False

        # Create sqlite db name and table name with today's date
        self.sqlite_db_name = 'can_sqlite'            
        self.sqlite_db = self.sqlite_db_name + '.sqb'
        self.sqlite_tablename = self.sqlite_db_name + "_" + \
          str(datetime.now().date()).replace("-","_")
        self.sa.console.write("Creating sqlite db: %s" % self.sqlite_tablename)
        
        # Initiate sqlite conn & cursor, to create sql queries 
        self.conn = sqlite3.connect(self.sqlite_db, check_same_thread = False)
        c = self.conn.cursor()
       
        # Create table
        try:
            self.sa.console.write("Creating table: " + self.sqlite_tablename)
            c.execute('''CREATE TABLE ''' + self.sqlite_tablename + 
            ''' (packet_number INTEGER, 
                 priority INTEGER, 
                 message_type INTEGER, 
                 source_address INTEGER, 
                 specifics INTEGER, 
                 value INTEGER, 
                 scandal_timestamp INTEGER,
                 ciel_timestamp INTEGER)''')   
        
        # Operational Error occurs when a table already exists in db.
        except sqlite3.OperationalError:
            self.sa.console.write(self.sqlite_tablename + " already exists in " + self.sqlite_db_name + ".")
        
    def get_active(self):
        Can.Interface.is_active(self)
        return self.active
        
    def worker(self):
        while self.running:
            # Connect to serial port to read serial data
            try: 
                self.ser = serial.Serial(self.config["port"], 115200)
                self.sa.console.write("Set up serial port...")
                self.ser.write("rrr")
                self.active = True    
                break

            # If error as right port may not be chosen, inform user
            except:  
                self.sa.console.write("Could not open serial port -- %s, retrying" % self.config["port"],\
                                          mod=self)                
                time.sleep(1)
              
        #Counter Variables        
        self.num_commits=0       #Counts number of commits to sqlite db
        self.num_packets_ctd = 0 #Counts number of packets committed to sqlite
        self.num_packets_queued=0 #Number of packets queued to wr to sqlite
        self.current_char_index=0 #Index of last char read from serialdata
 
        #Storage Lists
        self.packet=[]           #Stores exact copy of packet (incl delimiter)
        self.serialdata=[]       #data stream read from the serial port

        #Flag Variables
        self.packet_mode=0 #When delim recvd, start stor data to packet list.

        while self.running:        
            # Read data from serial port
            self.serialdata  = self.ser.read(RX_BUF_LEN) 

            #debug
            #prints all serial data that was read
            #for d in self.serialdata:
            #    print("%d " %ord(d)),
            #print("")
                
            # Read each serial data char...
            self.current_char_index=-1;
            for c in self.serialdata:               
                self.current_char_index = self.current_char_index + 1

                if(len(self.packet) < PCKT_LEN):                   

                    # If delimiter received...
                    if(self.serialdata[self.current_char_index-PCKT_DELIM_LEN+1 : \
                        self.current_char_index+1] == PCKT_DELIM):

                        #New packet before previous packet finished-drop prev
                        if(len(self.packet) > 0):                            
                            print("SP Err:"),
                            for d in self.packet:
                                print("%d " %ord(d)),
                            print("")
                        
                        #Packet mode - start capturing packet
                        self.packet=[]                      
                        self.packet_mode=1                
                        
                        # Copy delimiter into the packet - to keep exact copy
                        for ci in range(0, PCKT_DELIM_LEN-1): 
                            self.packet.append(PCKT_DELIM[ci])
                    
                    # If a delimiter was received, only then record packet 
                    if(self.packet_mode == 1):
                        self.packet.append(c)                   
                
                # Recorded packet length sufficient, time to write to sqlite...
                if(len(self.packet) >= PCKT_LEN):
                
                    #Check if there is data in the packet i.e. data length>0
                    if(ord(self.packet[RX_LEN_INDEX]) > 0):                         

                        # Calc checksum.
                        chksum=0 
                        for i in range(RX_ID_LSB_INDEX, RX_LEN_INDEX+1):
                            chksum=chksum+ord(self.packet[i])
                            if chksum > 255: 
                                chksum-=256
                    
                        # If chksm ok, calc id,data & queue to wr to sqlite
                        if chksum == ord(self.packet[RX_CHKSUM_INDEX]): 

                            #calc id
                            id=0
                            for i in range(RX_ID_LSB_INDEX, RX_ID_MSB_INDEX+1):
                                id= id | ord(self.packet[i]) << 8*(RX_ID_MSB_INDEX-i)                            

                            #calc data
                            length=ord(self.packet[RX_LEN_INDEX])
                            data_as_str = self.packet[RX_DATA_LSB_INDEX:RX_DATA_MSB_INDEX+1]
                            data=[] 
                            for ch in data_as_str:
                                data.append(ord(ch))                     

                            #queue to sqlite-recvd time set on init Can.packet
                            self.pkt_queue_lock.acquire()                       
                            self.pkt_queue.append( Can.Packet(id,data) )
                            self.pkt_queue_lock.release()                                    
                            self.num_packets_queued=self.num_packets_queued+1 
                            value_to_debug = data[3] <<  0 | \
                                data[2] <<  8 | \
                                data[1] << 16 | \
                                data[0] << 24                                               
               
                            #print number of packets queued                            
                            #print("%d#%d" %(self.num_packets_queued, value_to_debug) )

                            #--debug info--
                            #print("pss: "),
                            #for d in self.packet:
                            #    print("%d " %ord(d)),
                            #print("")
                         
                        else:

                            #checksum = cks
                            #calc cks & cks recvd in pkt mismatch - pkt corrupt
                            print("CkSm Err: r%d vs c%d" %(ord(self.packet[RX_CHKSUM_INDEX]), chksum))
                            for d in self.packet:
                               print("%d " %ord(d)),
                            print("")                           

                    #Packet delivered... wait for next delim
                    self.packet_mode=0                     
                    self.packet = []
                
    def poll(self):
        #Lock pkt queue from being changed by other threads
        self.pkt_queue_lock.acquire()
        
        while len(self.pkt_queue) > 0:

            #Obtain packet to write to sqlite and other threads
            pkt = self.pkt_queue.pop(0)
            self.deliver(pkt)
            
            self.num_packets_ctd=self.num_packets_ctd+1

            #Get values for sqlite fields
            packet_number = self.num_packets_ctd
            priority = pkt.id >> self.PRI_OFFSET & 0x07
            msg_type = pkt.id >> self.TYPE_OFFSET & 0xFF
            source_addr = pkt.id >> self.ADDR_OFFSET & 0xFF
            specifics = pkt.id >> self.SPECIFICS_OFFSET & 0x03FF
            value = pkt.data[3] <<  0 | \
                    pkt.data[2] <<  8 | \
                    pkt.data[1] << 16 | \
                    pkt.data[0] << 24                                   
            
            #Timestamp when the data was generated
            scandal_timestamp = pkt.data[7] <<  0 | \
                                pkt.data[6] <<  8 | \
                                pkt.data[5] << 16 | \
                                pkt.data[4] << 24       

            #Epoch Time - Time when data was put in queue for sqlite-see above
            ciel_timestamp = pkt.recvd

            #Write all values to db - values don't appear until committed
            self.conn.execute("INSERT INTO " + self.sqlite_tablename + " VALUES (%d, %d, %d, %d, %d, %d, %d, %d)" \
             % (packet_number, priority, msg_type, source_addr, specifics, value, scandal_timestamp, ciel_timestamp))

            #Commit after PCKTS_PER_REPEAT packets                                          
            if (self.num_packets_ctd%self.PCKTS_PER_REPEAT==0) :
           	self.conn.commit()                     
           	self.num_commits=self.num_commits+1
           	print("ctd. %d00" % self.num_commits)

        # Release pkt queue to allow changes from other threads
        self.pkt_queue_lock.release()

        return 1

    def send(self, pkt):
        if self.is_active() is not True:
            return

        data = pkt.get_data()
        id = pkt.get_id()

        bytes = [(id >> 24) & 0xFF, \
                     (id >> 16) & 0xFF, \
                     (id >> 8) & 0xFF, \
                     (id >> 0) & 0xFF]
        bytes = bytes + data
        bytes = bytes + range(0,(8-len(data))) + [len(data)]
        #print bytes
        checksum = 0
        for byte in bytes:
            checksum += byte
            if checksum > 255:
                checksum -= 256

        bytes = bytes + [checksum]

        tosend = struct.pack("B", ord("C"))

        for byte in bytes:
            if byte == ord('q') or \
                    byte == ord('r') or\
                    byte == ord('C') or \
                    byte == ord('\\'):
                tosend += "\\"
            tosend += struct.pack("B", byte)

        tosend += "r"
        self.ser.write(tosend)

    def configure(self):
        widg = Driver.Driver.configure(self)
        
        w = gtk.VBox()
        widg.pack_start(w)

        e = Configurator.TextConfig("port", self.config, "Port")
        w.pack_start(e, expand=False)

        return widg

    def stop(self):
        self.running = False

# Register our driver with the driver module's module factory
Driver.modfac.add_type("CANUSB", CANUSBDriver)
