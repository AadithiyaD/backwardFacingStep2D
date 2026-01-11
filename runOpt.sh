#!/bin/sh

# Small QOL script to run the experiement. Configure centralControl, and then execute this shell script
# to start the experiment

# Remove previous cases and results
./Allclean

python3 centralControl.py

python3 bayesOpt.py