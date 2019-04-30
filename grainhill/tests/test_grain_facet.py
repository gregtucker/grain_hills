#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 08:24:48 2019

@author: gtucker
"""

import numpy as np
from grainhill import GrainFacetSimulator
from landlab import HexModelGrid
from numpy.testing import assert_equal


def test_initial_state_grid():
    """Test passing in an initial array of node states."""
    nr = 4
    nc = 3
    hg = HexModelGrid(shape=(nr, nc), node_layout='rect', orientation='vert')
    ins = hg.add_zeros('node', 'node_state', dtype=np.int)
    ins[hg.y_of_node < 2] = 8
    
    params = {
        'grid_size' : (nr, nc),
        'report_interval' : 5.0, 
        'output_interval' : 1.0e99, 
        'disturbance_rate' : 0.0,
        'weathering_rate' : 0.0,
        'dissolution_rate': 1.0,
        'run_duration': 3.0e3,
        'plot_interval': 1.0e99,
        'uplift_interval': 1.0e7,
        'friction_coef' : 1.0,
        'fault_x' : -0.001, 
        'cell_width' : 1.0,
        'grav_accel' : 9.8,
        'plot_file_name' : 'test_column_dissolution',
        'init_state_grid' : ins,
        'seed' : 0,
    }

    gfs = GrainFacetSimulator(**params)
    assert_equal(np.count_nonzero(gfs.ca.node_state), 6)

