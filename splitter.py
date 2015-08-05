#!/usr/bin/env python
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

from splitencoder import utils

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

def on_autoplug_factories(element, pad, caps, udata):
    factories = Gst.ElementFactory.list_get_elements(Gst.ELEMENT_FACTORY_TYPE_DEMUXER | Gst.ELEMENT_FACTORY_TYPE_PARSER, Gst.Rank.MARGINAL)
    factories = Gst.ElementFactory.list_filter(factories, caps, Gst.PadDirection.SINK, caps.is_fixed())

    if len(factories) == 0:
        #TODO check if this is indeed a parsed type and not some unhandled format (missing elements)
        return None

    return factories

def on_autoplug_continue(element, pad, caps, udata):
    s = caps.get_structure(0)
    if s.has_field('parsed'):
        if s.get_value('parsed') == True:
            return False
    if s.has_field('framed'):
        if s.get_value('framed') == True:
            return False

    return True

def on_pad_added(element, pad, udata):
    pipeline, splitmuxsink = udata
    other_pad = None

    # Can't use 'get_compatible_pad' because splitmuxsink pad templates
    # are all ANY so it will always match the first
    if utils.caps_is_video(pad.get_current_caps()):
        klass = type(splitmuxsink)
        tmpl = klass.get_pad_template('video')
        other_pad = splitmuxsink.request_pad(tmpl, None, None)
    elif utils.caps_is_audio(pad.get_current_caps()):
        klass = type(splitmuxsink)
        tmpl = klass.get_pad_template('audio_%u')
        other_pad = splitmuxsink.request_pad(tmpl, None, None)
    else:
        caps = pad.get_current_caps()
        print 'leaving pad %s unlinked - "%s"' % (pad.get_name(), caps.to_string() if caps else 'no caps')

    if other_pad:
        queue = Gst.ElementFactory.make('queue')
        pipeline.add(queue)
        queue.sync_state_with_parent()
        pad.link(queue.get_static_pad('sink'))
        queue.get_static_pad('src').link(other_pad)

def split(input_uri, output_dir):
    loop = GObject.MainLoop()

    pipeline = Gst.Pipeline()
    uridecodebin = Gst.ElementFactory.make('uridecodebin')
    splitmuxsink = Gst.ElementFactory.make('splitmuxsink')
    pipeline.add(uridecodebin)
    pipeline.add(splitmuxsink)

    uridecodebin.set_property('uri', input_uri)
    uridecodebin.connect('autoplug-factories', on_autoplug_factories, None)
    uridecodebin.connect('autoplug-continue', on_autoplug_continue, None)
    uridecodebin.connect('pad-added', on_pad_added, (pipeline, splitmuxsink))

    # TODO fix mp4mux to properly segment files
    splitmuxsink.set_property('muxer', Gst.ElementFactory.make('matroskamux'))
    splitmuxsink.set_property('location', output_dir + '/' + 'segment_%09d.mkv')
    splitmuxsink.set_property('max-size-time', 10000000000) #10s segments

    bus = pipeline.get_bus()
    bus.add_watch(0, on_message, (pipeline, loop))

    pipeline.set_state(Gst.State.PLAYING)
    loop.run()

if __name__ == '__main__':
    Gst.init()

    input_uri = sys.argv[1]
    output_dir = sys.argv[2]
    #TODO validate args

    split(input_uri, output_dir)
