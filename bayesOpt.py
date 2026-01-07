"""
Main optimisation script
"""
import numpy as np
import os
import re
import shutil
from subprocess import Popen, DEVNULL
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from ax.api.client import Client
from ax.api.configs import RangeParameterConfig
from ax.api.protocols.metric import IMetric
from ax.api.protocols.runner import IRunner, TrialStatus
from ax.api.types import TParameterization
from errorCalc import calcRmse

# ===================================================================================================
# TODO - Put all of these setupvariables in a central config / setup file

# Define opt config
max_iter = 10
parallel_runs = 3
failure_tolerance = 0.3 # 0.3 => exception raised if 30% of trials fail
time_bw_polls = 30

# Initialize ax client
client = Client()

# Define parameters
a1 = RangeParameterConfig(name="a1", parameter_type="float", bounds=(0.248, 0.372))
betaStar = RangeParameterConfig(name="betaStar", parameter_type="float", bounds=(0.072, 0.108))

# x/H positions
x_by_h=[1,4,6,10]

# Weightage for near wall rmse (w1) and free stream (w2)
w1 = 1
w2 = 0.5

# ===================================================================================================

# # Add data from any pre exisiting trials
# preexisting_trials = [
#     (
#         {"a1": 0.31, "betaStar": 0.09,},
#         {"FINAL_ERROR": 3.007},
#     )
# ]

# for parameters, data in preexisting_trials:
#     # Attach the parameterization to the Client as a trial and immediately complete it with the preexisting data
#     trial_index = client.attach_trial(parameters=[a1, betaStar])
#     client.complete_trial(trial_index=trial_index, raw_data=data)

class Runner(IRunner):
    def run_trial(self, trial_index, parameterization) -> dict[str, str]:
        """Sets up and executes an instance of simpleFoam for the case

        Args:
            trial_index (int): trial index
            parameterization (list): parameter values for current trial

        Returns:
            trial_metadata: dict of trial metadata containing location of case_dir,
            log_file and state_file
        """
    
        # Setup case dir
        case_dir = f"./cases/trial_{trial_index}"
        os.makedirs(case_dir, exist_ok=True)
        
        # Copy base files
        for folder in ['0', 'constant', 'system', 'dataForOptLoop']:
            shutil.copytree(f"./{folder}", 
                            f"{case_dir}/{folder}", dirs_exist_ok = True)
        
        # Modify turbulenceProperties with new coeffs
        turb_props = ParsedParameterFile(
            f'{case_dir}/constant/turbulenceProperties',
            treatBinaryAsASCII=True
        )
        coeffs = turb_props["RAS"]["kOmegaSSTCoeffs"]
        coeffs["a1"] = parameterization["a1"]
        coeffs["betaStar"] = parameterization["betaStar"]
        turb_props.writeFile()
    
        # Non-blocking execution of simpleFoam
        decompose = Popen(
            [f'decomposePar -case {case_dir}'],
            stdin = DEVNULL,
            stdout= DEVNULL,
            shell= True
            )
        
        # WAit for decompose to finish 
        decompose.wait()
        
        simpleFoam = Popen(
            [f'pyFoamRunner.py --procnr=6 simpleFoam -case {case_dir} '],
            stdin = DEVNULL,
            stdout= DEVNULL,
            shell= True
        )
        
        # Return metadata
        return {
            'case_dir': case_dir,
            'log_file': f'{case_dir}/PyFoamRunner.simpleFoam.logfile',
            'state_file': f'{case_dir}/PyFoamState.TheState',
            'dataForOptLoop': f'{case_dir}/dataForOptLoop',
            'postProcessing': f'{case_dir}/postProcessing'
        }
    #* No need to call reconstructPar since we only compare data from postProcessing dir
    
    def poll_trial(self, trial_index, trial_metadata) -> TrialStatus:
        """Checks the status of a trial

        Args:
            trial_index (int): index of current trial
            trial_metadata (dict): metadata dict of current trial

        Returns:
            TrialStatus: TrialStatus
        """

        # Check if its still running
        # Another way to check would be to use Popen return codes
        # But I think this is more descriptive
        with open(f"{trial_metadata['state_file']}", 'r') as f:
            content = f.read().splitlines()
            
            if content[0] =='Running':
                return TrialStatus.RUNNING
            
            # Finished - Ended => sim finished successfully
            elif content[0] == 'Finished - Ended':
                #  Question - How do you determine convergence of the sim
                #  Ans - I'm doing a VERY simple check here
                #  I want all sims to run for the 2000 iters. Since the sim is very quick on the baseline, I don't
                #  consider this to be a big issue. Next, If the first and last time steps do not exist, I consider
                #  that as a divergence and return a TrialStatus.FAILED (this status will include both sim crashes and divergences)
                #  Next, if any of the initial residulas from the last time step are > those of the first time step.
                #  I return a TrialStatus.FAILED
                

                with open(trial_metadata['log_file'], 'r') as f:
                    content = f.read().splitlines()
                
                # Extract relevant lines for first and last time steps
                # re.search pattern explanation - \b => line must start with Time and have one or more digits (i.e \d+)
                time_lines = [i for i, line in enumerate(content) if re.search(r"\bTime = \d+", line)]
                if time_lines:
                    first_time_idx = time_lines[0]
                    time_1_content = content[first_time_idx+2 : first_time_idx+9]
                    last_time_idx = time_lines[-1] 
                    time_end_content = content[last_time_idx+2 : last_time_idx+9]

                # If sim crashed and did not write any time steps
                if not time_1_content or not time_end_content:
                    return TrialStatus.FAILED
                
                # Pattern for extracting decimals
                # \d+ => start with one or more (i.e +) digits (i.e \d)
                # [.?] => match an optional (i.e ?) . (i.e [.])
                # \d* => end with zero or more (i.e *) digits
                # [e]?[-]?\d* => optionally match an e-{number} pattern 
                
                pattern = r"\d+[.]?\d*[e]?[-]?\d*"
                
                # Dict to store residuals
                residuals_1 = {} 
                residuals_2 = {}
                variables = ["Ux", "Uy", "p", "omega", "k"]

                # Extract residual values from content
                for line in time_1_content:
                    for var in variables:
                        if re.search(f"Solving for {var}", line):
                            residuals_1[var] = float(re.findall(pattern, line)[0])

                for line in time_end_content:
                    for var in variables:
                        if re.search(f"Solving for {var}", line):
                            residuals_2[var] = float(re.findall(pattern, line)[0])

                # Simple divergence check
                if any(residuals_2[var] > residuals_1[var] for var in variables):
                    return TrialStatus.FAILED
                
                else:
                    return TrialStatus.COMPLETED
                
                    # Move sample csv files to new dir for convenience
                    source_dir_path = f"{trial_metadata['postProcessing']}/sample/2000/"
                    dest_dir_path = f"{trial_metadata['dataForOptLoop']}"
                    
                    for file in x_by_h:
                        shutil.copy(src= source_dir_path / f'x_by_h_{file:02d}_U.csv',
                                    dst= dest_dir_path / f'x_by_h_{file:02d}_U.csv')
            
            else:
                # Note: If State == 'Finished' it means sim abruptly stopped
                print(f"State - {content}")
                return TrialStatus.FAILED

class ErrorMetric(IMetric):   
    """IMetric def for calculating RMSE. 
    
    Note - ax calls fetch only if trial status is completed
    """
    def fetch(self, trial_metadata: dict) :
        """Calculates rmse and returns dict of {self.name : (total_error, 0)}
        total_error = rmse(x/h) where x/h values are pre-specified in setup
        
        If exception encountered, returns None and ax will ignore the sepcific
        iteration / trialS
        """
        
        try:
            total_error = 0
            for x_pos in x_by_h:
                total_error += calcRmse(trial_metadata=trial_metadata,
                                        x_by_h=x_pos)
            
            return (0, total_error)
        
        except Exception as e:
            print(f"Encountered error {e}")
            return None


client.configure_experiment(
    parameters=[a1, betaStar],
    name="2D Turbulence model Calibration",
    description="k-omega SST Calibration against 2D backward facing step using Driver and Seegmiller dataset",
    owner="me"
)

runner = Runner()
error_metric = ErrorMetric(name="TOTAL_RMSE") 

client.configure_optimization(objective="-TOTAL_RMSE")

client.configure_runner(runner=runner)
client.configure_metrics(metrics=[error_metric])

client.run_trials(
    max_trials=max_iter,
    parallelism=parallel_runs,
    tolerated_trial_failure_rate=failure_tolerance,
    initial_seconds_between_polls=time_bw_polls
)

