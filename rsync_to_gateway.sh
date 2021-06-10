#!/bin/bash
#set password parameter
set -e

if [[ $# -eq 0 ]] ; then
    echo 'Require password'
    exit 1
fi

pw=$1
TARGET=/data/AISEL/dronelab
SOURCE=/home/pi/data
GATEWAYIP=141.2.10.184
DRONENAME=TELLO-588A0C




# sync pictures to remote server
sshpass $pw -p ssh pi@$GATEWAYIP mkdir -p $TARGET/$DRONENAME
rsync --relative --inplace --partial --append --progress -avz $SOURCE/./$DRONENAME/ pi@$GATEWAYIP:$TARGET/

