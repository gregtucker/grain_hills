#! /usr/bin/env python

from grainhill import BmiGrainHill

params_dict = {
    'grid_size': (5, 5)
}


def test_bmi_initialize():
    model = BmiGrainHill()

    # Test with default parameters
    model.initialize()

    # Test with parameters in a file
    model.initialize('test_parameters.txt')

    # Test with parameters in a dict (enhanced BMI)
    model.initialize(params_dict)
