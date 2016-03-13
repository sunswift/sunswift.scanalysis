from ScandalWidgets import *
import gtk
import Driver
import Configurator
import thread
import os
import time
from subprocess import Popen

class LiveView(Driver.Driver):
    def __init__(self, sa, config, name="LiveView"):
        Driver.Driver.__init__(self, sa, config, name)

        if "video" not in self.config:
            self.config["video"] = "/dev/video"

        if "scploc" not in self.config:
            self.config["scploc"] = "www.cse.unsw.edu.au:/home/sunswift/public_html/"

        if "imgdir" not in self.config:
            self.config["imgdir"] = "misc/liveview/imgdir"

        if "inputhtml" not in self.config:
            self.config["inputhtml"] = "misc/liveview/input"

        if "outputhtml" not in self.config:
            self.config["outputhtml"] = "misc/liveview"
            
        if "graphdir" not in self.config:
            self.config["graphdir"] = "misc/liveview/graphdir"
            
        # Get ready for graphs
        self.init_graphs()

        # Local channel DB
        self.chans = {}
        self.chans_pkt = {}
        self.chans_lock = thread.allocate_lock()
        self.latest_webcam_image = "noneyet.jpg"

        # capture command
        self.capturecmd = None
        
        # Get ourselves registered for everything
        self.sa.store.register_for_updates(self.update_func)
        for source in self.sa.store:
            self.sa.store[source].register_for_updates(self.update_func)

        # Register for all the channels
        for source in self.sa.store:
            for channel in self.sa.store[source]:
                chan = self.sa.store[source][channel]
                self.update_func(chan)
        

        # Create the interface
        self.page = page = gtk.HBox()

        col1 = gtk.VBox()
        page.pack_start(col1)
	col2 = gtk.VBox()
	page.pack_start(col2)

        # Add the image
        frame = gtk.Frame(label="Webcam Feed")
        col1.pack_start(frame, expand=False)
        image = gtk.Image()
        frame.add(image)
        image.set_from_file(self.latest_webcam_image)
        self.image = image

        # Add ourselves to the scanalysis notebook
        self.sa.add_notebook_page(self.get_display_name(), page)

        # Start the worker thread
        self.WS_tread = thread.start_new_thread(self.worker, ())

    def update_func(self, elem):
        if isinstance(elem, Driver.Channel):
            channame = elem.get_name()
            nodename = elem.get_source().get_name()
            key = (nodename, channame)
            if key not in self.chans:
                elem.register_for_delivery(lambda pkt: self.deliver(key, pkt))

        if isinstance(elem, Driver.Source):
            elem.register_for_updates(self.update_func)

    def deliver(self, key, pkt ):
        value = pkt.get_value()

        # Check that this is the most up to date packet we have
        if key in self.chans_pkt:
            if self.chans_pkt[key].get_time() > pkt.get_time():
                return

        # Some extra-hacky fixups. 
        if key == ("Negsum", "Array Power"):
            value = value * -1.0
        elif key == ("GPS", "Latitude"):
            value = value / 60.0
        elif key == ("GPS", "Longitude"):
            value = value / 60.0
        elif key == ("ControlGPS", "Latitude"):
            value = value / 60.0
        elif key == ("ControlGPS", "Longitude"):
            value = value / 60.0

        self.chans_lock.acquire()
        self.chans[key] = value
        self.chans_pkt[key] = pkt

        # Note that the below function can take a long time, which may stall scanalysis
        (a, b) = key
        graphkey = a + "_" + b
        self.do_graphs_deliver(graphkey, value)
        self.chans_lock.release()

    def do_grab_video(self):
        # First, take a picture
        try:
            os.popen("mkdir -p " + self.config["imgdir"])

#            self.capturecmd = Popen("misc/uvccapture-0.5/uvccapture -d" + self.config["video"] + \
#                                        " -t1 -o" + self.config["imgdir"] + "/latest.jpg", shell=True)

            picname = "%f.jpg" % time.time()
            picpath = self.config["imgdir"] + "/" + picname 

            cmd = Popen("misc/uvccapture-0.5/uvccapture -d" + self.config["video"] + \
                            " -o" + picpath, shell=True)
            cmd.wait()

#            cmd = Popen("mv " + self.config["imgdir"] + "/latest.jpg " + picpath, shell=True)
#            cmd.wait()

            cmd = Popen("cp " + picpath + " " + self.config["outputhtml"] + \
                            "/imgdir/latest_webcam.jpg", shell=True)
            cmd.wait()

        except OSError, e:
            self.sa.console.write("Error executing frame grabber -- " + str(e), mod=self)
            return False
        
        latestpicpath = self.config["outputhtml"] + "/imgdir/latest_webcam.jpg"
        self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(latestpicpath).\
                                       scale_simple(320,240,gtk.gdk.INTERP_BILINEAR))
        self.image.show()

        self.latest_webcam_image = picname

        return True

    def init_graphs(self):
        os.popen("mkdir -p " + self.config["graphdir"])
        self.graph_file_name = self.config["graphdir"] + "/graphdata.csv"

        self.graph_data_store = {}
        self.graph_data_store["Time"] = []
        
        self.graph_data = file(self.graph_file_name, "a+")
        self.graph_data.seek(0, os.SEEK_SET)
        line = self.graph_data.readline()
        print line
        if line != '':
            line = line.rstrip("\n ")
            self.graph_labels = line.split(",")
            self.graph_data.seek(0, os.SEEK_END) # seek to the end, ready for new lines
        else:
            self.graph_labels = ["Time"]
            self.graph_data.write("Time\n")

        self.graph_data_store["Time"] = [time.time()]
        for label in self.graph_labels[1:]:
            self.graph_data_store[label] = []

    def do_graphs_deliver(self, key, value):
        def avg(x):
            if len(x) == 0:
                return 0.0
            else:
                return sum(x) / float(len(x))

        # If our graph period has run out, its time to write a line
        if self.graph_data_store["Time"][0] < time.time() - 5.0: 
            next_period_start = time.time()
            self.graph_data_store["Time"].append(next_period_start)

            # Write out a line
            self.graph_data.write("%f" % (avg(self.graph_data_store["Time"]) - 1.23219e+09))
            for label in self.graph_labels[1:]:
                self.graph_data.write(",%f" % avg(self.graph_data_store[label]))
            self.graph_data.write("\n")

            # Zero out the whole lot
            for label in self.graph_labels:
                self.graph_data_store[label] = []

            # Set up the Time one. 
            self.graph_data_store["Time"].append(next_period_start)

            print "Wrote a new line"

        if key not in self.graph_labels:
            self.sa.console.write("*** Adding " + key + " to graph labels!", mod=self)

            self.graph_data.close()
            os.popen("mv %s %s-%f" % (self.graph_file_name, self.graph_file_name, time.time()))
            self.graph_data = file(self.graph_file_name, "w+")
            self.graph_labels.append(key)
            self.graph_data_store[key] = [value]
            self.graph_data.write(self.graph_labels[0])
            for label in self.graph_labels[1:]:
                print label
                self.graph_data.write("," + label) 
            self.graph_data.write("\n")

        # Otherwise, if the key _is_ in there, we're in business!
        else:
            self.graph_data_store[key].append(value)

    def do_graph_tag(self, parms):
        print "Doing graph tag: " 
        print parms
        name = parms[1]
        x_label = parms[2]
        y_label = parms[3]
        parms = parms[4:]
        graphs = []
        while(len(parms) >= 3):
            graph = {}
            graph["x_name"] = parms[0]
            graph["y_name"] = parms[1]
            graph["plottype"] = parms[2]
            graphs.append(graph)
            parms = parms[3:]

        return self.do_graph(name, graphs, x_label=x_label, y_label=y_label)
        
    def do_graph(self, name, graphs, x_label="", y_label=""):
        os.popen("mkdir -p " + self.config["graphdir"])
        graphname = name + ".png"
        graphname = graphname.replace(" ", "_")
        graphpath = self.config["graphdir"] + "/" + graphname
        datafile = self.graph_file_name

        gnuplot = os.popen("gnuplot", "w")
        gnuplot.write("set terminal png size 640,480\n")
        gnuplot.write("set xlabel \"" + x_label + "\"\n")
        gnuplot.write("set ylabel \"" + y_label + "\"\n")
        if x_label[0:4] == "Time":
            gnuplot.write("set xtics rotate by 90\n")
         #gnuplot.write("unset xtics\n")

        gnuplot.write("set datafile separator \",\"\n")
        gnuplot.write("set output \"%s\"\n" % graphpath)
        print "Outputting to " + graphpath
        
        if graphs != []:
            gnuplot.write("plot ")
            for i in range(len(graphs)):
                if i != 0:
                    gnuplot.write(",\\\n")

                graph = graphs[i]

                print graph

                try:
                    x_index = self.graph_labels.index(graph["x_name"])
                except ValueError:
                    self.sa.console.write("Could not find key %s\n" % (graph["x_name"]), mod=self )
                    return "N/A"

                try:
                    y_index = self.graph_labels.index(graph["y_name"])
                except ValueError:
                    self.sa.console.write("Could not find key %s\n" % (graph["y_name"]), mod=self)
                    return "N/A"

                plottype = graph["plottype"]

                gnuplot.write("\"%s\" using %d:%d notitle with %s" % (datafile, x_index+1, y_index+1, plottype))
            
         
        gnuplot.close()

        return graphname

    def do_parse_tag(self, parms, linenum):
        if len(parms) < 1:
            self.sa.console.write("Error parsing tag on line %d -- no actual tag!" %linenum, mod=self)
            return ""
        
        if parms[0] == "CHANNEL":
            if len(parms) != 3:
                self.sa.console.write("Error parsing tag on line %d -- not enough params to CHANNEL tag -- usual form is <<<<CHANNEL NodeName ChannelName>>>>" %linenum, mod=self)

            self.chans_lock.acquire()
            key = (parms[1], parms[2])
            if key in self.chans:
                self.chans_lock.release()
                return str(self.chans[key])
            else:
                self.chans_lock.release()
                return "N/A"

        elif parms[0] == "GRAPH":
            return self.do_graph_tag(parms)

        elif parms[0] == "WEBCAMIMAGE":
            return "latest_webcam.jpg"
            #return self.latest_webcam_image

        elif parms[0] == "TIME":
            return time.strftime("%I:%M%p %dth %B, %Y")
        
        elif parms[0] == "CTIME":
            return time.ctime()
        
        else:
            self.sa.console.write("Didn't recognise this %s on line %d" %(parms[0], linenum), mod=self)
            return ""

    def do_html_update(self):
        files = os.listdir(self.config["inputhtml"])
        for f in files:
            if ".html" in f:
                print "Updating " + f
                input = file(self.config["inputhtml"] + "/" + f)
                output = file(self.config["outputhtml"] + "/" + f, "w+")

                linenum = 0
                for line in input:
                    linenum += 1

                    # Look for token replacements
                    while True:
                        i = line.find("<<<<")
                        if i == -1:
                            break; 

                        # Write up to the 
                        output.write(line[0:i])
                        
                        # Get rid of the stuff we just wrote
                        # and the < characters
                        line = line[i+1:]
                        line = line.lstrip("<")

                        # Find the end of the token and split it off
                        i = line.find(">>>>")
                        if i == -1:
                            self.sa.console.write("Invalid line at line# %d -- no end >>>>" % linenum, mod=self)
                            break

                        mytok = line[0:i]
                        line = line[i+4:] # Get rid of the <<<<

                        parms = mytok.split("/")

                        # Get rid of any leading or trailing whitespace
                        for i in range(len(parms)):
                            parms[i] = parms[i].lstrip().rstrip()

                        output.write(self.do_parse_tag(parms, linenum))

                    # Write the rest of the line to the output
                    output.write(line)

                input.close()
                output.close()

        return True

    def do_upload_to_server(self):
        try:
            localpath = self.config["outputhtml"] + "/*"
            remotepath = self.config["scploc"] + "/"
            command = "rsync -a " + localpath + " " + remotepath
            print command
            cmd = Popen(command, shell=True)
            cmd.wait()
        except OSError, e:
            self.sa.console.write("Error doing upload -- " + str(e), mod=self)
            return False
        
        return True

    def worker(self):
        while self.running:
            # First grab an image
            if not self.do_grab_video():
                continue

            # Then update the web page
            if not self.do_html_update():
                continue
            
            if not self.do_upload_to_server():
                continue

            self.sa.console.write("Successfully updated", mod=self)


    def stop(self):
        Driver.Driver.stop(self)
        self.sa.remove_notebook_page(self.page)

    # Overrides the Module version
    def configure(self):
        widg = Driver.Driver.configure(self)

        vbox = gtk.VBox()
        widg.pack_start(vbox)

        textconf = Configurator.TextConfig("video", self.config, "Video source")
        vbox.pack_start(textconf, expand=False)

        textconf = Configurator.TextConfig("scploc", self.config, "SCP/RSYNC location")
        vbox.pack_start(textconf, expand=False)

        textconf = Configurator.TextConfig("imgdir", self.config, "Image Directory")
        vbox.pack_start(textconf, expand=False)

        textconf = Configurator.TextConfig("inputhtml", self.config, "Input HTML directory")
        vbox.pack_start(textconf, expand=False)

        textconf = Configurator.TextConfig("outputhtml", self.config, "Output HTML directory")
        vbox.pack_start(textconf, expand=False)

        textconf = Configurator.TextConfig("graphdir", self.config, "Graph Directory")
        vbox.pack_start(textconf, expand=False)

        return widg

# Register our driver with the driver module's module factory
Driver.modfac.add_type("Live View", LiveView)
