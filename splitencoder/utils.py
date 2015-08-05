# splitencoder
#
# Copyright (C) 2015 Samsung Electronics. All rights reserved.
#   Author: Thiago Santos <thiagoss@osg.samsung.com>
#
# This library is free software; you can redistribute it and/or
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

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

def caps_is_video(caps):
    s = caps.get_structure(0)
    return s.get_name().startswith('video/')
def caps_is_audio(caps):
    s = caps.get_structure(0)
    return s.get_name().startswith('audio/')

