#! /usr/bin/env python
"""Run the GrainHill model from command line with input file."""

import sys


if len(sys.argv) > 1:  # Check command-line argument

    from grainhill import BmiGrainHill

    print("Initializing...")
    gh = BmiGrainHill()
    gh.initialize(sys.argv[1])
    print("Running...")
    gh.update_until(gh._model.run_duration)
    print("Cleaning up...")
    gh.finalize()
    print("done.")
else:
    print('Usage: python run_grain_hill.py <input file>')
