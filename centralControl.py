from ax.api.configs import RangeParameterConfig
from ax.api.client import Client


max_trials = 50
parallel_runs = 3
failure_tolerance = 0.3 # 0.3 => exception raised if 30% of trials fail
time_bw_polls = 300

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