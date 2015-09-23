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
import zmq

from splitencoder.transcoder import transcode

tasks_host = 'localhost'
tasks_port = 5557
sink_host = 'localhost'
sink_port = 5558
segment_base_uri = 'http://localhost:8008/'

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://%s:%d" % (tasks_host, tasks_port))

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://%s:%d" % (sink_host, sink_port))

# Process tasks forever
while True:
    s = receiver.recv()
    print 'Transcoding: ', s

    file_name = s[s.rfind('/')+1:]

    transcode(s, 'transcoded/%s' % file_name)
    sender.send_string(segment_base_uri + file_name)
