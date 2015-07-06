import sys

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
from gi.repository import GObject, Gst, GstPbutils

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

def caps_is_video(caps):
    s = caps.get_structure(0)
    return s.get_name().startswith('video/')
def caps_is_audio(caps):
    s = caps.get_structure(0)
    return s.get_name().startswith('audio/')

def on_pad_added(element, pad, udata):
    pipeline, muxer = udata
    caps = pad.get_current_caps()
    if caps_is_video(caps):
        reqname = 'video_%u'
    elif caps_is_audio(caps):
        reqname = 'audio_%u'
    else:
        print 'Ignoring pad of caps:', caps.to_string()
        return

    tmpl = type(muxer).get_pad_template(reqname)
    other_pad = muxer.request_pad(tmpl, None, None)
    if other_pad:
        queue = Gst.ElementFactory.make('queue')
        queue.set_property('max-size-buffers', 0)
        queue.set_property('max-size-time', 0)
        queue.set_property('max-size-bytes', 0)
        pipeline.add(queue)
        queue.sync_state_with_parent()
        pad.link(queue.get_static_pad('sink'))
        queue.get_static_pad('src').link(other_pad)

def transcode(input_file, output_file, profile):
    loop = GObject.MainLoop()

    pipeline = Gst.Pipeline()
    uridecodebin = Gst.ElementFactory.make('uridecodebin')
    encodebin = Gst.ElementFactory.make('encodebin')
    sink = Gst.ElementFactory.make('filesink')
    pipeline.add(uridecodebin)
    pipeline.add(encodebin)
    pipeline.add(sink)

    encodebin.link(sink)

    uridecodebin.set_property('uri', input_file)
    sink.set_property('location', output_file)
    encodebin.set_property('profile', profile)
    uridecodebin.connect('pad-added', on_pad_added, (pipeline, encodebin))

    bus = pipeline.get_bus()
    bus.add_watch(0, on_message, (pipeline, loop))

    pipeline.set_state(Gst.State.PLAYING)
    loop.run()

def create_encoding_profile():
    container = GstPbutils.EncodingContainerProfile.new('matroska', None, Gst.Caps.new_empty_simple('video/x-matroska'), None)
    video = GstPbutils.EncodingVideoProfile.new(Gst.Caps.new_empty_simple('video/x-h264'), None, None, 0)
    audio = GstPbutils.EncodingAudioProfile.new(Gst.Caps.from_string('audio/mpeg, mpegversion=4'), None, None, 0)
    container.add_profile(video)
    container.add_profile(audio)
    return container

if __name__ == '__main__':
    Gst.init()

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    #TODO validate args

    profile = create_encoding_profile()

    transcode(input_file, output_file, profile)
