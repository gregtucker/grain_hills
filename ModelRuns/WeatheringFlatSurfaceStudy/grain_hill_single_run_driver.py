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
import grain_hill_as_class
grain_hill_as_class = reload(grain_hill_as_class)
os.chdir(start_dir)


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
        if not grain_hill.ca.bnd_lnk[link]:
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

    print('plot_hill here')
    print(np.amax(grid.at_node['node_state']))
    print(np.amin(grid.at_node['node_state']))
    # Generate the plot
    #ax = grid.hexplot(grid.at_node['node_state'], color_map=my_cmap)
    #plt.axis('off')
    #ax.set_aspect('equal')

    # If applicable, save to file. Otherwise display the figure.
    # (Note: the latter option freezes execution until user dismisses window)
    if filename is not None:
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        print('Figure saved to ' + filename)
    else:
        print('hp here')
        grid.hexplot(grid.at_node['node_state'])
        plt.draw()

# Dictionary for parameters
params = {}

num_cols = 401
params['number_of_node_columns'] = num_cols
num_rows = 41 #int(np.round(0.866 * 1.3 * (num_cols - 1)))
#num_rows = 58
params['number_of_node_rows'] = num_rows
params['disturbance_rate'] = 0.01
params['uplift_interval'] = 1.0e10
params['weathering_rate'] = 0.01
params['run_duration'] = 4000.0
params['show_plots'] = False
params['plot_interval'] = 40.0
params['output_interval'] = 1.1 * params['run_duration']
params['report_interval'] = 20.0
params['settling_rate'] = 220000000.0
params['friction_coef'] = 1.0
params['rock_state_for_uplift'] = 8
params['opt_rock_collapse'] = 1.0
params['plot_every_transition'] = False

# Clunky but should work: create a fake grid, used only to make initial
# condition array
from landlab import HexModelGrid
grid = HexModelGrid(num_rows, num_cols, orientation='vert', shape='rect')
ns = np.zeros(grid.number_of_nodes, dtype=int)
bottom_half = np.where(grid.y_of_node < 0.5 * num_rows)[0]
ns[bottom_half] = 8
left_edge = np.where(grid.x_of_node == 0.0)[0]
ns[left_edge] = 8
right_edge = np.where(grid.x_of_node > 0.866 * num_cols - 1.0)[0]
ns[right_edge] = 8
grid = 0

params['initial_state_grid'] = ns

# instantiate a GrainHill model
grain_hill = grain_hill_as_class.GrainHill((num_rows, num_cols), **params)

grid = grain_hill.ca.grid
try:
    print(grid._hexplot_configured)
except:
    print('no hpc')

#run the model
n_iter = 1000
dt = params['run_duration'] / float(n_iter)
soil_thickness = np.zeros(n_iter + 1)
outfile = open('soil_vs_time.csv', 'w')
outfile.write('Time,Soil thickness')
outfile.write('0,0')
for i in range(n_iter):
    grain_hill.run_for(dt)

    # compute and write the results
    (elev_profile, soil) = grain_hill.get_profile_and_soil_thickness(grain_hill.grid, 
                                                             grain_hill.ca.node_state)
    #plot_hill(grain_hill.ca.grid)
    soil_thickness[i+1] = np.mean(soil)
    print('Soil thickness: ' + str(np.mean(soil)))
    outfile.write(str(dt * i) + ',' + str(soil_thickness[i+1]))

# Now run it again without pausing to check soil
#params['show_plots'] = True
#grain_hill = grain_hill_as_class.GrainHill((num_rows, num_cols), **params)
#grain_hill.run()

max_elev = np.amax(elev_profile)
N = len(elev_profile)
mean_grad_left = np.mean(two_node_diff(elev_profile[:((N+1)/2)])/1.73205)
mean_grad_right = np.mean(-two_node_diff(elev_profile[((N+1)/2):])/1.73205)
mean_grad = (mean_grad_left + mean_grad_right) / 2

frac_soil = calc_fractional_soil_cover(grain_hill)

plt.figure(2)
plt.plot(dt * np.arange(n_iter + 1), soil_thickness)
plt.show()

#myfile = open('results.out', 'w')
#myfile.write(str(max_elev) + ' ' + str(mean_grad) + ' ' + str(frac_soil)
#             + '\n')
#myfile.close()

# Make a plot to file
#plot_hill(grain_hill.grid, 'flat_surf_wxing.png')
