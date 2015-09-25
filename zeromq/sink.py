

# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
from datetime import datetime
import time
import zmq
import urllib
import argparse
import processing

from splitencoder.merger import merge

parser = argparse.ArgumentParser('Merges')
parser.add_argument('--port', type=int, default=5558)
args = parser.parse_args()

class DownloadTask(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.queue = processing.Queue()
        self.process = processing.Process(target=self.download, args=[self.queue])
        self.finished = True

    def start(self):
        self.start = time.time()
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
        print 'Download finished: %s %f' % (self.name, time.time() - self.start)
        return True

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:%d" % args.port)


start_msg = receiver.recv()
start_msg = start_msg.split(';')
outputfile = start_msg[0]
number = int(start_msg[1])

# Start our clock now
tstart = time.time()

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
    file_name = s[s.rfind('/')+1:]
    files.append(file_name)
    print 'Downloading:', s
    p = DownloadTask('downloaded/' + file_name, s)
    p.start()
    processes.append(p)
    update_downloads()
    print_status()


while len(local_files) < number:
    if update_downloads():
        print_status()
    time.sleep(1)

print 'Starting merge'
merge_start = time.time()
merge('downloaded/*', outputfile)
print 'Merge finished:', time.time() - merge_start
print 'Finished: %s %s (%f)' % (outputfile, datetime.now().isoformat(), time.time() - tstart)

