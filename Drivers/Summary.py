from ScandalWidgets import *

import Driver

import Graphing
import GraphingMPL

class Summary(Driver.Driver):
    def __init__(self, sa, config, name="Summary"):
        Driver.Driver.__init__(self, sa, config, name)

        self.page1 = page = gtk.HBox()

        col1 = gtk.VBox()
        page.pack_start(col1, expand=False)
        col2 = gtk.VPaned()
        page.pack_start(col2)

        batsum = BatterySummary(sa)
        col1.pack_start(batsum, expand=False)

        motsum = MotorSummary(sa)
        col1.pack_start(motsum, expand=False)

        arraysum = ArraySummary(sa)
        col1.pack_start(arraysum, expand=False)


### Speed Graph
        graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Speed (km/h)",
                                  title="Solar car speed",
                                  maxupdate=1000)
        speed_series = Graphing.SeriesTime(self.sa, "SteeringWheel", "Speed", \
                                               label="Speed", \
                                              maxtimediff=1800.0, \
                                              format={"color":"black"}) 
        graph.add_series(speed_series)
        col2.pack1(graph.get_widget(), resize=True, shrink=True)



### Bus V Graph
        graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Current (A)",\
                                  title="Bus Voltage and Currents",
                                  maxupdate=1000)
        graph.add_axis(axis=(1,2), ylabel="Bus Voltage (V)")

        busv_series = Graphing.SeriesTime(self.sa, "Negsum", "Bus Voltage", 
                                          label="Bus Voltage", 
                                          maxtimediff=1800.0, 
                                          format={"color":"magenta", "lw":2}) 

        graph.add_series(busv_series, axis=(1,2))


### Current Graph

        batI_series = Graphing.SeriesTime(self.sa, "Negsum", "Battery Current",
                                          label="Battery Current", 
                                          maxtimediff=1800.0, 
                                          format={"color":"red"}) 
        arrayI_series = Graphing.SeriesTime(self.sa, "Negsum", "Array Current",
                                            label="Array Current",
                                            maxtimediff=1800.0,
                                            format={"color":"green"}) 
        motorI_series = Graphing.SeriesTime(self.sa, "Negsum", "Motor Current",
                                            label="Motor Current",
                                            maxtimediff=1800.0,
                                            format={"color":"blue"}) 

        graph.add_series(batI_series)
        graph.add_series(arrayI_series)
        graph.add_series(motorI_series)

        col2.pack2(graph.get_widget(), resize=True, shrink=True)


        # Add a second page, with extra stuff. 
        self.page2 = page = gtk.HBox()

        col1 = gtk.VBox()
        page.pack_start(col1)
        col2 = gtk.VBox()
        page.pack_start(col2)



### Temp Graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Temperature (degrees)",\
                                  maxupdate=500)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, "SteeringWheel", "Heatsink Temp", \
                                         label="MC Heatsink Temp", \
                                         maxtimediff=1800.0, \
                                         format={"color":"red"}) 
        graph.add_series(series)

        series = Graphing.SeriesTime(self.sa, "SteeringWheel", "Motor Temp", \
                                         label="Motor Temp", \
                                         maxtimediff=1800.0, \
                                         format={"color":"green"}) 
        graph.add_series(series)

#        series = Graphing.SeriesTime(self.sa, "Motor Controller", "Cap Temp", \
#                                         label="MC Capacitor Temp", \
#                                         maxtimediff=1800.0, \
#                                         format={"color":"blue"}) 
#        graph.add_series(series)


### Altitude
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Altitude (m)",\
                                  maxupdate=500)
        col2.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, "GPS", "Altitude", \
                                         label="Solar car altitude", \
                                         maxtimediff=1800.0, \
                                         format={"color":"red"}) 
        graph.add_series(series)

        series = Graphing.SeriesTime(self.sa, "ControlGPS", "Altitude", \
                                         label="Control car altitude", \
                                         maxtimediff=1800.0, \
                                         format={"color":"blue"}) 
        graph.add_series(series)

        series = Graphing.SeriesTime(self.sa, "CourseProfile", "Altitude", \
                                         label="Profile altitude", \
                                         maxtimediff=1800.0, \
                                         format={"color":"magenta"}) 
        graph.add_series(series)

        graph.add_axis(axis=(1,2), ylabel="Gradient")
        series = Graphing.SeriesTime(self.sa, "CourseProfile", "Gradient", \
                                         label="Solar car gradient", \
                                         maxtimediff=1800.0, \
                                         format={"color":"green"}) 
        graph.add_series(series, axis=(1,2))


### Packet rate graph
	graph = GraphingMPL.Graph(self.sa, \
                                      xlabel="Time (s)", \
                                      ylabel="Packet Rate (hz)",\
                                  maxupdate=500)
        col1.pack_start(graph.get_widget())
        series = Graphing.SeriesTime(self.sa, "Messages", "Packet Rate", \
                                         label="Packet Rate", \
                                         maxtimediff=1800.0, \
                                         format={"color":"red"}) 
        graph.add_series(series)


        # Add ourselves to the scanalysis notebook
        self.sa.add_notebook_page(self.get_display_name() + " 1", self.page1)
        self.sa.add_notebook_page(self.get_display_name() + " 2", self.page2)

    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page1)
        self.sa.remove_notebook_page(self.page2)


class CurrentIntIndicator(NewListener, gtk.Label):
    def __init__(self, store, nodename, channame):
        NewListener.__init__(self, store, nodename, channame)
        gtk.Label.__init__(self, str="Current Int")

    def deliver(self, pkt):
        value = pkt.get_value()
        value -= 38.0
        value = 35.0 - value
        newpkt = Driver.Deliverable(value, timestamp=pkt.get_time())

        NewListener.deliver(self, newpkt)

        self.set_text("%f" % self.get_value())

class BatterySummary(gtk.Frame):
    def __init__(self, sa):
        gtk.Frame.__init__(self, label="Battery Summary")
        
        vbox = gtk.VBox()
        self.add(vbox)
    
        batV = LabelIndicator(sa.store, "Negsum", "Bus Voltage", "Bus Voltage", units="V")
        vbox.pack_start(batV)

        batI = LabelIndicator(sa.store, "Negsum", "Battery Current", "Battery Current", units="A")
        vbox.pack_start(batI)

        batP = LabelIndicator(sa.store, "Negsum", "Battery Power", "Battery Power", units="W")
        vbox.pack_start(batP)

        currentInt = CurrentIntIndicator(sa.store, "Current Integrator 10", "Current Int Linear")
        vbox.pack_start(currentInt)



class MCLoopStatusIndicator(NewListener, gtk.Label):
    def __init__(self, store, nodename, channame):
        NewListener.__init__(self, store, nodename, channame)
        gtk.Label.__init__(self, str="status")

    # Ugly!! Get rid of magic numbers. 
    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
        if self.last_packet.get_raw_value() & (1 << 0):
            string = "Bridge PWM"
        elif self.last_packet.get_raw_value() & (1 << 1):
            string = "Motor Current"
        elif self.last_packet.get_raw_value() & (1 << 2):
            string = "Velocity"
        elif self.last_packet.get_raw_value() & (1 << 3):
            string = "Bus Current"
        elif self.last_packet.get_raw_value() & (1 << 4):
            string = "Bus Voltage Upper Limit"
        elif self.last_packet.get_raw_value() & (1 << 5):
            string = "Bus Voltage Lower Limit"
        elif self.last_packet.get_raw_value() & (1 << 6):
            string = "Heatsink Temp"
        elif self.last_packet.get_raw_value() == 0x00:
            string = "None"
        else:
            
            string = "Unknown: 0x%04x" % (self.last_packet.get_raw_value() & 0xFFFF)
        self.set_text(string)

class MotorSummary(gtk.Frame):
    def __init__(self, sa):
        gtk.Frame.__init__(self, label="Motor Summary")
        
        vbox = gtk.VBox()
        self.add(vbox)
    
        widg = LabelIndicator(sa.store, "SteeringWheel", "Speed", "Speed", units="km/h")
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "SteeringWheel", "Velocity Setpoint", "Set Speed", units="km/h")
        vbox.pack_start(widg)

        widg = gtk.HSeparator()
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "SteeringWheel", "Current A", "Current A", units="A")
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "SteeringWheel", "Current B", "Current B", units="A")
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "SteeringWheel", "Current Setpoint", "Set Current", units="A")
        vbox.pack_start(widg)

        widg = gtk.HSeparator()
        vbox.pack_start(widg)

        batP = LabelIndicator(sa.store, "Negsum", "Motor Power", "Power", units="W")
        vbox.pack_start(batP)

        widg = gtk.HSeparator()
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "SteeringWheel", "Motor Temp", "Motor Temp", units="deg")
        vbox.pack_start(widg)
        
        widg = LabelIndicator(sa.store, "SteeringWheel", "Heatsink Temp", "Heatsink Temp", units="deg")
        vbox.pack_start(widg)

        widg = gtk.HSeparator()
        vbox.pack_start(widg)

        widg = MCLoopStatusIndicator(sa.store, "SteeringWheel", "Limits")
        hbox = gtk.HBox()
        label = gtk.Label(str="Limiting Loop")
        hbox.pack_start(label)
        hbox.pack_start(widg)
        vbox.pack_start(hbox)

        widg.set_justify(gtk.JUSTIFY_LEFT)
        widg.set_alignment(1.0, 0.5)
        widg.set_padding(4, 1)

        label.set_justify(gtk.JUSTIFY_RIGHT)
        label.set_alignment(0.0, 0.5)
        label.set_padding(4, 1)

class TrackerStatusIndicator(NewListener, gtk.Label):
    def __init__(self, store, nodename, channame):
        NewListener.__init__(self, store, nodename, channame)
        gtk.Label.__init__(self, str="status")

    # Ugly!! Get rid of magic numbers. 
    def deliver(self, pkt):
        NewListener.deliver(self, pkt)
        string = ""
        if self.last_packet.get_raw_value() & 0x01:
            string = string + "T"
        if self.last_packet.get_raw_value() & 0x02: 
            string = "I" + string
        if self.last_packet.get_raw_value() & 0x04: 
            string = "O" + string
        self.set_text(string)

class ArraySummary(gtk.Frame):
    def __init__(self, sa):
        gtk.Frame.__init__(self, label="Array Summary")
        
        vbox = gtk.VBox()
        self.add(vbox)
    
        widg = LabelIndicator(sa.store, "Negsum", "Array Power", "Power", units="W")
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "Negsum", "Array Power", "Corrected Power", units="W")
        vbox.pack_start(widg)

        widg = LabelIndicator(sa.store, "Negsum", "Array Power", "Suns", units="W")
        vbox.pack_start(widg)

        widg = gtk.Frame()
        vbox.pack_start(widg)

        trackers = gtk.Table(rows=8, columns=6, homogeneous=False)
        widg.add(trackers)

        widg = gtk.Label(str=" In Voltage ")
        trackers.attach(widg, 2, 3, 0, 1) # Second column title

        widg = gtk.Label(str=" In Current ")
        trackers.attach(widg, 3, 4, 0, 1) # Second column title

        widg = gtk.Label(str=" In Power ")
        trackers.attach(widg, 4, 5, 0, 1) # Second column title

        widg = gtk.Label(str=" HS Temp ")
        trackers.attach(widg, 5, 6, 0, 1) # Second column title

        widg = gtk.Label(str=" Status ")
        trackers.attach(widg, 6, 7, 0, 1) # Second column title

        widg = gtk.HSeparator()
        trackers.attach(widg, 0,7,1,2)

        widg = gtk.VSeparator()
        trackers.attach(widg, 1,2,0,8)

        def attach_tracker(row, num):
            # attach attaches the top edge to row, the bottom edge to 
            # row+1, the left to col, and the left to col+1

            widg = gtk.Label(str="MPPT %s"%num)
            trackers.attach(widg, 0, 1, row, row+1)

            widg = LabelIndicator(sa.store, "MPPT %s"%num, "Input Voltage", units="V")
            trackers.attach(widg, 2, 3, row, row+1)

            widg = LabelIndicator(sa.store, "MPPT %s"%num, "Input Current", units="A")
            trackers.attach(widg, 3, 4, row, row+1)

            widg = ProductLabelIndicator(sa.store, "MPPT %s"%num, "Input Voltage",\
                                      "MPPT %s"%num, "Input Current", units="W")
            trackers.attach(widg, 4, 5, row, row+1)

            widg = LabelIndicator(sa.store, "MPPT %s"%num, "Heatsink Temp", units="deg")
            trackers.attach(widg, 5, 6, row, row+1)

            widg = TrackerStatusIndicator(sa.store, "MPPT %s"%num, "Status")
            trackers.attach(widg, 6, 7, row, row+1)

        for i in range(3):
            attach_tracker(i+2, i+1)
        

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Summary", Summary)
