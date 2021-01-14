#!/bin/bash
# Setup
if [ -z $1 ]
    then
        echo "Script $0 takes two arguments. Provide a period in between exitmap runs in hours 1-23 as an integer. Provide amount of runs as an integer."
        echo "Syntax: sh $0 PERIOD RUNS"
        exit 1
    fi

echo "Period: $1"
echo "Runs: $2"

# Variables and executables
WORKING_DIRECTORY=$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/../"
EXITMAP_CMD="( cd $WORKING_DIRECTORY && sh bin/run.sh )"
#CLEAN_CMD="( crontab -l | grep "$WORKING_DIRECTORY" -v | crontab - )"

# Temporary directory
CRON_TMP="/tmp/"$(tr -dc A-Za-z0-9 </dev/urandom | head -c 8 ; echo '')
eval touch $CRON_TMP
eval crontab -l > $CRON_TMP

# Set cron jobs
echo $(date --date 'now + 1 minutes' +"%M")' */'$1' * * * '$EXITMAP_CMD >> $CRON_TMP
#echo $(date --date 'now + 5 minutes' +"%M")' */'$(($1*$2))' * * * '$CLEAN_CMD >> $CRON_TMP
eval crontab $CRON_TMP
eval rm -f $CRON_TMP
eval crontab -l