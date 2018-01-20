# -*- coding: utf-8 -*-
"""
Simple driver for GrainHill model

"""

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

source_dir = '/Users/gtucker/Dev/MountainFrontModel/mountain_front_model'

start_dir = os.getcwd()
os.chdir(source_dir)
import grain_hill
grain_hill = reload(grain_hill)
os.chdir(start_dir)


def two_node_diff(a):
    """Calculate and return diffs over two nodes instead of one."""
    N = len(a)
    return a[2:] - a[:(N-2)]

def calc_fractional_soil_cover(gh):
    """Calculate and return fractional soil versus rock cover."""
    num_soil_air_faces = 0.0
    num_rock_air_faces = 0.0
    
    grid = gh.grid
    node_state = gh.ca.node_state
    
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

def plot_hill(grid, filename=None):
    """Generate a plot of the modeled hillslope."""

    # Set color map
    rock = '#5F594D'
    sed = '#A4874B'
    sky = '#D0E4F2'
    mob = '#D98859'
    clist = [sky, mob, mob, mob, mob, mob, mob, sed, rock]
    my_cmap = mpl.colors.ListedColormap(clist)

    # Generate the plot
    ax = grid.hexplot(grid.at_node['node_state'], color_map=my_cmap)
    #plt.axis('off')
    ax.set_aspect('equal')

    # If applicable, save to file. Otherwise display the figure.
    # (Note: the latter option freezes execution until user dismisses window)
    if filename is not None:
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        print('Figure saved to ' + filename)
    else:
        plt.show()

# Dictionary for parameters
params = {}

num_cols = 313
params['number_of_node_columns'] = num_cols
num_rows = 120
params['number_of_node_rows'] = num_rows
params['disturbance_rate'] = 0.000468
params['uplift_interval'] = 370.0
params['weathering_rate'] = 0.002
params['run_duration'] = 50000.0
params['uplift_duration'] = params['run_duration'] - 1.0
params['show_plots'] = True
params['plot_interval'] = 500.0
params['output_interval'] = 10000001.0
params['report_interval'] = 20.0
params['settling_rate'] = 7.0e7
params['friction_coef'] = 1.0
params['rock_state_for_uplift'] = 8
params['opt_rock_collapse'] = 1.0

# instantiate a GrainHill model
gh = grain_hill.GrainHill((num_rows, num_cols), **params)

# plot 

#run the model
gh.run()

# compute and write the results
(elev_profile, soil) = gh.get_profile_and_soil_thickness(gh.grid, 
                                                         gh.ca.node_state)
max_elev = np.amax(elev_profile)
N = len(elev_profile)
mean_grad_left = np.mean(two_node_diff(elev_profile[:((N+1)/2)])/1.73205)
mean_grad_right = np.mean(-two_node_diff(elev_profile[((N+1)/2):])/1.73205)
mean_grad = (mean_grad_left + mean_grad_right) / 2

frac_soil = calc_fractional_soil_cover(gh)

myfile = open('results.out', 'w')
myfile.write(str(max_elev) + ' ' + str(mean_grad) + ' ' + str(frac_soil)
             + '\n')
myfile.close()

plot_hill(gh.grid, 'grain_hill_yucaipa_d000468.png')
plot_hill(gh.grid, 'grain_hill_yucaipa_d000468.pdf')

