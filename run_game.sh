#!/bin/sh

#./halite --replay-directory replays/ -vvv --seed  1540874910 --width 56 --height 56 "python3 run.py" "python3 run.py" "python3 old.py" "python3 old.py"
./halite --replay-directory replays/ -vvv --seed  1540874910 --width 32 --height 32 "python3 MyBot.pypy --look_amount 40" "python3 OldBot.pypy"
#./halite --replay-directory replays/ -vvv "python3 MyBot.pypy --name 1" "python3 OldBot.pypy --name old" "python3 OldBot.pypy --name old2" "python3 MyBot.pypy --name 2"
#./halite --replay-directory replays/ -vvv "python3 run.py" "python3 other.py" "python3 run.py -s" "python3 old.py"
#./halite --replay-directory replays/ "python3 run.py" "python3 run.py" "python3 run.py" "python3 run.py"


