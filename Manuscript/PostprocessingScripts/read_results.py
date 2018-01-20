#!/usr/env/python
"""
read_results.py

Reads results.out contents from a series of GrainHill run folders.
"""

import os

results_list = []

for item in os.listdir('/scratch/gtucker/GrainHill/'):

    if item[0] == 'G':

        fname = item + '/results.out'
        print(fname)
        rf = open(fname, 'r')
        line = rf.readline()
        print(line)
        rf.close()

	run_number = item[17:]
	run_number = run_number[:run_number.find('-')]
        print('run num ' + run_number)
        vals = line.split()
        results_list.append((int(run_number), vals[0], vals[1]))

results_list.sort()

outfile = open('grain_hill_results.csv', 'w')
outfile.write('Run num,max ht,mean slp\n')
for item in results_list:
    outstr = str(item[0]) + ',' + item[1] + ',' + item[2] + '\n'
    outfile.write(outstr)
outfile.close()

