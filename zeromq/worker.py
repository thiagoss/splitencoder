#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Task worker
#
# Transcodes files
# Connects PULL socket to tcp://localhost:5557
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#
# Based on sample by: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import argparse
import zmq

from splitencoder.transcoder import transcode

parser = argparse.ArgumentParser('Transcodes files')
parser.add_argument('--tasks-host', type=str, default='localhost')
parser.add_argument('--tasks-port', type=int, default=5557)
parser.add_argument('--sink-host', type=str, default='localhost')
parser.add_argument('--sink-port', type=int, default=5558)
parser.add_argument('--base-uri', type=str, default='http://localhost:8000/')
parser.add_argument('--spawn-process', dest='process', action='store_true')
parser.add_argument('--no-spawn-process', dest='process', action='store_false')

args = parser.parse_args()

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://%s:%d" % (args.tasks_host, args.tasks_port))

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://%s:%d" % (args.sink_host, args.sink_port))

def do_transcode(in_uri, outfile):
    transcode(s, 'transcoded/%s' % file_name)

# Process tasks forever
while True:
    s = receiver.recv()
    print 'Transcoding: ', s

    file_name = s[s.rfind('/')+1:]

    if args.process:
        p = processing.Process(target=do_transcode,
                               args=[s, 'transcoded/%s' % file_name])
        p.start()
        p.join()
    else:
        transcode(s, 'transcoded/%s' % file_name)
    sender.send_string(args.base_uri + file_name)
