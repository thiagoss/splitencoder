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

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

# Process tasks forever
while True:
    s = receiver.recv()
    print 'Transcoding: ', s

    transcode('http://localhost:8000/%s' % s,
              'transcoded/%s' % s)
    sender.send_string(s)
