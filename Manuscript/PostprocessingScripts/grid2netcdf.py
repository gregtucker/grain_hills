#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
grid2netcdf.py: converts a native-Landlab format file to netcdf

Created on Thu Mar  2 07:41:29 2017

@author: gtucker
"""

import sys
from landlab.io.native_landlab import load_grid
from landlab.io.netcdf import write_netcdf


def get_output_file_name(infile_name):
    """Parse input file name to replace text after first dot with 'nc'"""
    split_str = infile_name.split('.')
    return split_str[0] + '.nc'


def main():
    """Executes model."""
    try:
        infile_name = sys.argv[1]
    except IndexError:
        print('Must include input file name on command line')
        sys.exit(1)

    print infile_name
    if len(infile_name) > 2 and infile_name[-3:] == '.nc':
        print('The file already has .nc extension')
        sys.exit(1)

    grid = load_grid(infile_name)
    outfile_name = get_output_file_name(infile_name)
    write_netcdf(outfile_name, grid)


if __name__ == '__main__':
    main()
