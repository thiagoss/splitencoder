#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Splits the file and sends the chunks to be transcoded by workers
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket
#
# Based on sample by: Lev Givon <lev(at)columbia(dot)edu>

from datetime import datetime
import time
import sys
import os
import errno
from os import listdir
from os.path import isfile, join
import argparse

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

parser = argparse.ArgumentParser('Splits a video file and sends for transcoders')
parser.add_argument('--input-uri', type=str, metavar='i', help='Input media URI')
parser.add_argument('--output-file', type=str, metavar='o', help='Output file')
parser.add_argument('--port', type=int, metavar='p', default=5557)
parser.add_argument('--sink-port', type=int, default=5558)
parser.add_argument('--sink-host', type=str, default='localhost')
parser.add_argument('--base-uri', type=str, default='http://localhost:8000/')

args = parser.parse_args()
outputdir = 'split'

make_sure_path_exists(outputdir)

context = zmq.Context()

print 'Spliter starting... (time: %s)' % str(datetime.now().isoformat())

# Socket to send messages on
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:%d" % args.port)

# Socket with direct access to the sink: used to syncronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://%s:%d" % (args.sink_host, args.sink_port))

split_start = time.time()
split(args.input_uri, outputdir)
split_end = time.time()

print 'Splitting file took %ss' % str(split_end - split_start)

onlyfiles = [ f for f in listdir(outputdir) if isfile(join(outputdir,f)) ]
onlyfiles.sort()

sink.send_string('%s;%d' % (args.output_file, len(onlyfiles)))

print 'Sending %d segments for transcoding' % len(onlyfiles)

for f in onlyfiles:
    print f
    sender.send_string(args.base_uri + f)

# Give 0MQ time to deliver
time.sleep(5)

