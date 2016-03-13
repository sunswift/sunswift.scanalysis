# Sam May 09
#
# General command interface to a Fluke Hydra data logger.
#
# Written for Sunswift 4
#

import serial
import datetime

# let's be disciplined here
class FlukeNoDataException(Exception):
    """Raised when a query command sent to a Fluke returns a NODATA
    message"""
    def __init__(self,command):
        self.command = command
    def __str__(self):
        return "The Fluke command '%s' returned NODATA status" % self.command

class FlukeError(Exception):
    """Raised when a command sent to a Fluke returns an ERROR message"""
    def __init__(self,command,result):
        self.command = command
        self.result = result
    def __str__(self):
        return "The Fluke command '%s' returned ERROR status '%s'" % (self.command,self.result)

# wrapper around the fluke serial command list
class Fluke():
    """A low level interface to a Fluke Hydra data logger. Initialize with the
    serial port the fluke is connected to"""
    # some constants
    
    # status codes
    NODATA  = "!>"
    ERROR   = "?>"
    SUCCESS = "=>"

    # allowed measurement rates
    SLOW_RATE = 0
    FAST_RATE = 1

    FUNCTIONS = {"Off":"OFF", "DC Voltage":"VDC", "AC Voltage":"VAC",
                 "Frequency":"FREQ", "Resistance":"OHMS", "Temperature":"TEMP"}
    VOLTAGE_RANGES = {"Auto":"AUTO", "300mV":"1", "3V":"2", "30V":"3",
                      "150/300V":"4"}
    RESISTANCE_RANGES = {"Auto":"AUTO", "300R":"1", "3K":"2", "30K":"3",
                         "300K":"4", "3M":"5", "10M":"6"}
    FREQUENCY_RANGES = {"Auto":"AUTO", "900Hz":"1", "9kHz":"2", "90kHz":"3",
                        "900kHz":"4","1MHz":"5"}
    # I have no idea what the difference is, or why 'PT' is special and needs
    # a range. So i'm not going to treat it specially.
    THERMOCOUPLE_TYPES = {"J Thermocouple":"J", "K Thermocouple":"K",
                          "E Thermocouple":"E", "T Thermocouple":"T",
                          "N Thermocouple":"N", "R Thermocouple":"R",
                          "S Thermocouple":"S", "B Thermocouple":"B",
                          "C Thermocouple":"C", "PT Thermocouple":"PT"}
    # 'Off' doesn't have a range, so remove it from FUNCTIONS.keys
    RANGES = { "DC Voltage":VOLTAGE_RANGES,"AC Voltage":VOLTAGE_RANGES,
               "Frequency":FREQUENCY_RANGES,"Resistance":RESISTANCE_RANGES,
               "Temperature":THERMOCOUPLE_TYPES }

    def __init__(self,serial_port):
        # open serial port object. PySerial should do a nice job of
        # tidying up all the low level things we had to worry about in C
        self.serial_link = serial.Serial(
            port=serial_port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        # send plain carriage return and newline: clear device input buffer
        self.send_command("")
        # turn off echoing
        self.send_command("ECHO 0")
    
    # All these functions simply abstract the communication protocol
    def send_command(self,command):
        """Send a command string to the Fluke, and raise an exception if the
        returned status code is not a success code."""
        self.serial_link.write("%s\r\n" % command)
        result = self.serial_link.readline().rstrip()
        if result != self.SUCCESS:
            raise FlukeError(command,result)

    def send_query(self,query):
        """Send a query string to the Fluke, and return the result of the query.
        If the status code is not 'success', the relevant NODATA or ERROR
        exception is raised."""
        self.serial_link.write("%s\r\n" % query)
        # if unsuccessful returns a status code.
        # if successful returns result, then SUCCESS status code
        
        line1 = self.serial_link.readline().rstrip()
        if line1 == self.NODATA:
            raise FlukeNoDataException(query)
        elif line1 == self.ERROR:
            raise FlukeError(query,line1 + " (on first line)")
        line2 = self.serial_link.readline().rstrip()
        if line2 != self.SUCCESS:
            raise FlukeError(query,line2 + " (on second line)")
        return line1

    def get_id (self):
        "Get the model identification string."
        return self.send_query('*IDN?')

    # scanning control
    def start_logging (self):
        """Clear the Fluke's memory, start printing to memory, and start
        scanning."""
        # this is a little bit magic, mybad.
        self.clear_log()
        self.send_command("PRINT 1")
        self.send_command("PRINT_TYPE 1,0")
        self.send_command("SCAN 1")
        
    def stop_logging(self):
        """Stop scanning and printing."""
        self.send_command("PRINT 0")
        self.send_command("SCAN 0")

    # monitoring control
    def start_monitoring(self,channel):
        """Start front panel monitoring of a given channel, specified by an
        integer between 1 and 20"""
        self.send_command("MON 1,%d" % channel)

    def stop_monitoring(self):
        """Stop front panel monitoring"""
        self.send_command("MON 0")

    # rate control. Choose one of Fluke.SLOW_RATE or Fluke.FAST_RATE
    def set_rate(self,rate):
        """Set the measurement rate to slow or fast mode. The argument should be
        one of Fluke.FAST_RATE or Fluke.SLOW_RATE. Fast mode is faster, but you
        loose a significant figure"""
        self.send_command("RATE %d" % rate)

    def get_rate(self):
        """Get the measurement rate. The return value is either Fluke.FAST_RATE
        or Fluke.SLOW_RATE."""
        return int(self.send_query("RATE?"))

    # channel configuration
    # NO CHECKING. you gotta get the right string
    # yourself, including function and range. No immediate solution
    # presented itself to to problem that different functions require
    # different arguments
    def get_function(self,channel):
        """Returns a string describing the function of the given channel. The
        format is '<function>,<range>,<other stuff dependent on function>'"""
        return self.send_query("FUNC? %d" % channel)

    def set_function(self,channel,function,range_="Auto",scaling=None,
                     terminals=2):
        """Set the function of a channel. The first argument is an integer
        specifying the channel. The second argument is a function in
        Fluke.FUNCTIONS. The optional arguments are a range out of
        Fluke.RANGES[function] (set to 'Auto' by default), a tuple of integers
        specifying the Mx+B scaling, and a value specifying 2 or 4 terminal
        measurement (only relevant for resistance and PT thermocouples)"""
        
        command = "FUNC %d,%s" % (channel, self.FUNCTIONS[function])
        if self.RANGES.has_key(function):
            command = command + "," + self.RANGES[function][range_]
        # resistance measurements and PT thermocouples need a terminals
        # argument, which is 2 or 4
        if function == "Resistance" or range_ == "PT Thermocouple":
            command = command + "," + str(terminals)
        self.send_command(command)
        if scaling is not None:
            scaling_data = (channel,scaling[0],scaling[1],scaling[2] + 4)
            self.send_command("SCALE_MB %d,%+f,%+f,%d" % scaling_data)
        
    
    # set measurement interval, in seconds
    def set_interval(self,interval):
        """Set the time between measurements, in seconds"""
        # format 'INTVL <hour>,<minute>,<second>'
        hours = interval/3600
        minutes = (interval % 3600) / 60
        seconds = interval % 60
        self.send_command("INTVL %d,%d,%d" % (hours,minutes,seconds))

    def get_interval(self):
        """Get the time between measurements, in seconds"""
        # format "<hour>,<minute>,<second>', reduce it to seconds
        # that sneaky Guido character went and depreciated 'map'
        nums = [int(i) for i in self.send_query("INTVL?").split(",")]
        return nums[0]*3600 + nums[1]*60 + nums[2]

    # helper function for timestamps
    def parse_fluke_date(self,fields):
        """Return a python datetime object from an array of integers
        representing hour, minute, second, month, day, and year"""
        #datetime.datetime(year, month, day, hour, minute, second...)
        #fluke returns "hours,minutes,seconds,month,day,year"
        return datetime.datetime(2000+fields[5],fields[3],fields[4],
                                 fields[0],fields[1],fields[2])		

    # set fluke date
    def set_datetime(self,dtime):
        """Set the onboard clock on the Fluke from a python datetime object"""
        self.send_command("DATE %d,%d,%d" % (dtime.month,
                                             dtime.day,
                                             dtime.year % 100))
        self.send_command("TIME %d,%d" % (dtime.hour, dtime.minute))

    def get_datetime(self):
        """Get the date and time from the Fluke onboard clock. Returns a python
        datetime object."""
        result = self.send_query("TIME_DATE?")
        return self.parse_fluke_date([int(i) for i in result.split(",")])

    # channel minimum and maximum values collected so far
    def get_min(self,channel):
        """Get the minimum value measured so far from a channel"""
        self.send_command("MIN? %d" % channel)

    def get_max(self,channel):
        """Get the maximum value measured so far from a channel"""
        self.send_command("MAX? %d" % channel)

    # get data off the thing
    def clear_log(self):
        """Clear the Fluke's onboard log of measurements."""
        self.send_command("LOG_CLR")
        
    def read_log(self):
        """Read a single measurement from the Fluke's onboard log. Will block
        and wait until data is available if a FlukeNoDataException is thrown."""
        # if at first you don't succeed, poll and poll again
        while True:
            try:
                line = self.send_query("LOG?")
                break
            except FlukeNoDataException:
                pass
            
        fields = line.split(",")
            
        # first five fields are date and time
        timestamp = self.parse_fluke_date([int(i) for i in fields[:6]])
        # the last three fields are IO line states and some sort of count, do
        # not want.
        # the rest is data
        data = [float(f) for f in fields[6:-3]]
        return data,timestamp
