#!/bin/sh

# Use this script to setup the project for use on the backwardFacingStep2D tutorial from openFoam

# Delete existing sample, BC setup and mesh miles
rm system/sample
rm -rf 0
rm -rf constant/polyMesh

# Copy the new ones
cp system/sample_baseOF system/sample
cp -r 0.orig_baseOF ./0
blockMesh