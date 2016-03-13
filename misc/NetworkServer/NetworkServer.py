#!/usr/bin/env python

# These you shouldn't need to install
from optparse import OptionParser
import pprint, sys, copy, math
import thread

import socket

threadlock = thread.allocate_lock()
threads = []

def client_thread(lock, clientsocket):
    print "Started new thread with " + str(clientsocket.getsockname())
    while 1:
        data = clientsocket.recv(1024)
        if data > 0:
            threadlock.acquire()
            for (theirlock, theirclientsocket) in threads:
                theirlock.acquire()
                theirclientsocket.send(data)
                theirlock.release()
            threadlock.release()
        else:
            print "Got zero data from " + str(clientsocket.getsockname())

config = {}
if "port" not in config:
    config["port"] = 4001


#create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind the socket to a public host, 
# and a well-known port
serversocket.bind((socket.gethostname(), config["port"]))
print "Listening on port " + str(config["port"])

#become a server socket
serversocket.listen(5)

while 1:
#accept connections from outside
    (clientsocket, address) = serversocket.accept()

    # Create the lock
    lock = thread.allocate_lock()

    # Add the thread to our records
    threadlock.acquire()
    threads.append( (lock, clientsocket) )
    threadlock.release()

#now do something with the clientsocket
#in this case, we'll pretend this is a threaded server
    ct = thread.start_new_thread(client_thread, (lock, clientsocket))


