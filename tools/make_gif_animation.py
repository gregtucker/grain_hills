#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Make a gif animation from a set of .png files.

Assumes the files have the same base name, followed by a number,
followed by .png. Designed to create movies from a sequence of
output images from the GrainHill model.

Created on Tue May 15 14:05:15 2018

@author: gtucker
"""

import imageio
import sys
import os


def main(basename):

    images = []

    for this_name in sorted(os.listdir('.')):
        print('appending ' + this_name)
        if this_name[-3:] == 'png':
            images.append(imageio.imread(this_name))
    imageio.mimsave(basename + '_movie.gif', images)


if __name__ == '__main__':

    try:
        basename = sys.argv[1]
    except:
        print('Usage: ' + sys.argv[0] + ' <folder/file name>')
        raise

    main(basename)
