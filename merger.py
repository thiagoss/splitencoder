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
