----
ToDo
- Link Turbo RANS to this and try optimizing
    - Try to optimize the medium refinement to match expt data and see how close
        you can get to the fine mesh results
- Different turbulence models
- [x] run other grid levels
    - [x] create plots
- [ ] Mesh adaption?
----

In x_by_h_01_p_U_turbulenceProperties:devReff.xy
    - *columns 3,4,5* are *U_x,U_y,U_z* respectively
    - I believe *column 1* is the *y* coordinate
    - *column 2* probably *pressure*
    - *remainder columns* *turbulence properties*
    - Probably why the file is called ...p_U_turbProp
    - The Uref file also probably follows similar. So, U_ref mag would be = 46.59

plot3dToFoam -2D 1 -noBlank backstep5_4levdn.p2dfmt
- Will convert my 2D plot3d grid to openfoam format

autoPatch 90 // autoPatch -overwrite 90
- Will automatically create patches on this converted grid, with feature angle 90 degs
- This will create a dir called 1 with its results
- You want to overwrite your constant/polyMesh with these files to use autoPatch's results
- Overwrite will edit in place

topoSet
- Needs a topoSetDict in system
- Creates the face and cell sets which will be used to create our new patches and subpatches
- Can check results and manually modify face sets if needed

createPatch // createPatch -overwrite
- Needs a createPatchDict in system
- Uses the face sets defined by topoSet to create new patches
- specifying -overwrite will directly edit your mesh in place

createPatch -dict system/patchMerge -overwrite
- Uses the patchMerge dict to merge lowerWall and the other subpatch

I've modified the Allrun script to do the above

postProcess -funcs '(magU sample)' -latestTime
- runs the sample dict in system for the latest time

The sample dict from the ori case file takes U_ref at -0.0508 0.0508 0.01, which is basically the midpoint of the
entry region. I can use somethime similar for the nasa grids

*#! Source of inaccuracy* - The "wall" B.C is supposed to start at x=-110 for the uppper and lower walls. I only used the first 2 cells,
so this could cause some issues with the boundary layer thickness, which would afffect the velocity at the step, and thereby
the solution. Should rectify this