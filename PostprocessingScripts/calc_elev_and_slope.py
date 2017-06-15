#!/usr/env/python
"""
calc_elev_and_slope.py

Reads output from a series of GrainHill runs, and for each, calculates:
    1 - the maximum elevation
    2 - the mean elevation
    3 - the mean slope.
    4 - the mean soil thickness.
    5 - the fractional soil cover.
These are written to a csv file.
"""

import os
import sys
from landlab.io.native_landlab import load_grid
import numpy as np


DEFAULT_OUTPUT_NAME = 'grain_hill_results.csv'
DEFAULT_INPUT_NAME = 'grain_hill_model0001.nc.grid'
DEFAULT_INPUT_PATH = os.getcwd()


def calc_fractional_soil_cover(grid, node_state):
    """Calculate and return fractional soil versus rock cover."""
    num_soil_air_faces = 0.0
    num_rock_air_faces = 0.0
    
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
    return frac_soil, total_surf_faces, num_soil_air_faces, num_rock_air_faces


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
        in_path = argv[1]

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
            g = load_grid(in_path + '/' + item + '/' + in_name)
            ns = g.at_node['node_state']
            
            # Get the elevation profile
            (elev, soil) = get_profile_and_soil_thickness(g, ns) 
            
            # Calculate mean and max elevation
            N = len(elev)
            hmax = np.amax(elev[2:N-2])
            hmean = np.average(elev[2:N-2])
            
            # Get mean gradient
            grad_mean = calc_mean_gradient(elev)
            
            # Get the mean soil thickness and fractional soil cover
            soil_mean = np.mean(soil)
            (fs, nsurf, nsoil, nrock) = calc_fractional_soil_cover(g, ns)
            
            run_number = item[17:]
            run_number = run_number[:run_number.find('-')]
            print(['run num ' + str(run_number) + ' ' + str(hmax)
                    + ' ' + str(hmean) + ' ' + str(grad_mean) + ' '
                    + str(soil_mean) + ' ' + str(fs) + ' ' + str(nsurf)
                    + ' ' + str(nsoil) + ' ' + str(nrock)])
            results_list.append((int(run_number), hmax, hmean, grad_mean,
                                 soil_mean, fs, nsurf, nsoil, nrock))

    results_list.sort()
    return results_list


def write_output(results_list, out_name):
    """Write output to a file in csv format."""
    outfile = open(out_name, 'w')
    outfile.write('Run number,Max height,Mean height,Mean gradient,'
                  + 'Mean soil thickness,Fractional soil cover,'
                  + 'Total number of surface faces,'
                  + 'Number of soil-air faces,'
                  + 'Number of rock-air faces\n')
    for item in results_list:
        outstr = (str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + ',' 
                  + str(item[3]) + ',' + str(item[4]) + ',' + str(item[5])
                  + ',' + str(item[6]) + ',' + str(item[7])
                  + ',' + str(item[8]) + '\n')
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