#!/usr/env/python
"""
read_results2.py

Reads results.out contents from a series of GrainHill run folders.
"""

import os
import sys
from landlab.io.native_landlab import load_grid
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


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
    plt.axis('off')
    ax.set_aspect('equal')

    # If applicable, save to file. Otherwise display the figure.
    # (Note: the latter option freezes execution until user dismisses window)
    if filename is not None:
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        print('Figure saved to ' + filename)
    else:
        plt.show()
        
        
def get_profile_and_soil_thickness(grid, data):
    """Calculate and return profiles of elevation and soil thickness.
    """
    nc = grid.number_of_node_columns
    elev = np.zeros(nc)
    soil = np.zeros(nc)
    for col in range(nc):
        states = data[grid.nodes[:, col]]  
        (rows_with_rock_or_sed, ) = np.where(states > 0)
        if len(rows_with_rock_or_sed) == 0:
            elev[col] = 0.0
        else:
            elev[col] = np.amax(rows_with_rock_or_sed) + 0.5 * (col % 2)
        soil[col] = np.count_nonzero(np.logical_and(states > 0, states < 8))

    return elev, soil

try:
    dir_name = sys.argv[1]
except IndexError:
    print('Must include input file name on command line')
    sys.exit(1)

results_list = []

print('Reading folder ' + dir_name)

for item in os.listdir(dir_name):

    if item[0] == 'G':

        g = load_grid(dir_name + item + '/grain_hill_model0001.nc.grid')
        ns = g.at_node['node_state']
        (elev, soil) = get_profile_and_soil_thickness(g, ns) 
        N = len(elev)
        hmean = np.average(elev[2:N-2])

        fname = dir_name + item + '/results.out'
        print(fname)
        rf = open(fname, 'r')
        line = rf.readline()
        print(line)
        rf.close()
        vals = line.split()
        hmax = vals[0]
        mean_slp = vals[1]

        run_number = item[17:]
        run_number = run_number[:run_number.find('-')]
        print('run num ' + run_number + ' ' + str(hmean) + ' ' + str(N)
              + ' ' + str(np.amax(elev)))

        results_list.append((int(run_number), hmax, hmean, mean_slp,
                             np.mean(soil)))

        plot_hill(g, 'run' + str(run_number) + '.png')

results_list.sort()

outfile = open('grain_hill_stats.csv', 'w')
outfile.write('Run num,max height,mean height,mean slope,mean soil thickness\n')
for item in results_list:
    outstr = str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + ',' + str(item[3]) + ',' + str(item[4]) + '\n'
    outfile.write(outstr)
outfile.close()

