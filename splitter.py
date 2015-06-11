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

def on_autoplug_continue(element, pad, caps, udata):
    #FIXME this is hardcoded for h264
    video_caps = Gst.Caps.from_string('video/x-h264, parsed=(boolean)true')

    if caps.can_intersect(video_caps):
        return False
    return True

def on_pad_added(element, pad, udata):
    pipeline, splitmuxsink = udata
    #TODO we are only linking video here
    if pad.get_current_caps().get_structure(0).get_name().startswith('video/'):
        other_pad = splitmuxsink.get_compatible_pad (pad, None)
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
    uridecodebin.connect('autoplug-continue', on_autoplug_continue, None)
    uridecodebin.connect('pad-added', on_pad_added, (pipeline, splitmuxsink))
    splitmuxsink.set_property('location', output_dir + '/' + 'segment_%09d.mp4')
    splitmuxsink.set_property('max-size-time', 10000000000) #4s segments

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
