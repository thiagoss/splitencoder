#!/bin/bash

# Argument 1 is the file to be transcoded
# Argument 2 is the output file
inputfile=$1
outputfile=$2

gst-launch-1.0 uridecodebin uri=file://`readlink -f $inputfile` name=u ! queue ! videoconvert ! videoscale ! x264enc ! matroskamux name=m ! filesink location=$outputfile u. ! queue ! audioconvert ! audiorate ! faac ! m.
