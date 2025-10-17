What is happening in this tut with the sampling; I do not know. This is what I need to figure out first

Q) How does the sampling utility work? How are the data files written out?
Which columns represent which variables? What is H, U_ref? Why does the gnuplot of U/Uref look 
so different to what my plotter plot of the same?
A) Try opening file in paraview, and probing specific locations for U vals, and compare with
csv files. 

In x_by_h_01_p_U_turbulenceProperties:devReff.xy
    - *columns 3,4,5* are *U_x,U_y,U_z* respectively
    - I believe *column 1* is the *y* coordinate
    - *column 2* probably *pressure*
    - *remainder columns* *turbulence properties*
    - Probably why the file is called ...p_U_turbProp
    - The Uref file also probably follows similar. So, U_ref mag would be = 46.59

plot3dToFoam -2D 1 -noBlanks
- Will convert my 2D plot3d grid to openfoam format

autoPatch 90
- Will automatically create patches on this converted grid, with feature angle 90 degs
- This will create a dir called 1 with its results
- You want to overwrite your constant/polyMesh with these files to use autoPatch's results

topoSet
- Needs a topoSetDict in system
- Creates the face and cell sets which will be used to create our new patches and subpatches
- Can check results and manually modify face sets if needed

createPatch // createPatch -overwrite
- Needs a createPatchDict in system
- Uses the face sets defined by topoSet to create new patches
- specifying -overwrite will directly edit your mesh in place

ToDo
- Link Turbo RANS to this and try optimizing
    - Try to optimize the medium refinement to match expt data and see how close
        you can get to the fine mesh results
- Further mesh refinement to see if any improvement produced
- Different turbulence models