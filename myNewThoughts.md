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

07-01-26
--------
- [x] Generate the dammn certificate so that pyfoam doesnt pollute my console
- The trial runs have all worked
- [x] Need to store results to an external file
  - Need to find way to view the analysis graphs
- [x] Create central control script

09-01-2026
---------
- [] Add provision for attaching known datapoints to experiment
- [] Add foamToVTK call on completion of simpleFoam to trials
- [] sequential domain reduction?
- [] add other coefficients of kOmegaSST?

------
# Notes
------
```shell
INFO 01-07 07:50:44] Orchestrator: Waiting for completed trials (for 45 sec, currently running trials: 2).
[INFO 01-07 07:51:29] Orchestrator: Retrieved COMPLETED trials: 3 - 4.
[INFO 01-07 07:51:29] ax.core.metric: MetricFetchE INFO: Initialized MetricFetchE(message="Failed to fetch TOTAL_RMSE", exception=ErrorMetric.fetch() got an unexpected keyword argument 'trial_index')
with Traceback:
 Traceback (most recent call last):
  File "/home/durai/OpenFOAM/durai-v2506/run/dev-space/backwardFacingStep2D/.venv/lib/python3.10/site-packages/ax/api/protocols/utils.py", line 59, in fetch_trial_data
    progression, outcome = self.fetch(
TypeError: ErrorMetric.fetch() got an unexpected keyword argument 'trial_index'
```
The above error was because fetch() always needs to have trial_index and trial_metadata as args

- The trial metadata must use strings for paths, as the Path() from pathlib will cause issues.
  Therefore just to keep it uniform, i'll use strings for constructing my paths everywhere

- Note: ax will make the first poll at `time_bw_polls` sec into the opt. At this point, if the trials are still running
  ax then makes the next poll at `time_bw_polls * (1.5^n)` where n=> poll number. 
  - Ex: the first poll is done at 30s, the next at 30*1.5=45s, the next at 30 * (1.5 ^2) = 67s, and so on
  - Therefore it is very important to set the polling time to a reasonable value relative to the experiment (i.e sim)
    Because even if a set of parallel trials are done, ax will not move on until it has polled them and returned TrialStatus.COMPLETED
  - Once TrialStatus.COMPLETED is returned, it starts again at time_bw_polls for the next trial

- The Allrun scripts (i.e Allrun, Allrun_parallel, Allrun-w_pyFoam) are meant to execute the base backward 2D
  step using the grids from the NASA Turbulence modelling resource website
- runOpt.sh is meant for running the bayesian optimisation experiment


- put polymesh from NASA_Grids to under constant to use grid level 1
  - !!! In order to change to using blockmesh, i'll haave to change my 0 dir as well

- I haven't implemented the ability to store the state of the sim and restart from it. This requires aving to either an external sql data base or json file, using
  the built in methods of ax; which in turn would requre specifying encoding/decoding, and a different definition of the ErrorMetric(). This seems to be
  a sizeable endeavour, since the docs are pretty sparse, and the source code is not too inviting either

- !!! I tested the base openFOAM backward step case and i was able to get a better result. Looking at the residuals, its clear that the nasa grids still had to
be iterated for atleast another 1000 steps, and i don't really want to do that. For the learning purpose, i think i should stick with the base blockMesh tut case

- In order to change to using blockMesh, you'll need to change the 0 dir, system/sample, constant/polyMesh (remove this before doing blockMesh)

- Files/dirs needed for the opt framework - 

- To make plots from the pickle files 
```pyFoamRedoPlot.py PyFoamRunner.simpleFoam.analyzed/pickledPlots --pickle-file --picture-prefix=nasa_grid_```

- [x] Need to add be able to extract results from available dir in sample rather than fixed iter based dir

- _base_OF_ case step size = 0.0127