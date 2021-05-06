#!/bin/bash
TARGET=/data/AISEL/dronelab
SOURCE=/home/pi/data
GATEWAYIP=192.168.0.144
DRONENAME=TELLO-588A0C


# sync pictures to remote server
ssh pi@$GATEWAYIP "mkdir -p "$TARGET/$DRONENAME
rsync --relative --inplace --partial --append --progress -avz $SOURCE/./$DRONENAME/ pi@$GATEWAYIP:$TARGET/

