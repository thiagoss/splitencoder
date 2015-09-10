#!/bin/bash

mkdir -p output
cp input output

OUTPUT_FILE=output/jobinput

python splitter.py --files-root output --file-name input > $OUTPUT_FILE
python job.py $OUTPUT_FILE --files-root "$PWD/output"
