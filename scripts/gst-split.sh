#!/bin/bash

# Argument 1 is the file to be split
# Argument 2 is the output directory to save the segments
inputfile=$1
outputdir=$2
segmenttime=10000000000

# Create output dir if it doesn't exist
if [ ! -d "$outputdir" ]; then
  mkdir -p $outputdir
fi

# Try to figure out the right demuxer to use
if [[ $inputfile =~ \.mp4$ ]]; then
  demuxer="qtdemux"
elif [[ $inputfile =~ \.mov$ ]]; then
  demuxer="qtdemux"
else
  echo "Unhandled file type, please add a demuxer for it in the list."
  exit 1
fi

gst-launch-1.0 file://`readlink -f $inputfile` ! $demuxer name=d ! queue ! splitmuxsink name=m muxer=matroskamux location="$outputdir/segment_%09d.mkv" max-size-time=$segmenttime d. ! queue ! m.audio_%u
