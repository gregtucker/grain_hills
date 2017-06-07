#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""


Created on Wed Jun  7 08:13:39 2017

@author: gtucker
"""

import os
import sys
import plot_grain_hill


# Get the name of the directory containing run dirs
if len(sys.argv) < 2:
    dir_containing_run_dirs = os.getcwd()
else:
    dir_containing_run_dirs = sys.argv[1]

print('Looking for model output in subfolders of '
      + dir_containing_run_dirs)


# Sweep through the various folders
for item in os.listdir(dir_containing_run_dirs):
    
    # Get the full path name of the current item
    current_file_or_dir = os.path.join(dir_containing_run_dirs, item)
    
    # If it's a dir, look inside it
    if os.path.isdir(current_file_or_dir):

        for subitem in os.listdir(current_file_or_dir):
            
            # If it's an output file, read and plot to file
            if subitem == 'grain_hill_model0001.nc.grid':
                
                landlab_file = os.path.join(current_file_or_dir, subitem)
                plotfile = os.path.join(dir_containing_run_dirs,
                                        'final_hill_' + item + '.png')
                plot_grain_hill.run(infile_name=landlab_file,
                                    plot_file_name=plotfile)
