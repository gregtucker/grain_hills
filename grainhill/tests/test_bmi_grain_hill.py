#! /usr/bin/env python

import os
import numpy
from numpy.testing import assert_equal, assert_allclose, assert_raises
from grainhill import BmiGrainHill


params_dict = {
    'grid_size': (6, 5),
    'run_duration': 4.0,
    'show_plots': False
}

params_for_file = \
"""number_of_node_rows: 5
number_of_node_columns: 5
report_interval: 1.0e8
run_duration: 1.0
output_interval: 1.0e99
settling_rate: 2.2e8
disturbance_rate: 1.0
weathering_rate: 1.0
dissolution_rate: 0.0
uplift_interval: 1.0
plot_interval: 1.0e99
friction_coef: 0.3
rock_state_for_uplift: 7
opt_rock_collapse: False
show_plots: True
opt_track_grains: False
"""


def test_bmi_initialize():
    model = BmiGrainHill()

    # Test with default parameters
    model.initialize()

    # Test with parameters in a file
    f = open('test_parameters.txt', 'w')
    f.write(params_for_file)
    f.close()
    model.initialize('test_parameters.txt')

    # Test with parameters in a dict (enhanced BMI)
    model.initialize(params_dict)
    os.remove('test_parameters.txt')

def test_bmi_run_and_finalize():
    model = BmiGrainHill()

    model.initialize(params_dict)
    assert_equal(model.get_current_time(), 0.0)
    model.update()
    assert_equal(model.get_current_time(), 1.0)
    model.update_frac(0.5)
    assert_equal(model.get_current_time(), 1.5)
    model.update_until(3.5)
    assert_equal(model.get_current_time(), 3.5)
    model.finalize()
    assert(model._model is None)

def test_other_bmi_funcs():
    model = BmiGrainHill()

    model.initialize(params_dict)
    assert_equal(model.get_var_type("node_state"), "int64")
    assert_equal(model.get_var_units("node_state"), "-")
    assert_equal(model.get_var_nbytes("node_state"), 240)
    assert_equal(model.get_var_itemsize("node_state"), 8)
    assert_equal(model.get_var_location("node_state"), "node")
    assert_equal(model.get_var_grid("node_state"), 0)
    assert_equal(model.get_grid_rank(0), 2)
    assert_equal(model.get_grid_size(0), 30)
    assert(type(model.get_value_ptr("node_state")) is numpy.ndarray)
    assert(type(model.get_value("node_state")) is numpy.ndarray)
    assert_equal(len(model.get_value_at_indices("node_state", [0, 1, 2])), 3)

    # Test set_value
    a = numpy.zeros(model.get_grid_size(0))
    a[:] = 7
    model.set_value("node_state", a)
    assert_equal(model.get_value_at_indices("node_state", [0]), 7)
    a = numpy.array([5, 6])
    model.set_value_at_indices("node_state", [0, 1], a)
    assert_equal(model.get_value_at_indices("node_state", [0]), 5)

    assert_equal(model.get_component_name(), "BmiGrainHill")
    assert_equal(model.get_input_item_count(), 1)
    assert_equal(model.get_output_item_count(), 1)
    assert_equal(model.get_input_var_names(), ("node_state", ))
    assert_equal(model.get_output_var_names(), ("node_state", ))
    assert_equal(model.get_grid_shape(0), [6, 5])
    assert_equal(model.get_grid_spacing(0), 1.0)
    assert_equal(model.get_grid_origin(0), [0., 0.])
    assert_equal(model.get_grid_type(0), "unstructured")
    assert_equal(model.get_start_time(), 0.0)
    assert_equal(model.get_end_time(), 4.0)
    assert_equal(model.get_time_step(), 1.0)
    assert_equal(model.get_time_units(), "y")

    # Grid geometry/topology functions
    numlinks = model.get_grid_edge_count(0)
    assert_equal(numlinks, 69)
    edge_nodes = numpy.zeros(2 * numlinks, dtype=numpy.int)
    model.get_grid_edge_nodes(0, edge_nodes)
    assert_equal(edge_nodes[:4], [0, 3, 3, 1])
    numnodes = model.get_grid_node_count(0)
    assert_equal(numnodes, 30)
    numcells = model.get_grid_face_count(0)
    assert_equal(numcells, 12)
    face_nodes = numpy.zeros(numcells, dtype=numpy.int)
    model.get_grid_nodes_per_face(0, face_nodes)
    assert_equal(face_nodes[:4], [6, 6, 6, 6])
    x = numpy.zeros(numnodes)
    model.get_grid_x(0, x)
    assert_allclose(x[:4], [0.0, 1.732, 3.464, 0.866], rtol=1.0e-3)
    y = numpy.zeros(numnodes)
    model.get_grid_y(0, y)
    assert_equal(y[:4], [0.0, 0.0, 0.0, 0.5])
    assert_raises(NotImplementedError, model.get_grid_face_nodes, 0, 0)
    assert_raises(NotImplementedError, model.get_grid_face_edges, 0, 0)
    assert_raises(NotImplementedError, model.get_grid_z, 0, 0)
