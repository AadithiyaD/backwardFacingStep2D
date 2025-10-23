#!/bin/bash

# Moves the validation grid files from NASA_Grids to the current directory
# Usage: copyGrid.sh <number_of_level> <2d/3d>
# Example: copyGrid.sh 4 2d

rm backstep5_[0-4]levdn.p[23]dfmt
cp "NASA_Grids/backstep5_${1}levdn.p${2}fmt" .