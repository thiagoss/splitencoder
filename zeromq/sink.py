

# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import urllib
import processing

from splitencoder.merger import merge

class DownloadTask(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.queue = processing.Queue()
        self.process = processing.Process(target=self.download, args=[self.queue])
        self.finished = True

    def start(self):
        self.finished = False
        self.process.start()

    def join(self):
        self.process.join()

    def download(self, q):
        x = urllib.urlretrieve (self.url, self.name)
        q.put(x[0])

    def has_finished(self):
        if self.finished:
            return False

        if self.queue.empty():
            return False
        print self.queue.get()
        self.finished = True
        return True

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5558")

# Start our clock now
tstart = time.time()

start_msg = receiver.recv()
start_msg = start_msg.split(';')
outputfile = start_msg[0]
number = int(start_msg[1])

print 'Creating output file \'%s\' (%d segments)' % (outputfile, number)

total_msec = 0
files = []
processes = []
local_files = []

def update_downloads():
    ret = False
    for p in processes:
        if p.has_finished():
            local_files.append(p.name)
            ret = True
    return ret

def print_status():
    print 'Transcoded: %d / %d' % (len(files), number)
    print 'Downloaded: %d / %d' % (len(local_files), number)
    print

while len(files) < number:
    s = receiver.recv()
    files.append(s)
    p = DownloadTask('downloaded/' + s, 'http://localhost:8008/%s' % s)
    p.start()
    processes.append(p)
    update_downloads()
    print_status()


while len(local_files) < number:
    if update_downloads():
        print_status()
    time.sleep(1)

print 'Starting merge'
merge('downloaded/*', 'output.mkv')
print 'Finished:', outputfile
