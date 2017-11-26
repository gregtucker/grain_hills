
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
plot_grain_hill.py: read and plot node state from a grain hill run.

Created on Thu Mar  2 08:13:51 2017

@author: gtucker
"""

import sys
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
        
        
def run(infile_name, plot_file_name=None):
    """
    Read grid, generate plot.
    """
    # Read in the model run
    grid = load_grid(infile_name)

    # Create the plot
    plot_hill(grid, plot_file_name)


def main():
    """Executes model."""
    try:
        infile_name = sys.argv[1]
    except IndexError:
        print('Must include input file name on command line')
        sys.exit(1)

    # Parse third arg, which is name of file to save. File format depends on
    # the extension, e.g. "foo.pdf" will generate a pdf file.
    if len(sys.argv) > 2:
        plot_file_name = sys.argv[2]
    else:
        plot_file_name = None

    run(infile_name, plot_file_name)

if __name__ == '__main__':
    main()


