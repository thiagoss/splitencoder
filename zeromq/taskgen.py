#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Splits the file and sends the chunks to be transcoded by workers
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket
#
# Based on sample by: Lev Givon <lev(at)columbia(dot)edu>

import time
import sys
import os
import errno
from os import listdir
from os.path import isfile, join

import zmq

from splitencoder.splitter import split

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        elif not os.path.isdir(path):
            raise

inputuri = sys.argv[1]
outputfile = sys.argv[2]
outputdir = 'split'
sender_port = 5557
sink_host = 'localhost'
sink_port = 5558
segments_base_uri = 'http://localhost:8000/'

make_sure_path_exists(outputdir)

context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:%d" % sender_port)

# Socket with direct access to the sink: used to syncronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://%s:%d" % (sink_host, sink_port))

split(inputuri, outputdir)

onlyfiles = [ f for f in listdir(outputdir) if isfile(join(outputdir,f)) ]
onlyfiles.sort()

sink.send_string('%s;%d' % (outputfile, len(onlyfiles)))

print 'Sending %d segments for transcoding' % len(onlyfiles)

for f in onlyfiles:
    print f
    sender.send_string(segments_base_uri + f)

# Give 0MQ time to deliver
time.sleep(5)

