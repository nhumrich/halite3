#!/bin/sh

#./halite --replay-directory replays/ -vvv --seed  1540874910 --width 56 --height 56 "python3 run.py" "python3 run.py" "python3 old.py" "python3 old.py"
./halite --replay-directory replays/ -vvv "python3 run.py" "python3 other.py" "python3 old.py" "python3 old.py"
