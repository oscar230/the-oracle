#!/bin/bash
WORKING_DIRECTORY=$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/.."
watch "
    echo 'Watching the oracle output and exitmap running processes.';
    echo 'Results files:';
    du -hs $WORKING_DIRECTORY'/results';
    echo 'Exit nodes scanned:';
    ls -1q results/** | wc -l;
    echo 'Exitmap processes:';
    ps wwuxa | grep 'exitmap' | grep -E 'grep|Watching the oracle output' -v -c;
    echo 'Run script processes:';
    ps wwuxa | grep -E 'run.sh' | grep 'grep' -v -c;
    echo 'Memory:';
    free -ht;
    echo 'CPU usage top 5:';
    ps -eo pcpu,pid,user,args | sort -k 1 -r | head -5;
    "