#!/bin/bash
# HOURS determines how many hours there are between each run
HOURS=1

if [ $# -gt 0 ]; then
HOURS=$1
fi

FILE="tmp_cron"

# Set PATH in run_cron to absolute path to this directory
CHANGE=ABSPATH
sed -i "s+$CHANGE+$PWD+g" ./run_cron.sh

crontab -l > $FILE
python -m src.general.cron $FILE $HOURS
crontab $FILE
rm $FILE