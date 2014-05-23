#!/bin/bash

width=1024
height=2000
depth=24

Xvfb :1 -screen 0 ${width}x${height}x${depth} &
DISPLAY=:1 firefox -width $width -height $height http://lostfilm.tv &

#Wait for Xvfb to initialize
# ACTIVE=9999
# while [ $ACTIVE -ne 0 ] ; do
#         xdpyinfo -display :1 &> /dev/null
#         ACTIVE=$?
# done
sleep 1
myvar="0 0"
while [[ true ]]
do
DISPLAY=:1 import -window root ./before.jpg  # make screenshot
myvar=$(python find.py before.jpg)
echo $myvar
if [ "$myvar" != "0 0" ]
then 
	break
fi
done 

DISPLAY=:1 xdotool mousemove $myvar click 1
sleep 5
DISPLAY=:1 import -window root ./after.jpg  # screenshot again