#!/bin/bash

# Transcodes a media file remotely using parallel

if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters"
    echo "parallel-splitencoder.sh <input_uri> <split_directory> <transcoded_directory> <output_file>"
    exit 1
fi

# 1. Split
echo "Splitting"
python splitencoder/splitter.py $1 $2

# 2. Transcode
echo "Transcoding"
parallel --no-notice --sshloginfile nodefile --transfer --return $3/{} "splitencoder/transcoder.py {} $3/{}" ::: `find $2 -type f`

# 3. Merge
echo "Merging"
python splitencoder/merger.py "$3/$2/segment_*" $4
