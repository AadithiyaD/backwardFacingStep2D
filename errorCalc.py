import pandas as pd
import numpy as np
import os

# Reference data for non-dimensionalisation
Uref = 44.2 
H = 0.0127 

# TODO - 
#! Before this, polling func must move needed csv files to dataForOptLoop

def _rmse_(prediction, truth) -> np.float64:
    """Function implementing rmse formula

    Args:
        prediction (array): array of values from sim
        truth (array): array of values from experiment

    Returns:
        rmse value as a numpy.float64
    """
    return np.linalg.norm(prediction - truth) / np.sqrt(len(truth))

def calcRmse(trial_metadata: dict, x_by_h: int, w1: float = 1, w2: float = 0.5) -> np.float64:
    """Calc and return Root Mean Square error for specified x/H location, 
    with weighting applied to near wall and free stream / away from wall.
    y/H <= 1.2 is taken as near wall and y/H > 1.2 as free stream

    Args:
        x_by_h (int): x/H location
        w1 (float, optional): Weight for near wall error. Defaults to 1.
        w2 (float, optional): Weight for free stream error. Defaults to 0.5.

    Returns:
        float: total weighted rmse
    """

    # Path where csv files are located
    data_loc = trial_metadata['dataForOptLoop']
    
    # Shows mapping of x_by_H loc to driver data file
    sample_expt_map = {1:5,
           4:10,
           6:13,
           10:17}
    
    # Load experimental (ref) data
    expt_data = pd.read_csv(os.path.join(data_loc, f'R.ST0_station_{sample_expt_map[x_by_h]:02d}.csv'), skiprows=5)
    ux_ref = expt_data['U/Ur']
    uy_ref = expt_data['V/Ur']
    yh_ref = expt_data['Y/H']

    # Load respective sim (pred) data and non-dimensionalize it
    sim_data = pd.read_csv(os.path.join(data_loc, f'x_by_h_{x_by_h:02d}_U.csv'), header=0)
    ux_sim_all = sim_data['U_0'] / Uref
    uy_sim_all = sim_data['U_1'] / Uref
    yh_sim = sim_data['y'] / H
    
    # interpolate CFD data and sample experimental y/H on interpolated CFD data
    ux_sim_interp = np.interp(yh_ref, yh_sim, ux_sim_all)
    uy_sim_interp = np.interp(yh_ref, yh_sim, uy_sim_all)
    
    # Establish index limits of flow regions
    # near => near_wall
    near_idx = expt_data.index[expt_data['Y/H'] <= 1.2]
    free_stream_idx = expt_data.index[expt_data['Y/H'] > 1.2]
    
    # Calculate rmse sum for ux and uy
    near_rmse = _rmse_(ux_sim_interp[near_idx], ux_ref[near_idx]) + _rmse_(uy_sim_interp[near_idx], uy_ref[near_idx])
    free_str_rmse = _rmse_(ux_sim_interp[free_stream_idx], ux_ref[free_stream_idx]) + _rmse_(uy_sim_interp[free_stream_idx], uy_ref[free_stream_idx])
    
    # Add and return total remse for the specified sample x/H location
    tot_rmse = (w1 * near_rmse) + (w2 * free_str_rmse)
    return tot_rmse


if __name__ == "__main__":
    
    #! refactor to make use of trial_metadata
    print(type(calcRmse(x_by_h=1, trial_metadata=0)))