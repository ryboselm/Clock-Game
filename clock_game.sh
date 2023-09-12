#!/bin/bash

if [[ $1 == "True" ]] ; then
    python clock_game.py -ng True
else
    python clock_gui.py &
    sleep 1
    python clock_game.py &
fi