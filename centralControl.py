"""Central configuration script. Make changes here, execute this file, and then run 
bayesOpt.py
"""

from ax.api.configs import RangeParameterConfig
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import os

# Ax experiment setup
MAX_TRIALS = 3
PARALLEL_RUNS = 3
FAILURE_TOLERANCE = 0.3 # 0.3 => exception raised if 30% of trials fail
TIME_BW_POLLS = 75

# Define parameters
A1_COEFF = RangeParameterConfig(name="a1", parameter_type="float", 
                            bounds=(0.248, 0.372))
BETASTAR = RangeParameterConfig(name="betaStar", parameter_type="float", 
                                bounds=(0.072, 0.108))

# x/H positions
X_BY_H=[1,4,6,10]

# Weightage for near wall rmse (w1) and free stream (w2)
WEIGHT1 = 1
WEIGHT2 = 0.5

# Max number of openFoam iterations
MAX_ITER = 100

# Number of processors for each run
NPROC = 6


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
controlDict.writeFile()
