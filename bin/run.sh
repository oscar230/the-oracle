#!/bin/bash

# Variables and direcories
ID=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 8 ; echo ''); ID=$(date +%s)"-"$ID
WORKING_DIRECTORY=$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/../"
CONFIG=$WORKING_DIRECTORY"exitmaprc"
CACHE_DIR=$WORKING_DIRECTORY"tor_cache/"$ID
OUTPUT_FILE=$WORKING_DIRECTORY"logs/"$ID".txt"

touch $OUTPUT_FILE
# Run command and log
echo "Running exitmap with module timeddns. Id: $ID"
echo "$0 Started at $(date) by user $(whoami)." >> $OUTPUT_FILE
echo "Current working directory $WORKING_DIRECTORY" >> $OUTPUT_FILE
eval $WORKING_DIRECTORY"exitmap/bin/exitmap" timeddns -f $CONFIG -t $CACHE_DIR &>> $OUTPUT_FILE
echo "$0 Exitmap done at $(date) by user $(whoami)." >> $OUTPUT_FILE

# Cleanup
echo "Remving $CACHE_DIR" >> $OUTPUT_FILE
eval rm -rf $CACHE_DIR
echo "$0 Cache cleared, script exiting at $(date) by user $(whoami)." >> $OUTPUT_FILE