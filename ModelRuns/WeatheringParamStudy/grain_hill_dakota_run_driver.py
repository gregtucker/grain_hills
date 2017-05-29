#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analysis (run) driver for Grain Hill Dakota runs.
"""

import os
import shutil
import sys
from subprocess import call
from grain_hill_run_config import source_path #, output_path #, jobsub


# 1. Copy needed files to the right place. Specifically:
#
#    - Copy "inputs_template.txt" from the source directory to the "run.N"
#      directory for the current run (where "N" is the run number). This
#      "run.N" directory should be the current directory.
#
input_template = 'inputs_template.txt'
print('Copying ' + input_template + ' from ' + source_path + ' to '
      + os.getcwd())
shutil.copy(os.path.join(source_path, input_template), os.curdir)


# 2. Configure the input file: Use `dprepro` (from $DAKOTA_DIR/bin) to 
# substitute parameter values from Dakota into the input template, creating a
# new input file.
#    Here the arguments are:
#      - sys.argv[1] contains the name of Dakota's version of the input file,
#        which here will typically be called "params.in"
#      - inputs_template is the template input file for the grain hill model,
#        here "inputs_template.txt"
#      - input_file is the name of the resulting input file for this run, here
#        "inputs.txt". This is the grain-hill-format input file that has all
#        the default values from the template input file, plus the actual
#        (varying run-to-run) values from params.in for this particular run.
#
input_file = 'inputs.txt'
call(['dprepro', sys.argv[1], input_template, input_file])







#import sys
#import os
#import shutil
#from subprocess import call
#from grain_hill_run_config import program_path, output_path, jobsub
#
#print program_path
#print output_path
#print jobsub
#
#
#def copytree(src, dst, symlinks=False, ignore=None):
#    for item in os.listdir(src):
#        s = os.path.join(src, item)
#        d = os.path.join(dst, item)
#        if os.path.isdir(s):
#            shutil.copytree(s, d, symlinks, ignore)
#        else:
#            shutil.copy2(s, d)
#
## Files and directories.
#print os.getcwd()
#for arg in sys.argv:
#    print 'arg: ', arg
##start_dir = output_path
#start_dir = os.path.dirname(os.path.realpath(__file__))
#print start_dir
#input_file = 'inputs.txt'
#input_template = 'inputs_template.txt'
#run_script = 'run_grain_hill_like_mark.sh'
##module_name = 'grainhill' #folder that holds the model python module
#analysis_driver = 'dakota_analysis_driver.py'
#
## Use `dprepro` (from $DAKOTA_DIR/bin) to substitute parameter
## values from Dakota into the input template, creating a new
## input file.
#os.chdir(output_path)
#print os.curdir
#shutil.copy(os.path.join(program_path, input_template), os.curdir)
#call(['dprepro', sys.argv[1], input_template, input_file])
#
##copytree(os.path.join(start_dir, module_name), os.curdir)
##copytree(program_path, os.curdir)
#shutil.copy(os.path.join(program_path, run_script), os.curdir)
#
## copy analysis driver py script to active dir
## (gt commented this out; not sure why it's needed)
##shutil.copy(os.path.join(start_dir, analysis_driver), os.curdir)
#
## Call model through a PBS submission script. Note that `qsub`
## returns immediately, so jobs do not block.
#if jobsub == 'qsub':
#    job_name = 'GrainHill-Dakota' + os.path.splitext(os.getcwd())[-1]
#    call(['qsub', '-N', job_name, os.path.join(start_dir, run_script)])
#elif jobsub == None:
#    call(run_script)
#
## Provide a dummy results file to advance Dakota.
#with open(sys.argv[2], 'w') as fp:
#    fp.write('0.0\n1.0\n')
