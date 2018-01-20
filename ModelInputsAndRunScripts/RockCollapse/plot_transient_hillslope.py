#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 08:25:13 2017

@author: gtucker
"""

from landlab.io.native_landlab import load_grid
import matplotlib as mpl
import matplotlib.pyplot as plt


def plot_hill(grid, filename=None):
    """Generate a plot of the modeled hillslope."""

    # Set color map
    rock = '#5F594D'
    sed = '#A4874B'
    sky = '#D0E4F2'
    mob = '#D98859'
    clist = [sky, mob, mob, mob, mob, mob, mob, sed, rock]
    my_cmap = mpl.colors.ListedColormap(clist)

    # Generate the plot
    ax = grid.hexplot(grid.at_node['node_state'], color_map=my_cmap)
    plt.axis('off')
    ax.set_aspect('equal')

    # If applicable, save to file. Otherwise display the figure.
    # (Note: the latter option freezes execution until user dismisses window)
    if filename is not None:
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        print('Figure saved to ' + filename)
    else:
        plt.show()



for i in range(1, 21):
    
    fname = 'grain_hill_model' + str(i).zfill(4) + '.nc.grid'
    grid = load_grid(fname)
    plot_hill(grid, filename='transient_hill' + str(i).zfill(4) + '.png')
