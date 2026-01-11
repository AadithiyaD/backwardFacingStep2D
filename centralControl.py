"""Central configuration script. Make changes here, execute this file, and then run 
bayesOpt.py
"""

from ax.api.configs import RangeParameterConfig
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import os

# Ax experiment setup
MAX_TRIALS = 10
PARALLEL_RUNS = 3
FAILURE_TOLERANCE = 0.3 # 0.3 => exception raised if 30% of trials fail
TIME_BW_POLLS = 1000 # In seconds

# Max number of simpleFoam iterations
MAX_ITER = 5000

# Number of intervals to wait before writing out data
write_control = 500

# Number of processors for each run
NPROC = 6

# Define parameters
A1_COEFF = RangeParameterConfig(name="a1", parameter_type="float", 
                            bounds=(0.155, 0.465))
BETASTAR = RangeParameterConfig(name="betaStar", parameter_type="float", 
                                bounds=(0.045, 0.135))

# x/H positions
X_BY_H=[1,4,6,10]

# Weightage for near wall rmse (weight1) and free stream (weight2)
WEIGHT1 = 1.5
WEIGHT2 = 0.5

# ===============================================================================
# Dict modification
decomposeParDict = ParsedParameterFile(
        os.path.join('system', 'decomposeParDict'),
        treatBinaryAsASCII=True
)
decomposeParDict['numberOfSubdomains'] = NPROC
decomposeParDict.writeFile()

controlDict = ParsedParameterFile(
            os.path.join('system', 'controlDict'),
            treatBinaryAsASCII=True
        )

controlDict['endTime'] = MAX_ITER
controlDict['writeInterval'] = write_control
controlDict.writeFile()
