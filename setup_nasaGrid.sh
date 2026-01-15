#!/bin/sh

# Use this script to setup the project for use on the grids from
# the NASA Turbulence Modelling Resource (https://turbmodels.larc.nasa.gov/backstep_grids.html)
# Usage- ./setup_nasaGrid.sh <grid_level>

# Delete existing sample, BC setup and mesh miles
rm system/sample
rm -rf 0
rm -rf constant/polyMesh

# Copy the new ones
cp system/sample_nasaGrid system/sample
cp -r 0.orig_nasaGrid ./0

# Setup chosen grid level
rm backstep5_[0-4]levdn.p[23]dfmt

# Move chosen grid to project root
cp "NASA_Grids/backstep5_${1}levdn.p2dfmt" .

# Convert to foam format
plot3dToFoam -2D 1 -noBlank backstep5_${1}levdn.p2dfmt

# Create patches
autoPatch -overwrite 90

topoSet

createPatch -overwrite

createPatch -dict system/patchMerge -overwrite

# Remove the grid we initially moved to the root
rm backstep5_[0-4]levdn.p[23]dfmt