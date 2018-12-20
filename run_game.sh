#!/bin/sh

#./halite --replay-directory replays/ -vvv --seed  1540874910 --width 56 --height 56 "python3 run.py" "python3 run.py" "python3 old.py" "python3 old.py"
./halite --replay-directory replays/ -vvv --seed  1540874910 --width 48 --height 48 "python3 MyBot.pypy" "python3 MyBot.pypy"
#./halite --replay-directory replays/ -vvv "python3 run.py" "python3 other.py" "python3 run.py -s" "python3 old.py" --no-timeout
#./halite --replay-directory replays/ -vvv "python3 run.py" "python3 other.py" "python3 run.py -s" "python3 old.py"
#./halite --replay-directory replays/ "python3 run.py" "python3 run.py" "python3 run.py" "python3 run.py"


