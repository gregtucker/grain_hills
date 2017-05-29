# -*- coding: utf-8 -*-
"""
Created on Mon May 30th 22:21:07 2016

Simple driver for GrainHill model, based on example by Charlie Shobe for
his Brake model.

"""

import os
print('dakota_friendly_driver here. cwd = ' + os.getcwd())
import grain_hill_as_class
from landlab import load_params
import numpy as np
import sys

grain_hill_as_class = reload(grain_hill_as_class)

def two_node_diff(a):
    """Calculate and return diffs over two nodes instead of one."""
    N = len(a)
    return a[2:] - a[:(N-2)]

dx = 0.1  # assumed node spacing, m

#DAKOTA stuff: setting input files
input_file = 'inputs.txt' #DAKOTA creates this

#INPUT VARIABLES

# read parameter values from file 
params = load_params(input_file)

num_cols = params['number_of_node_columns']
num_rows = int(np.round(0.866 * 0.5 * (num_cols - 1)))
print('Launching run with ' + str(num_rows) + ' rows and ' + str(num_cols) + ' cols')
params['number_of_node_columns'] = num_cols
params['number_of_node_rows'] = num_rows
params['disturbance_rate'] = 10.0 ** params['disturbance_rate']
params['uplift_interval'] = 10.0 ** params['uplift_interval']
wprime = 10.0 ** params['weathering_rate']
params['weathering_rate'] = wprime / params['uplift_interval']

# Calculate run duration
#
# Time for the domain to rise by L/2, where L is # of node cols 
t1 = params['uplift_interval'] * num_cols
print('Time for domain rise:')
print(t1)
# Time to generate, on average, 10 * L disturbance events per column
t2 = 10 * num_cols / params['disturbance_rate']
print('Time for 10 L disturbances per column:')
print(t2)
# Take the minimum
tt = min(t1, t2)
# Time to have at least ten uplift events
t3 = 10 * params['uplift_interval']
# Take the max
params['run_duration'] = max(tt, t3)
if params['run_duration'] > 580000.0:
    print('WARNING: something is wrong')
    params['run_duration'] = 1.0
print('Run duration used:')
print(params['run_duration'])
params['plot_interval'] = 1.1 * params['run_duration']
params['output_interval'] = params['run_duration']

print('Running grainhill, params:')
print(params)
sys.stdout.flush()

# instantiate a GrainHill model
grain_hill = grain_hill_as_class.GrainHill((num_rows, num_cols), **params)

#run the model
grain_hill.run()

# compute an write the results
(elev_profile, soil) = grain_hill.get_profile_and_soil_thickness(grain_hill.grid, 
                                                         grain_hill.ca.node_state)
max_elev = np.amax(elev_profile)
N = len(elev_profile)
mean_grad_left = np.mean(two_node_diff(elev_profile[:((N+1)/2)])/1.73205)
mean_grad_right = np.mean(-two_node_diff(elev_profile[((N+1)/2):])/1.73205)
mean_grad = (mean_grad_left + mean_grad_right) / 2

myfile = open('results.out', 'w')
myfile.write(str(max_elev) + ' ' + str(mean_grad) + '\n')
myfile.close()

