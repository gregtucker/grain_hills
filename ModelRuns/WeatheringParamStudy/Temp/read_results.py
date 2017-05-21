#!/usr/env/python
"""
read_results.py

Reads results.out contents from a series of GrainHill run folders.
"""

for dir in range(1, 126):
    fname = ['GrainHill-Dakota.' + str(dir) + '-*/results.out']
    print(fname)
    rf = open(fname, 'r')
    for line in rf:
        print(line)
    rf.close()
