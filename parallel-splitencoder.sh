#!/bin/bash

# Transcodes a media file remotely using parallel

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
    echo "parallel-splitencoder.sh <input_uri> <split_directory> <output_file>"
    exit 1
fi

# 1. Split
python splitter.py $1 $2

# 2. Transcode
parallel --no-notice --sshloginfile nodefile --transfer "transcoder.py {} $3/out_{}" ::: `find $2 -type f`

# 3. Merge
# TODO
