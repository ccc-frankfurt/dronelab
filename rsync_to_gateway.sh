#!/bin/bash
TARGET=/data/AISEL/dronelab
SOURCE=/home/pi/data
GATEWAYIP=141.2.10.184
DRONENAME=TELLO-588A0C


# sync pictures to remote server
echo 'ssh pi@'$GATEWAYIP' "mkdir -p "'$TARGET'/'$DRONENAME
echo 'rsync --relative --inplace --partial --append --progress -avz '$SOURCE'/./'$DRONENAME'/ pi@'$GATEWAYIP':'$TARGET'/'

