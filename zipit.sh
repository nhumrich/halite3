#!/usr/bin/env bash

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
zip nicksbot.zip MyBot.pypy -r ./hlt/ install.sh
