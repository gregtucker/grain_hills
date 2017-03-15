#!/usr/env/python
"""
calc_elev_and_slope.py

Reads output from a series of GrainHill runs, and for each, calculates:
    1 - the maximum elevation
    2 - the mean elevation
    3 - the mean slope.
These are written to a csv file.
"""

import os
import sys
from landlab.io.native_landlab import load_grid
import numpy as np


DEFAULT_OUTPUT_NAME = 'grain_hill_results.csv'
DEFAULT_INPUT_NAME = 'grain_hill_model0001.nc.grid'
DEFAULT_INPUT_PATH = os.getcwd()


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


def get_input_and_output_names(argv):
    """Parses names for input path, input file name, and output file.
    
    Assumes that within the input path folder location there is a series of
    folders that start with 'G', each containing an output grid."""
    if len(argv) < 4:
        out_name = DEFAULT_OUTPUT_NAME
    else:
        out_name = argv[3]

    if len(argv) < 3:
        in_name = DEFAULT_INPUT_NAME
    else:
        in_name = argv[2]

    if len(argv) < 2:
        in_path = DEFAULT_INPUT_PATH
    else:
        in_name = argv[1]

    return in_path, in_name, out_name


def two_node_diff(a):
    """Calculate and return diffs over two nodes instead of one."""
    N = len(a)
    return a[2:] - a[:(N-2)]


def calc_mean_gradient(elev_profile):
    """Given elevation profile, calculates and returns mean gradient."""
    N = len(elev_profile)
    mean_grad_left = np.mean(two_node_diff(elev_profile[:((N+1)/2)])/1.73205)
    mean_grad_right = np.mean(-two_node_diff(elev_profile[((N+1)/2):])/1.73205)
    mean_grad = (mean_grad_left + mean_grad_right) / 2.0
    return mean_grad


def process_model_output_data(in_path, in_name):
    """Iterate through output files and process, returning list of results."""
    results_list = []
    
    for item in os.listdir(in_path):
    
        if item[0] == 'G':
    
            # Read the Landlab grid and pull out the node_state field
            g = load_grid(item + '/' + in_name)
            ns = g.at_node['node_state']
            
            # Get the elevation profile
            (elev, soil) = get_profile_and_soil_thickness(g, ns) 
            
            # Calculate mean and max elevation
            N = len(elev)
            hmax = np.amax(elev[2:N-2])
            hmean = np.average(elev[2:N-2])
            
            # Get mean gradient
            grad_mean = calc_mean_gradient(elev)
            
            run_number = item[17:]
            run_number = run_number[:run_number.find('-')]
            print(['run num ' + str(run_number) + ' ' + str(hmax)
                    + ' ' + str(hmean) + ' ' + str(grad_mean)])
            results_list.append((int(run_number), hmax, hmean, grad_mean))

    results_list.sort()
    return results_list


def write_output(results_list, out_name):
    """Write output to a file in csv format."""
    outfile = open(out_name, 'w')
    outfile.write('Run number,Max height,Mean height,Mean gradient\n')
    for item in results_list:
        outstr = (str(item[0]) + ',' + str(item[1]) + str(item[2]) + ',' 
                  + str(item[3]) + '\n')
        outfile.write(outstr)
    outfile.close()


def main():
    """Read, process, write, finish."""
    (in_path, in_name, out_name) = get_input_and_output_names(sys.argv)
    results_list = process_model_output_data(in_path, in_name)
    write_output(results_list, out_name)
    print('Processed ' + str(len(results_list)) + ' output files')


if __name__ == '__main__':
    main()