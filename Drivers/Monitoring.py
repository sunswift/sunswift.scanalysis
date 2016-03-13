from ScandalWidgets import *

import Driver

import Graphing
import GraphingMPL

class Monitoring(Driver.Driver):
    def __init__(self, sa, config, name="Summary"):
        Driver.Driver.__init__(self, sa, config, name)


        # Add ourselves to the scanalysis notebook
        self.array_page = ArrayPage(sa)
        self.sa.add_notebook_page("Array", self.array_page)

        self.array_total_page = ArrayTotalPage(sa)
        self.sa.add_notebook_page("Array Total", self.array_total_page)

        self.battery_page = BatteryPage(sa)
        self.sa.add_notebook_page("Battery", self.battery_page)

        self.current_int_page = CurrentIntegratorPage(sa)
        self.sa.add_notebook_page("Current Int", self.current_int_page)


    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.array_page)


class ArrayPage(gtk.HBox):
    def __init__(self, sa):
        gtk.HBox.__init__(self)
        self.sa = sa

        class power_time_series(Graphing.SeriesTime):
            def __init__(self, sa, nodename, currentchan, voltagechan, **kwargs):
                Graphing.SeriesTime.__init__(self, sa, None, None, **kwargs)
                
                self.sa.store.register_for_channel(nodename, currentchan, self.deliverI)
                self.sa.store.register_for_channel(nodename, voltagechan, self.deliverV)
                
                self.last_I = None
                self.last_V = None


            def try_update(self):
                if self.last_I is None or self.last_V is None:
                    return

                # Because I'm lazy and don't want to interpolate, 
                # I'm just going to check if the two samples are < 10ms apart
                # Which should be the case for simultaneous samples coming from 
                # the same tracker. 
                if abs(self.last_I.get_time() - self.last_V.get_time()) < 0.01: 
                    timestamp = (self.last_I.get_time() + self.last_V.get_time()) / 2.0
                    value = self.last_I.get_value() * self.last_V.get_value()
                    self.deliver(Driver.Deliverable(value, timestamp=timestamp))

            def deliverI(self, pkt):
                if self.last_I is None:
                    self.last_I = pkt
                elif self.last_I.get_time() >= pkt.get_time():
                    return
                else:
                    self.last_I = pkt
                    self.try_update()

            def deliverV(self, pkt):
                if self.last_V is None:
                    self.last_V = pkt
                elif self.last_V.get_time() >= pkt.get_time():
                    return
                else:
                    self.last_V = pkt
                    self.try_update()

### MPPT power graph
        graph = GraphingMPL.Graph(self.sa, 
                                  xlabel="Time (s)", 
                                  ylabel="Power (W)",
                                  title="Maximum Power Point Tracker Power",
                                  maxupdate=1000)
       
	mppt1_series = power_time_series(self.sa, "MPPTNG 40", 
                                         "Input Current", 
                                         "Input Voltage",
                                         label="MPPT R40",
                                         maxtimediff=600.0, 
                                         format={"color":"blue"}) 

        mppt2_series = power_time_series(self.sa, "MPPTNG 41", 
                                         "Input Current", 
                                         "Input Voltage",
                                         label="MPPT F41", 
                                         maxtimediff=600.0, 
                                         format={"color":"green"}) 

        #mppt3_series = power_time_series(self.sa, "MPPT 3", 
        #                                 "Input Current", 
        #                                 "Input Voltage",
        #                                 label="MPPT 3", 
        #                                 maxtimediff=600.0, 
        #                                 format={"color":"red"}) 

        graph.add_series(mppt1_series)
        graph.add_series(mppt2_series)
        #graph.add_series(mppt3_series)
        self.add(graph.get_widget())


class ArrayTotalPage(gtk.HBox):
    def __init__(self, sa):
        gtk.HBox.__init__(self)
        self.sa = sa


### MPPT power graph
        graph = GraphingMPL.Graph(self.sa, 
                                  xlabel="Time (s)", 
                                  ylabel="Power (W)",
                                  title="Total Array Power Power",
                                  maxupdate=1000)
                                  
        power_series = Graphing.SeriesTime(self.sa, "Negsum", "Array Power", \
                                               label="Power", \
                                              maxtimediff=600.0, \
                                              format={"color":"blue"}) 
        graph.add_series(power_series)
        self.add(graph.get_widget())

        


class BatteryPage(gtk.HBox):
    def __init__(self, sa):
		gtk.HBox.__init__(self)
		self.sa = sa

### Values vs. Time
		graph = GraphingMPL.Graph(self.sa, 
                                  xlabel="Time (s)", 
                                  ylabel="Voltage (V)",
                                  title="Battery Analysis",
                                  maxupdate=5000)
		current_time_series = Graphing.SeriesTime(self.sa, "Current Integrator 50", "Current Linear", \
                                               label="Current", \
                                              maxtimediff=600.0, \
                                              format={"color":"blue"}) 
		voltage_time_series = Graphing.SeriesTime(self.sa, "Current Integrator 50", "Voltage", \
                                               label="Voltage", \
                                              maxtimediff=600.0, \
                                              format={"color":"red"}) 
		corrected_voltage_time_series = Graphing.SeriesTime(self.sa, "BatteryIntegrator", "Corrected Voltage", \
                                               label="Corrected Voltage", \
                                              maxtimediff=600.0, \
                                              format={"color":"green"}) 
										
		graph.add_axis(axis=(1,2), ylabel="Voltage")
		graph.add_series(current_time_series)
		graph.add_series(voltage_time_series, axis=(1,2))
		graph.add_series(corrected_voltage_time_series, axis=(1,2))
		self.add(graph.get_widget())


### Voltage vs. BSOC graph
		graph = GraphingMPL.Graph(self.sa, 
                                  xlabel="BSOC (Ah)", 
                                  ylabel="Voltage (V)",
                                  maxupdate=5000)
		voltage_bsoc_series = Graphing.SeriesXY(self.sa, "Current Integrator 50", "Current Int Linear", \
													"Current Integrator 50", "Voltage", \
                                               label="Voltage", \
                                              format={"color":"blue"}) 
		corrected_voltage_bsoc_series = Graphing.SeriesXY(self.sa, "Current Integrator 50", "Current Int Linear", \
													"BatteryIntegrator", "Corrected Voltage", \
													label="Corrected Voltage", \
													format={"color":"red"}) 
		graph.add_series(voltage_bsoc_series)
		graph.add_series(corrected_voltage_bsoc_series)
		self.add(graph.get_widget())

		


class CurrentIntegratorPage(gtk.HBox):
    def __init__(self, sa):
        gtk.HBox.__init__(self)
        self.sa = sa

### Values vs. Time
        class negated_timeseries(Graphing.SeriesTime):
            def deliver(self, packet):
                thevalue = -packet.get_value()
                thetime = packet.get_time()
                newpkt = Driver.Deliverable(thevalue, timestamp=thetime)
                Graphing.SeriesTime.deliver(self, newpkt)

        graph = GraphingMPL.Graph(self.sa, 
                                  xlabel="Time (s)", 
                                  ylabel="Voltage (V)",
                                  title="Battery Analysis",
                                  maxupdate=5000)
        currentint_current_time_series = Graphing.SeriesTime(self.sa, "Current Integrator 50", "Current", \
                                               label="Current Integrator Current", \
                                              maxtimediff=600.0, \
                                              format={"color":"blue"}) 
        currentint_linear_current_time_series = Graphing.SeriesTime(self.sa, "Current Integrator 50", "Current Linear", \
                                               label="Current Integrator Current Linear", \
                                              maxtimediff=600.0, \
                                              format={"color":"green"}) 
        negsum_current_time_series = negated_timeseries(self.sa, "Negsum", "Battery Current", \
                                               label="Negsum Current", \
                                              maxtimediff=600.0, \
                                              format={"color":"red"}) 
										
        graph.add_series(currentint_current_time_series)
        graph.add_series(currentint_linear_current_time_series)
        graph.add_series(negsum_current_time_series)
        self.add(graph.get_widget())


# Register our driver with the driver module's module factory
Driver.modfac.add_type("Monitoring", Monitoring)
