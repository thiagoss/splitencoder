#!/bin/bash

# Argument 1 is the directory with the segments
# Argument 2 is the output file
inputdir=$1
outputfile=$2

gst-launch-1.0 splitmuxsrc location=$inputdir name=s ! queue ! h264parse ! matroskamux name=m ! filesink location=$outputfile s. ! queue ! aacparse ! m.
