#!/usr/bin/python2
#
# splitencoder
#
# Copyright (C) 2015 Samsung Electronics. All rights reserved.
#   Author: Thiago Santos <thiagoss@osg.samsung.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.
#

import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

def on_message(bus, message, udata):
    pipeline, loop = udata

    if message.type == Gst.MessageType.EOS:
        pipeline.set_state(Gst.State.NULL)
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        print message.parse_error()
        pipeline.set_state(Gst.State.NULL)
        loop.quit()

    return True

def on_pad_added(element, pad, udata):
    pipeline, muxer = udata

    other_pad = muxer.get_compatible_pad(pad, pad.get_current_caps())
    if other_pad:
        queue = Gst.ElementFactory.make('queue')
        pipeline.add(queue)
        queue.sync_state_with_parent()
        pad.link(queue.get_static_pad('sink'))
        queue.get_static_pad('src').link(other_pad)

def merge(input_location, output_file):
    loop = GObject.MainLoop()

    pipeline = Gst.Pipeline()
    splitmuxsrc = Gst.ElementFactory.make('splitmuxsrc')
    muxer = Gst.ElementFactory.make('matroskamux')
    sink = Gst.ElementFactory.make('filesink')
    pipeline.add(splitmuxsrc)
    pipeline.add(muxer)
    pipeline.add(sink)

    muxer.link(sink)

    splitmuxsrc.set_property('location', input_location)
    sink.set_property('location', output_file)
    splitmuxsrc.connect('pad-added', on_pad_added, (pipeline, muxer))

    bus = pipeline.get_bus()
    bus.add_watch(0, on_message, (pipeline, loop))

    pipeline.set_state(Gst.State.PLAYING)
    loop.run()

if __name__ == '__main__':
    Gst.init()

    input_location = sys.argv[1]
    output_file = sys.argv[2]
    #TODO validate args

    merge(input_location, output_file)
