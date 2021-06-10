#!/bin/bash
#set password parameter
TARGET=/data/AISEL/dronelab
SOURCE=/home/pi/data
GATEWAYIP=141.2.10.184
DRONENAME=TELLO-588A0C




# sync pictures to remote server
ssh pi@$GATEWAYIP mkdir -p $TARGET/$DRONENAME
rsync --relative --inplace --partial --append --progress -avz $SOURCE/./$DRONENAME/ pi@$GATEWAYIP:$TARGET/

