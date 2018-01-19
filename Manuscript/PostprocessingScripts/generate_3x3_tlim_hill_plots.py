#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:43:33 2017

@author: gtucker
"""

import plot_grain_hill

in_folders = ['Run101', 'Run103', 'Run105', 'Run111', 'Run113', 'Run115',
              'Run121', 'Run123', 'Run125']

master_in_path = ('/Users/gtucker/Documents/Papers/_InProgress/'
                  + 'GrainHill/ModelOutputData/RunOutput/ParamStudyRuns/')

master_out_path = ('/Users/gtucker/Documents/Papers/_InProgress/GrainHill/'
                   + 'grain_hills/Figures/RawMaterials/')

grid_filename = 'grain_hill_model0001.nc.grid'

plot_file_extension = '.jpg'

infiles = []
outfiles = []
for folder in in_folders:
    this_in_name = master_in_path + folder + '/' + grid_filename
    this_plot_name = master_out_path + folder.lower() + plot_file_extension
    print('')
    print('GENERATING PLOT FOR GRID: ' + folder)
    print('Reading from:')
    print(this_in_name)
    print('Writing to:')
    print(this_plot_name)
    plot_grain_hill.run(this_in_name, this_plot_name)
