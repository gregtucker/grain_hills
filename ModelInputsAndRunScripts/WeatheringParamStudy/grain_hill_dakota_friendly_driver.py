# -*- coding: utf-8 -*-
"""
Created on Mon May 30th 22:21:07 2016

Simple driver for GrainHill model, based on example by Charlie Shobe for
his Brake model.

"""

import os
print('grain_hill_dakota_friendly_driver here. cwd = ' + os.getcwd())
import grain_hill_as_class
from landlab import load_params
import numpy as np
import sys

grain_hill_as_class = reload(grain_hill_as_class)

def two_node_diff(a):
    """Calculate and return diffs over two nodes instead of one."""
    N = len(a)
    return a[2:] - a[:(N-2)]

def calc_fractional_soil_cover(grain_hill):
    """Calculate and return fractional soil versus rock cover."""
    num_soil_air_faces = 0.0
    num_rock_air_faces = 0.0
    
    grid = grain_hill.grid
    node_state = grain_hill.ca.node_state
    
    for link in range(grid.number_of_links):
        tail = grid.node_at_link_tail[link]
        head = grid.node_at_link_head[link]
        if node_state[tail] == 0:  # if tail is air, see if head is rock/sed
            if node_state[head] == 7:
                num_soil_air_faces += 1
            elif node_state[head] == 8:
                num_rock_air_faces += 1
        elif node_state[head] == 0:  # if head is air, see if tail is rock/sed
            if node_state[tail] == 7:
                num_soil_air_faces += 1
            elif node_state[tail] == 8:
                num_rock_air_faces += 1

    total_surf_faces = num_soil_air_faces + num_rock_air_faces
    frac_rock = num_rock_air_faces / total_surf_faces
    frac_soil = num_soil_air_faces / total_surf_faces
    print('Total number of surface faces: ' + str(total_surf_faces))
    print('Number of soil-air faces: ' + str(num_soil_air_faces))
    print('Number of rock-air faces: ' + str(num_rock_air_faces))
    print('Percent rock-air faces: ' + str(100.0 * frac_rock))
    print('Percent soil-air faces: ' + str(100.0 * frac_soil))
    return frac_soil

dx = 0.1  # assumed node spacing, m

#DAKOTA stuff: setting input files
input_file = 'inputs.txt' #DAKOTA creates this

#INPUT VARIABLES

# read parameter values from file 
params = load_params(input_file)

num_cols = params['number_of_node_columns']
num_rows = int(np.round(0.866 * 1.0 * (num_cols - 1)))
print('Launching run with ' + str(num_rows) + ' rows and ' + str(num_cols) + ' cols')
params['number_of_node_columns'] = num_cols
params['number_of_node_rows'] = num_rows
params['disturbance_rate'] = 10.0 ** params['disturbance_rate']
params['uplift_interval'] = 10.0 ** params['uplift_interval']
wprime = 0.4 * (10.0 ** params['weathering_rate'])
params['weathering_rate'] = wprime / params['uplift_interval']

# Calculate run duration
#
# Time for the domain to rise by L, where L is # of node cols 
t1 = params['uplift_interval'] * num_cols
print('Time for domain rise:')
print(t1)
# Time to generate, on average, 10 * L disturbance events per column
t2 = 10 * num_cols / params['disturbance_rate']
print('Time for 0.1 (10) L disturbances per column:')
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

# compute and write the results
(elev_profile, soil) = grain_hill.get_profile_and_soil_thickness(grain_hill.grid, 
                                                         grain_hill.ca.node_state)
max_elev = np.amax(elev_profile)
N = len(elev_profile)
mean_grad_left = np.mean(two_node_diff(elev_profile[:((N+1)/2)])/1.73205)
mean_grad_right = np.mean(-two_node_diff(elev_profile[((N+1)/2):])/1.73205)
mean_grad = (mean_grad_left + mean_grad_right) / 2

frac_soil = calc_fractional_soil_cover(grain_hill)

myfile = open('results.out', 'w')
myfile.write(str(max_elev) + ' ' + str(mean_grad) + ' ' + str(frac_soil)
             + '\n')
myfile.close()

# Make a plot to file
import matplotlib.pyplot as plt
grain_hill.grid.hexplot('node_state')
plt.savefig('final_hill.png')

