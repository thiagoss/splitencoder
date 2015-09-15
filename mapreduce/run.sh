#!/bin/bash

CHUNKS_DIR=output
INPUT_VIDEO=file:///path/to/video
OUTPUT_VIDEO=output.mkv
mkdir -p $CHUNKS_DIR

JOB_INPUT_FILE=jobinput

python mrsplitter.py --chunks-dir $CHUNKS_DIR --input $INPUT_VIDEO
ls -1 $PWD/$CHUNKS_DIR/* > $JOB_INPUT_FILE
python job.py $JOB_INPUT_FILE --files-root "$PWD/$CHUNKS_DIR" $PWD/$OUTPUT_VIDEO
rm $JOB_INPUT_FILE
