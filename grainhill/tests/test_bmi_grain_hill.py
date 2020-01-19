#! /usr/bin/env python

from grainhill import BmiGrainHill
from numpy.testing import assert_equal


params_dict = {
    'grid_size': (5, 5),
    'run_duration': 4.0
}


def test_bmi_initialize():
    model = BmiGrainHill()

    # Test with default parameters
    model.initialize()

    # Test with parameters in a file
    model.initialize('test_parameters.txt')

    # Test with parameters in a dict (enhanced BMI)
    model.initialize(params_dict)

def test_bmi_run_and_finalize():
    model = BmiGrainHill()

    model.initialize('test_parameters.txt')
    assert_equal(model.get_current_time(), 0.0)
    model.update()
    assert_equal(model.get_current_time(), 1.0)
    model.update_frac(0.5)
    assert_equal(model.get_current_time(), 1.5)
    model.update_until(3.5)
    assert_equal(model.get_current_time(), 3.5)
    model.finalize()
    assert(model._model is None)
