#! /usr/bin/env python
"""Run the GrainHill model from command line with input file."""

import sys

args = sys.argv

if len(args) > 1:  # Check for version argument
    for arg in args:
        if ('-v' in arg) or ('--version' in arg):
            from grainhill import VERSION
            print('Version ' + VERSION)
            args.pop(args.index(arg))
if len(args) > 1:  # Check other arguments (input file name)
    from grainhill import BmiGrainHill
    print("Initializing...")
    gh = BmiGrainHill()
    gh.initialize(args[1])
    print("Running...")
    gh.update_until(gh._model.run_duration)
    print("Cleaning up...")
    gh.finalize()
    print("done.")
else:
    print('Usage: python run_grain_hill.py <input file>')
