#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
grain_hill_run_config.py: system configuration file for Grain Hill model runs.
Modify this to match the system on which you run.

Created on Fri May 19 07:42:35 2017

@author: gtucker
"""

# This is the directory containing the source-code files for the grain hill
# model (grain_hill_as_class.py, cts_model.py, lattice_grain.py)
source_path = '/Users/gtucker/Dev/MountainFrontModel/mountain_front_model'

# This is the directory containing the inputs template file
# "inputs_template.txt"
input_path = '/Users/gtucker/Documents/Papers/_InProgress/GrainHill/grain_hills/ModelRuns/WeatheringParamStudy'

# This is the directory from which Dakota should run
output_path = '/Users/gtucker/Runs/GrainHill/WeatheringParamStudy'

# This is the name of the shell script that gets called to launch each run
run_script = 'run_grain_hill_beach.sh'

# For beach only: home directory
home_path = '/Users/gtucker'

# For beach only: scratch directory
scratch_path = '/Users/gtucker/Runs/Scratch'

# For beach only: working directory
work_path = output_path

# For a "local" computer (e.g., my laptop), make jobsub = None. For Beach,
# set it to 'qsub'.
jobsub = 'qsub'

