grid level 0 is most refined, 4 is most coarse
im using grid level 1

I'll just look at the residuals from the log file at the end of the sim and determine convergence. For now, its too complicated to find an in loop soln.

It should be possible to do this with a codedFunctionObject, but i need to know more about openfoam's C++ style to understand and make that

02-01-26
--------
Idea for monitoring convergence -
- Sampled velocities get written out live (i.e for every writeStep)

I can either monitor these live with another python script to the side, and then send the kill signal,
Or, I can parse them at the end of 2000 iters to determine convergence

03-01-26
--------
make sure the main ~/.bashrc file sources the openfoam environment. Otherwise you will not be able to run pyFoam scripts in ax

06-01-26
--------
I have it running now, need to see why
- trial_0 exiting with floating point exception (FPE)
- why runs are being done sequentially even though i specified parallelism
-  [x] AttributeError: 'BasicRunner' object has no attribute 'isRunning'

the issue with FPE is grid specific. the coefficients work with the base openfoam mesh, but not the nasa one. I'll try a much  more
tighter bound and see if that makes a difference


TODO
----
- [] MAke a single entry point for setting up all configs for the opt 
- [] Add time taken for trial in metadata