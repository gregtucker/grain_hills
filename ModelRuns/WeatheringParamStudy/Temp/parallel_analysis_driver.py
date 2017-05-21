# -*- coding: utf-8 -*-
"""
Created on Mon May 30th 22:21:07 2016

Simple analysis (not run) driver for GrainHill model.

Modified from script written originally by Charlie Shobe.
"""

import os
from subprocess import call

# Files and directories.
start_dir = os.path.dirname(os.path.realpath(__file__))
print start_dir
run_script = 'analyze_grain_hill_like_mark.sh'
module_name = 'grainhill' #folder that holds the model python module

copytree(os.path.join(start_dir, module_name), os.curdir)

# Call model through a PBS submission script. Note that `qsub`
# returns immediately, so jobs do not block.
job_name = 'GrainHillAnalysis-Dakota' + os.path.splitext(os.getcwd())[-1]
call(['qsub', '-N', job_name, os.path.join(start_dir, run_script)])

