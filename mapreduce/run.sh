#!/bin/bash

CHUNKS_DIR=output
INPUT_VIDEO=file:///path/to/video
mkdir -p $CHUNKS_DIR

JOB_INPUT_FILE=jobinput

python mrsplitter.py --chunks-dir $CHUNKS_DIR --input $INPUT_VIDEO
ls -1 $CHUNKS_DIR > $JOB_INPUT_FILE
python job.py $OUTPUT_FILE --files-root "$PWD/$CHUNKS_DIR"
rm $JOB_INPUT_FILE
