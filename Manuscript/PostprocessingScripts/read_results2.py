#!/usr/env/python
"""
read_results2.py

Reads results.out contents from a series of GrainHill run folders.
"""

import os
from landlab.io.native_landlab import load_grid
import numpy as np

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

results_list = []

for item in os.listdir('/scratch/gtucker/GrainHill/'):

    if item[0] == 'G':

	g = load_grid(item + '/grain_hill_model0001.nc.grid')
	ns = g.at_node['node_state']
	(elev, soil) = get_profile_and_soil_thickness(g, ns) 
	N = len(elev)
	hmean = np.average(elev[2:N-2])

	run_number = item[17:]
	run_number = run_number[:run_number.find('-')]
        print('run num ' + run_number + ' ' + str(hmean) + ' ' + str(N) + ' ' + str(np.amax(elev)))
        results_list.append((int(run_number), hmean))

results_list.sort()

outfile = open('grain_hill_mean_height.csv', 'w')
outfile.write('Run num,mean height\n')
for item in results_list:
    outstr = str(item[0]) + ',' + str(item[1]) + '\n'
    outfile.write(outstr)
outfile.close()

