# -*- coding: utf-8 -*-
"""
Created on Mon May 30th 22:21:07 2016

Simple driver for GrainHill model.

Modified from script written originally by Charlie Shobe.
"""

import sys
import os
import shutil
from subprocess import call

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

# Files and directories.
start_dir = os.path.dirname(os.path.realpath(__file__))
print start_dir
input_file = 'inputs.txt'
input_template = 'inputs_template.txt'
run_script = 'run_grain_hill_like_mark.sh'
module_name = 'grainhill' #folder that holds the model python module
analysis_driver = 'dakota_analysis_driver.py'

# Use `dprepro` (from $DAKOTA_DIR/bin) to substitute parameter
# values from Dakota into the input template, creating a new
# input file.
# print os.curdir
shutil.copy(os.path.join(start_dir, input_template), os.curdir)
call(['dprepro', sys.argv[1], input_template, input_file])

copytree(os.path.join(start_dir, module_name), os.curdir)

# copy analysis driver py script to active dir
# (gt commented this out; not sure why it's needed)
#shutil.copy(os.path.join(start_dir, analysis_driver), os.curdir)

# Call model through a PBS submission script. Note that `qsub`
# returns immediately, so jobs do not block.
job_name = 'GrainHill-Dakota' + os.path.splitext(os.getcwd())[-1]
call(['qsub', '-N', job_name, os.path.join(start_dir, run_script)])

# Provide a dummy results file to advance Dakota.
with open(sys.argv[2], 'w') as fp:
    fp.write('0.0\n1.0\n')
