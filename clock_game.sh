#!/bin/bash

if [[ $1 == "True" ]] ; then
    python clock_game.py -ng $1 -s $2
else
    python clock_gui.py -s $2 &
    sleep 1
    python clock_game.py -s $2 &
fi