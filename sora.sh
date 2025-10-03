#!/bin/bash

# Check that 'in' and 'out' directories exist
if [ ! -d "in" ] || [ ! -d "out" ]; then
    echo "Error: 'in' and 'out' directories must exist."
    echo "Please create them before running this script. And put videos into 'in' directory."
    exit 1
fi

for infile in in/*.mp4; do
    filename=$(basename "$infile")
    outfile="out/$filename"
    if [ -e "$outfile" ]; then
        echo "Skipping $outfile (already exists)"
        continue
    fi
    ./start.sh -i "$infile" -o "$outfile" -w "20,80,180,75,0,3" "538,600,180,60,2,5" "20,1020,180,75,4,8" "20,80,180,75,7,10"
done